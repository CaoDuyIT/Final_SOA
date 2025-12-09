from fastapi import APIRouter, Depends, HTTPException, status
from db_connection import get_db, get_connection
from typing import List
from models import RoomRequest, User, RoomType, RoomCreate, RoomUpdateInfo
from services.auth_service import get_current_active_user
from services.rooms_service import get_rooms_available, get_rooms_available_by_type, get_rooms_by_type, get_all_room_types

room_router = APIRouter(prefix="/rooms", tags=["Rooms"])

# Get rooms by type
@room_router.get("/type/{room_type_id}", response_model=List[RoomRequest])
async def get_rooms_by_type(room_type_id: int, db=Depends(get_db)):
    try:
        rooms = get_rooms_by_type(room_type_id, db)

        if not rooms:
            raise HTTPException(status_code=404, detail="No rooms found for this room type")
        
        return rooms
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get rooms by type which are available    
@room_router.get("/type_available/{room_type_id}", response_model=List[RoomRequest])
async def get_rooms_available_by_type(room_type_id: int, db=Depends(get_db)):
    try:

        rooms = get_rooms_available_by_type(room_type_id, db)

        if not rooms:
            raise HTTPException(status_code=404, detail="No rooms left for this room type")
        
        return rooms
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Get rooms by tpye which are available with the input date
@room_router.get("/get_available_rooms/{room_type_id}", response_model=List[RoomRequest])
async def get_rooms_available(room_type_id: int, checkin: str, checkout: str, db=Depends(get_db)):
    try:
        rooms = get_rooms_available(room_type_id, checkin, checkout, db)

        if not rooms:
            raise HTTPException(404, "No rooms left")

        return rooms
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

    # Get all rooms types
@room_router.get("/get_all_type/")
async def get_all_rooms_type(current_user: User = Depends(get_current_active_user), db=Depends(get_db)):
    try:
        rooms = await get_all_room_types(db)

        if not rooms:
            raise HTTPException(status_code=404, detail="There are no room type for now")
        
        return rooms
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@room_router.get("/")
def get_all_rooms(conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT 
                    r.RoomID,
                    r.RoomNumber,
                    rt.Name as RoomType,
                    rt.Price,
                    s.Name as Status
                FROM Room r
                JOIN RoomType rt ON r.RoomTypeID = rt.RoomTypeID
                LEFT JOIN Status s ON r.StatusID = s.StatusID
                ORDER BY r.RoomNumber
            """
            cursor.execute(sql)
            return cursor.fetchall()
    except Exception as e:
        print(f"LỖI SERVER: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi Server: {str(e)}")

@room_router.post("/", status_code=status.HTTP_201_CREATED)
def create_room(room: RoomCreate, conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            # 1. Check RoomNumber exists
            cursor.execute("SELECT * FROM Room WHERE RoomNumber = %s", (room.room_number,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail=f"Phòng số {room.room_number} đã tồn tại")

            # 2. Lookup RoomTypeID from Name
            cursor.execute("SELECT RoomTypeID FROM RoomType WHERE Name = %s", (room.room_type_name,))
            rt_row = cursor.fetchone()
            if not rt_row:
                raise HTTPException(status_code=400, detail=f"Loại phòng '{room.room_type_name}' không tồn tại")
            room_type_id = rt_row['RoomTypeID']

            # 3. Lookup StatusID from Name
            cursor.execute("SELECT StatusID FROM Status WHERE Name = %s", (room.status,))
            s_row = cursor.fetchone()
            if not s_row:
                raise HTTPException(status_code=400, detail=f"Trạng thái '{room.status}' không tồn tại")
            status_id = s_row['StatusID']

            # 4. Insert
            cursor.execute(
                "INSERT INTO Room (RoomNumber, RoomTypeID, StatusID) VALUES (%s, %s, %s)",
                (room.room_number, room_type_id, status_id)
            )
            conn.commit()
            return {"message": "Thêm phòng thành công"}
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"LỖI SERVER: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi Server: {str(e)}")

@room_router.put("/{room_number}")
def update_room_info(room_number: str, update: RoomUpdateInfo, conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            # Check exist
            cursor.execute("SELECT * FROM Room WHERE RoomNumber = %s", (room_number,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Không tìm thấy phòng")

            fields = []
            params = []

            if update.room_number:
                # Check duplicate if changing room number
                if update.room_number != room_number:
                    cursor.execute("SELECT * FROM Room WHERE RoomNumber = %s", (update.room_number,))
                    if cursor.fetchone():
                        raise HTTPException(status_code=400, detail=f"Phòng số {update.room_number} đã tồn tại")
                    fields.append("RoomNumber = %s")
                    params.append(update.room_number)

            if update.room_type_name:
                cursor.execute("SELECT RoomTypeID FROM RoomType WHERE Name = %s", (update.room_type_name,))
                rt_row = cursor.fetchone()
                if not rt_row:
                    raise HTTPException(status_code=400, detail=f"Loại phòng '{update.room_type_name}' không tồn tại")
                fields.append("RoomTypeID = %s")
                params.append(rt_row['RoomTypeID'])

            if update.status:
                cursor.execute("SELECT StatusID FROM Status WHERE Name = %s", (update.status,))
                s_row = cursor.fetchone()
                if not s_row:
                    raise HTTPException(status_code=400, detail=f"Trạng thái '{update.status}' không tồn tại")
                fields.append("StatusID = %s")
                params.append(s_row['StatusID'])

            if not fields:
                return {"message": "Không có dữ liệu thay đổi"}

            params.append(room_number)
            sql = f"UPDATE Room SET {', '.join(fields)} WHERE RoomNumber = %s"
            cursor.execute(sql, tuple(params))
            conn.commit()
            return {"message": "Cập nhật phòng thành công"}
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"LỖI SERVER: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi Server: {str(e)}")

@room_router.delete("/room_number}")
def delete_room(room_number: str, conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            # 1. Lấy RoomID
            cursor.execute("SELECT RoomID FROM Room WHERE RoomNumber = %s", (room_number,))
            room = cursor.fetchone()
            if not room:
                raise HTTPException(status_code=404, detail="Không tìm thấy phòng")
            
            room_id = room['RoomID']

            # 2. Xóa dữ liệu liên quan (Cascade Delete thủ công)
            # Việc này sẽ xóa vĩnh viễn lịch sử đặt phòng, đánh giá, sự cố của phòng này.
            
            # Xóa Đánh giá (Review)
            cursor.execute("DELETE FROM Review WHERE RoomID = %s", (room_id,))
            
            # Xóa Sự cố (Incident)
            cursor.execute("DELETE FROM Incident WHERE RoomID = %s", (room_id,))
            
            # Xóa liên kết Giao dịch (TransactionRoom)
            cursor.execute("DELETE FROM TransactionRoom WHERE RoomID = %s", (room_id,))
            
            # 3. Xóa Phòng
            cursor.execute("DELETE FROM Room WHERE RoomNumber = %s", (room_number,))
            conn.commit()
                
            return {"message": f"Đã xóa phòng {room_number} và toàn bộ dữ liệu liên quan."}
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"LỖI SERVER: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi Server: {str(e)}")