from fastapi import HTTPException
import datetime

async def search_bookings(query: str, db):
    try:
        with db.cursor() as cursor:
            # Search by Customer Name, Transaction ID, or Phone Number
            # We join Transaction with Customer to get customer details
            # We also want to know the room details, but a transaction might have multiple rooms.
            # For simplicity, let's first find the transactions.
            
            sql = """
                SELECT 
                    t.TransactionID,
                    c.FullName as CustomerName,
                    c.PhoneNumber,
                    t.CheckIn,
                    t.CheckOut,
                    t.Status as BookingStatus,
                    GROUP_CONCAT(r.RoomNumber SEPARATOR ', ') as RoomNumbers,
                    GROUP_CONCAT(s.Name SEPARATOR ', ') as RoomStatuses
                FROM `Transaction` t
                JOIN Customer c ON t.CustomerID = c.CustomerID
                LEFT JOIN TransactionRoom tr ON t.TransactionID = tr.TransactionID
                LEFT JOIN Room r ON tr.RoomID = r.RoomID
                LEFT JOIN Status s ON r.StatusID = s.StatusID
            """
            
            params = []
            if query:
                sql += """
                WHERE 
                    (c.FullName LIKE %s OR 
                     CAST(t.TransactionID AS CHAR) LIKE %s OR 
                     c.PhoneNumber LIKE %s)
                """
                name_pattern = f"%{query}%"
                id_phone_pattern = f"{query}%"
                params = [name_pattern, id_phone_pattern, id_phone_pattern]
            
            sql += """
                GROUP BY t.TransactionID, c.FullName, c.PhoneNumber, t.CheckIn, t.CheckOut, t.Status
                ORDER BY t.CheckIn DESC
            """
            
            cursor.execute(sql, tuple(params))
            bookings = cursor.fetchall()
            return bookings
    except Exception as e:
        print(f"Error searching bookings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")

async def check_in(transaction_id: int, db):
    try:
        with db.cursor() as cursor:
            # 1. Verify transaction exists
            cursor.execute("SELECT Status FROM `Transaction` WHERE TransactionID = %s", (transaction_id,))
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Booking not found")
            
            current_status = result['Status']
            # Allow Check-in if Booked, Confirmed, Paid
            allowed_statuses = ['Booked', 'Confirmed', 'Paid']
            if current_status not in allowed_statuses:
                 # If already Occupied, maybe we shouldn't error if user clicks check-in again? 
                 # But UI should handle button. API should probably be strict or idempotent.
                 if current_status == 'Occupied':
                     raise HTTPException(status_code=400, detail="Booking is already checked in")
                 
                 # If status is Unpaid or Cancelled or anything else not allowed
                 raise HTTPException(status_code=400, detail=f"Cannot check-in. Current status is '{current_status}' (Must be Paid/Booked/Confirmed)")

            # Check Room Statuses
            cursor.execute("""
                SELECT s.Name as StatusName
                FROM TransactionRoom tr
                JOIN Room r ON tr.RoomID = r.RoomID
                JOIN Status s ON r.StatusID = s.StatusID
                WHERE tr.TransactionID = %s
            """, (transaction_id,))
            room_statuses = cursor.fetchall()
            
            for rs in room_statuses:
                if rs['StatusName'] == 'Maintenance':
                    raise HTTPException(status_code=400, detail="Cannot check-in.")

            # 2. Update Transaction Status to 'Occupied'
            cursor.execute("UPDATE `Transaction` SET Status = 'Occupied' WHERE TransactionID = %s", (transaction_id,))
            
            # 3. Update Room Status to 'Occupied' for all rooms in this transaction
            # First get the 'Occupied' StatusID
            cursor.execute("SELECT StatusID FROM Status WHERE Name = 'Occupied' AND Type = 'Room'")
            status_result = cursor.fetchone()
            if not status_result:
                 raise HTTPException(status_code=500, detail="Status 'Occupied' not found in database")
            occupied_status_id = status_result['StatusID']

            # Get rooms associated with this transaction
            cursor.execute("SELECT RoomID FROM TransactionRoom WHERE TransactionID = %s", (transaction_id,))
            rooms = cursor.fetchall()
            
            for room in rooms:
                cursor.execute("UPDATE Room SET StatusID = %s WHERE RoomID = %s", (occupied_status_id, room['RoomID']))
            
            db.commit()
            return {"message": "Check-in successful", "transaction_id": transaction_id}
            
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        print(f"Error checking in: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")

async def check_out(transaction_id: int, db):
    try:
        with db.cursor() as cursor:
            # 1. Verify transaction exists and is 'Occupied'
            cursor.execute("SELECT Status FROM `Transaction` WHERE TransactionID = %s", (transaction_id,))
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Booking not found")
            
            current_status = result['Status']
            if current_status != 'Occupied':
                raise HTTPException(status_code=400, detail="Booking is not currently occupied (cannot check-out)")

            # 2. Update Transaction Status to 'Maintenance' (User request)
            cursor.execute("UPDATE `Transaction` SET Status = 'Maintenance' WHERE TransactionID = %s", (transaction_id,))
            
            # 3. Update Room Status to 'Need Clean'
            # Get 'Need Clean' StatusID
            cursor.execute("SELECT StatusID FROM Status WHERE Name = 'Need Clean' AND Type = 'Room'")
            status_result = cursor.fetchone()
            if not status_result:
                 raise HTTPException(status_code=500, detail="Status 'Need Clean' not found in database")
            need_clean_status_id = status_result['StatusID']

            # Get rooms associated with this transaction
            cursor.execute("SELECT RoomID FROM TransactionRoom WHERE TransactionID = %s", (transaction_id,))
            rooms = cursor.fetchall()
            
            for room in rooms:
                cursor.execute("UPDATE Room SET StatusID = %s WHERE RoomID = %s", (need_clean_status_id, room['RoomID']))
            
            db.commit()
            return {"message": "Check-out successful (Status set to Maintenance, Room set to Need Clean)", "transaction_id": transaction_id}

    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        print(f"Error checking out: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")
