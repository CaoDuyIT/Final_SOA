from fastapi import HTTPException

async def get_rooms_to_clean(db):
    try:
        with db.cursor() as cursor:
            sql = """
                SELECT 
                    r.RoomID,
                    r.RoomNumber,
                    rt.Name as RoomType,
                    s.Name as Status
                FROM Room r
                JOIN Status s ON r.StatusID = s.StatusID
                JOIN RoomType rt ON r.RoomTypeID = rt.RoomTypeID
                WHERE s.Name IN ('Need Clean', 'Cleaning', 'Wait Check Clean', 'Available') AND s.Type = 'Room'
            """
            cursor.execute(sql)
            rooms = cursor.fetchall()
            return rooms
    except Exception as e:
        print(f"LỖI SERVER: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi Server: {str(e)}")

async def update_room_status(room_number: str, status_update, db):
    # Chuẩn hóa input
    new_status = status_update.status.strip()
    
    # Housekeeping chỉ được phép chuyển thành 2 trạng thái này
    allowed_statuses = ["Cleaning", "Wait Check Clean"]
    if new_status not in allowed_statuses:
        raise HTTPException(status_code=400, detail="Housekeeping chỉ được phép chuyển trạng thái thành 'Cleaning' hoặc 'Wait Check Clean'")

    try:
        with db.cursor() as cursor:
            # 1. Kiểm tra trạng thái hiện tại của phòng
            cursor.execute("""
                SELECT s.Name 
                FROM Room r 
                JOIN Status s ON r.StatusID = s.StatusID 
                WHERE r.RoomNumber = %s
            """, (room_number,))
            result = cursor.fetchone()
            
            if not result:
                raise HTTPException(status_code=404, detail=f"Phòng số {room_number} không tồn tại")
            
            current_status = result['Name']
            
            # 2. Kiểm tra Logic chuyển đổi trạng thái
            if new_status == "Cleaning":
                # Chỉ được chuyển sang Cleaning nếu đang là 'Need Clean'
                if current_status.lower() != 'need clean':
                    raise HTTPException(status_code=400, detail=f"Không hợp lệ: Chỉ có thể bắt đầu dọn (Cleaning) khi phòng đang cần dọn (Need Clean). Trạng thái hiện tại: {current_status}")
            
            elif new_status == "Wait Check Clean":
                # Chỉ được chuyển sang Wait Check Clean nếu đang là 'Cleaning'
                if current_status.lower() != 'cleaning':
                    raise HTTPException(status_code=400, detail=f"Không hợp lệ: Chỉ có thể báo xong (Wait Check Clean) khi phòng đang được dọn (Cleaning). Trạng thái hiện tại: {current_status}")

            # 3. Lấy ID của trạng thái đích
            cursor.execute("SELECT StatusID FROM Status WHERE Name = %s AND Type = 'Room'", (new_status,))
            target_status = cursor.fetchone()
            
            if not target_status:
                # Fallback tìm kiếm nếu không khớp chính xác (ví dụ Cleaning vs cleaning)
                cursor.execute("SELECT StatusID FROM Status WHERE Name LIKE %s AND Type = 'Room'", (new_status,))
                target_status = cursor.fetchone()

            if not target_status:
                raise HTTPException(status_code=500, detail=f"cấu hình không tìm thấy trạng thái")
            
            target_status_id = target_status['StatusID']

            # 4. Cập nhật trạng thái
            cursor.execute("UPDATE Room SET StatusID = %s WHERE RoomNumber = %s", (target_status_id, room_number))
            db.commit()
            
            return {"message": f"Đã cập nhật phòng {room_number} sang trạng thái '{new_status}'"}

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"LỖI SERVER: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi Server: {str(e)}")
