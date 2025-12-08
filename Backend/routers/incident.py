from fastapi import APIRouter, Depends, HTTPException, status
from models import IncidentCreate, IncidentUpdate
import datetime
from db_connection import get_db

incident_router = APIRouter(prefix="/incident", tags=["Incident"])

# ==========================
# GUEST: Gửi báo cáo sự cố
# ==========================
@incident_router.post("/report", status_code=status.HTTP_201_CREATED)
def create_incident(incident: IncidentCreate, conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:

            # 1. Lấy transaction từ bảng Transaction
            cursor.execute("SELECT * FROM `Transaction` WHERE TransactionID = %s",
                           (incident.transaction_id,))
            transaction = cursor.fetchone()

            if not transaction:
                raise HTTPException(status_code=404, detail="Không tìm thấy giao dịch này")

            # 2. Lấy RoomID từ TransactionRoom
            cursor.execute("""
                SELECT RoomID 
                FROM TransactionRoom 
                WHERE TransactionID = %s
            """, (incident.transaction_id,))
            
            room_data = cursor.fetchone()

            if not room_data:
                raise HTTPException(status_code=404, detail="Không tìm thấy phòng cho giao dịch này")

            room_id = room_data["RoomID"]

            # 3. Tạo Incident
            cursor.execute("""
                INSERT INTO Incident (CustomerID, RoomID, StatusID, Description, CreateAt)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                transaction["CustomerID"],
                room_id,
                6,                       # Status: Reported
                incident.description,
                datetime.datetime.now()
            ))

            conn.commit()

            return {"message": "Đã gửi báo cáo sự cố thành công!"}

    except Exception as e:
        print("LỖI SERVER:", e)
        raise HTTPException(status_code=500, detail="Lỗi Server")


# ==========================
# MANAGER: Lấy danh sách sự cố
# ==========================
@incident_router.get("/get_incidents")
def get_incidents(conn=Depends(get_db)):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM Incident")
        return cursor.fetchall()


# ==========================
# MANAGER: Cập nhật trạng thái sự cố
# ==========================
@incident_router.put("/update/{incident_id}")
def update_incident_status(incident_id: int, update: IncidentUpdate, conn=Depends(get_db)):

    # Chuẩn hóa input
    new_status = update.status.strip()

    allowed_statuses = ['Reported', 'In Progress', 'Resolved']

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Trạng thái không hợp lệ. Chỉ được: {', '.join(allowed_statuses)}"
        )

    try:
        with conn.cursor() as cursor:
            # Kiểm tra sự cố tồn tại
            cursor.execute("SELECT * FROM Incident WHERE IncidentID = %s", (incident_id,))
            incident = cursor.fetchone()

            if not incident:
                raise HTTPException(status_code=404, detail="Không tìm thấy sự cố này")

            # Lấy StatusID theo tên trạng thái
            cursor.execute("""
                SELECT StatusID 
                FROM Status 
                WHERE Name = %s AND Type = 'Incident'
            """, (new_status,))
            status_row = cursor.fetchone()

            if not status_row:
                raise HTTPException(
                    status_code=500,
                    detail=f"Không tìm thấy trạng thái '{new_status}' trong bảng Status"
                )

            status_id = status_row['StatusID']

            # Update trạng thái
            cursor.execute("""
                UPDATE Incident 
                SET StatusID = %s 
                WHERE IncidentID = %s
            """, (status_id, incident_id))

            conn.commit()
            return {"message": f"Cập nhật trạng thái thành '{new_status}' thành công"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"LỖI SERVER: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi Server: {str(e)}")


# ==========================
# GUEST: Xác nhận đã giải quyết xong
# ==========================
@incident_router.put("/incidents/{incident_id}/confirm")
def confirm_incident_resolution(incident_id: int, conn=Depends(get_db)):

    try:
        with conn.cursor() as cursor:

            cursor.execute("SELECT * FROM Incident WHERE IncidentID = %s", (incident_id,))
            incident = cursor.fetchone()

            if not incident:
                raise HTTPException(status_code=404, detail="Không tìm thấy sự cố này")

            # Chỉ được xác nhận khi Manager đã xử lý xong = Resolved (ID=2)
            if incident['StatusID'] != 2:
                raise HTTPException(
                    status_code=400,
                    detail="Sự cố chưa được Manager xử lý (Resolved). Bạn chưa thể xác nhận."
                )

            # Đổi sang trạng thái cuối: Hoàn tất (3)
            cursor.execute("""
                UPDATE Incident 
                SET StatusID = 3 
                WHERE IncidentID = %s
            """, (incident_id,))

            conn.commit()
            return {"message": "Cảm ơn bạn! Sự cố đã được đóng lại."}

    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR SERVER: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error Server: {str(e)}")
