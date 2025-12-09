from fastapi import APIRouter, Depends, HTTPException
from models import RoomsBooking,RoomBookingAdd
from services.rooms_service import get_rooms_available
import datetime
from db_connection import get_db
from services.auth_service import get_current_customer_id

booking_router = APIRouter(prefix="/booking", tags=["Booking"])

@booking_router.post("")
async def create_booking(request: RoomsBooking, db=Depends(get_db)):
    try:
        with db.cursor() as cursor:
            checkin = datetime.datetime.strptime(request.CheckIn, "%Y-%m-%d").date()
            checkout = datetime.datetime.strptime(request.CheckOut, "%Y-%m-%d").date()

            if checkout <= checkin:
                raise HTTPException(status_code=400, detail="Invalid date")

            num_nights = (checkout - checkin).days
            total_price_all = 0

            # Check existing transactions
            cursor.execute("""
            SELECT t.TransactionID, t.Status 
            FROM `Transaction` t
            WHERE t.CustomerID = %s 
            AND t.CheckIn = %s 
            AND t.CheckOut = %s
            AND t.PaidAt IS NULL
            """, (request.CustomerID, request.CheckIn, request.CheckOut))

            existing_transactions = cursor.fetchall()
            matched_transaction_id = None

            if existing_transactions:
                for et in existing_transactions:
                    if et["Status"] in ["Pending"]:
                        matched_transaction_id = et["TransactionID"]
                        break
            if matched_transaction_id:
                raise HTTPException(status_code=400, detail="Booking already exists for the given dates")


            # Create 1 transaction
            created_transaction_id = None
            cursor.execute("""
                INSERT INTO `Transaction` (CustomerID, CheckIn, CheckOut, Status)
                VALUES (%s, %s, %s, %s)
            """, (request.CustomerID, request.CheckIn, request.CheckOut, "Pending"))
            cursor.execute("SELECT LAST_INSERT_ID() as last_id")
            last_id_row = cursor.fetchone()
            created_transaction_id = last_id_row["last_id"] if last_id_row else 0


            db.commit()

            return {
                "message": "Booking created successfully",
                "total_price": total_price_all,
                "transaction_id": created_transaction_id,
                "checkin": request.CheckIn,
                "checkout": request.CheckOut,
                "status": "Pending"
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@booking_router.post("/add/")
async def add_rooms_to_booking(request: RoomBookingAdd, db=Depends(get_db)):
    try:
        with db.cursor() as cursor:
            transaction_id = request.TransactionID

            # Check Transaction exists
            cursor.execute("SELECT * FROM `Transaction` WHERE TransactionID=%s", (transaction_id,))
            transaction = cursor.fetchone()
            if transaction["Status"] not in ["Pending"]:
                raise HTTPException(status_code=400, detail="Cannot add rooms to this booking status")
            if not transaction:
                raise HTTPException(status_code=404, detail="Transaction not found")

            checkin = transaction["CheckIn"]
            checkout = transaction["CheckOut"]

            # Add rooms
            for room_req in request.RoomRequests:

                cursor.execute("""
                    SELECT r.RoomID
                    FROM Room r
                    WHERE r.RoomTypeID = %s
                    AND r.RoomID NOT IN (
                        SELECT tr.RoomID
                        FROM TransactionRoom tr
                        JOIN `Transaction` t ON tr.TransactionID = t.TransactionID
                        WHERE t.Status IN ('Paid', 'Pending')
                        AND (
                            t.CheckIn < %s AND t.CheckOut > %s
                        )
                    )
                    LIMIT %s
                """, (room_req.RoomTypeID, checkout, checkin, room_req.Quantity))

                available_rooms = cursor.fetchall()

                if len(available_rooms) < room_req.Quantity:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Not enough rooms available for RoomType {room_req.RoomTypeID}"
                    )

                # Insert available rooms
                for room in available_rooms:
                    cursor.execute("""
                        INSERT INTO TransactionRoom (TransactionID, RoomID)
                        VALUES (%s, %s)
                    """, (transaction_id, room["RoomID"]))

            db.commit()

            await update_booking_total_price(transaction_id, db)

            return {"message": "Rooms added to booking successfully", "TransactionID": transaction_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@booking_router.get("/booking-history")
def get_booking_history(
    customer_id: int = Depends(get_current_customer_id),
    db=Depends(get_db)
):
    try:
        with db.cursor() as cursor:
            sql = """
                SELECT 
                    t.TransactionID AS id,
                    c.FullName AS guestName,
                    c.PhoneNumber AS phone,
                    r.RoomID AS RoomID,
                    r.RoomNumber AS roomNumber,
                    rt.Name AS roomType,
                    t.Status AS status,
                    t.CreateAt AS bookingDate
                FROM `Transaction` t
                JOIN Customer c ON t.CustomerID = c.CustomerID
                JOIN TransactionRoom tr ON t.TransactionID = tr.TransactionID
                JOIN Room r ON tr.RoomID = r.RoomID
                JOIN RoomType rt ON r.RoomTypeID = rt.RoomTypeID
                WHERE t.CustomerID = %s
                AND t.Status = 'Paid'
                ORDER BY t.CreateAt DESC
            """
            cursor.execute(sql, (customer_id,))
            bookings = cursor.fetchall()
            return bookings

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")


