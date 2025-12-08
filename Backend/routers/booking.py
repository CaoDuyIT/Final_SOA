from fastapi import APIRouter, Depends, HTTPException
from models import RoomsBooking
from rooms_service import get_rooms_available
import datetime
from db_connection import get_db

booking_router = APIRouter(prefix="/booking", tags=["Booking"])

@booking_router.post("")
async def create_booking(request: RoomsBooking, db=Depends(get_db)):
    try:
        with db.cursor() as cursor:
            checkin = datetime.datetime.fromisoformat(request.CheckIn)
            checkout = datetime.datetime.fromisoformat(request.CheckOut)

            if checkout <= checkin:
                raise HTTPException(status_code=400, detail="Invalid date")

            num_nights = (checkout - checkin).days
            total_price_all = 0
            created_transactions = []

            # Lấy balance khách hàng
            cursor.execute("SELECT Balance FROM Customer WHERE CustomerID=%s", (request.CustomerID,))
            customer = cursor.fetchone()
            if not customer:
                raise HTTPException(status_code=404, detail="Customer not found")
            balance = float(customer["Balance"])

            # Duyệt RoomRequests
            for room_req in request.RoomRequests:
                room_type_id = room_req.RoomTypeID
                quantity = room_req.Quantity if room_req.Quantity > 0 else 1

                cursor.execute("SELECT Price FROM RoomType WHERE RoomTypeID=%s", (room_type_id,))
                price_row = cursor.fetchone()
                if not price_row:
                    raise HTTPException(status_code=404, detail=f"RoomType {room_type_id} not found")
                room_price = float(price_row["Price"])

                # Kiểm tra phòng khả dụng
                rooms_available = await get_rooms_available(room_type_id, request.CheckIn, request.CheckOut, db)
                if len(rooms_available) < quantity:
                    raise HTTPException(status_code=404, detail=f"Not enough rooms available for RoomType {room_type_id}")

                # Tạo transaction cho từng phòng
                for room in rooms_available[:quantity]:
                    if balance < room_price * num_nights:
                        raise HTTPException(status_code=400, detail="Insufficient balance for one of the rooms")
                    
                    cursor.execute(
                        "INSERT INTO `Transaction` (CustomerID, RoomID, CheckIn, CheckOut, Status) VALUES (%s, %s, %s, %s, %s)",
                        (request.CustomerID, room["RoomID"], request.CheckIn, request.CheckOut, "Pending")
                    )
                    transaction_id = cursor.lastrowid
                    created_transactions.append({
                        "transaction_id": transaction_id,
                        "room_id": room["RoomID"],
                        "price": room_price * num_nights
                    })
                    total_price_all += room_price * num_nights
                    balance -= room_price * num_nights  # trừ balance tạm thời

            db.commit()

            return {
                "message": "Booking created successfully",
                "total_price": total_price_all,
                "transactions": created_transactions,
                "checkin": request.CheckIn,
                "checkout": request.CheckOut,
                "status": "Pending"
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
