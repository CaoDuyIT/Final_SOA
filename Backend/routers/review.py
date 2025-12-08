from fastapi import APIRouter, Depends, HTTPException, status
from models import ReviewCreate
import datetime
from db_connection import get_db

review_router = APIRouter(prefix="/review", tags=["Review"])

# ===============================
#   API TẠO REVIEW
# ===============================
@review_router.post("/", status_code=status.HTTP_201_CREATED)
def create_review(review: ReviewCreate, conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:

            # 1) Kiểm tra giao dịch hợp lệ
            cursor.execute(
                "SELECT * FROM `Transaction` WHERE TransactionID = %s",
                (review.transaction_id,)
            )
            transaction = cursor.fetchone()

            if not transaction:
                raise HTTPException(status_code=404, detail="Không tìm thấy giao dịch")

            if transaction["Status"] != "Paid":
                raise HTTPException(
                    status_code=400,
                    detail="Giao dịch chưa thanh toán, không thể đánh giá"
                )

            customer_id = transaction["CustomerID"]
            room_id = transaction["RoomID"]

            # 2) Kiểm tra khách này đã đánh giá phòng này chưa
            cursor.execute(
                """
                SELECT * FROM Review
                WHERE CustomerID = %s AND RoomID = %s
                """,
                (customer_id, room_id)
            )
            exist = cursor.fetchone()

            if exist:
                raise HTTPException(
                    status_code=400,
                    detail="Bạn đã đánh giá phòng này rồi."
                )

            # 3) Tạo review
            cursor.execute(
                """
                INSERT INTO Review (CustomerID, RoomID, Rating, ReviewText, CreateAt)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    customer_id,
                    room_id,
                    review.rating,
                    review.comment,
                    datetime.datetime.now()
                )
            )
            conn.commit()

            return {"message": "Đánh giá thành công!"}

    except HTTPException:
        raise
    except Exception as e:
        print("SERVER ERROR:", e)
        raise HTTPException(status_code=500, detail="Lỗi server")


# ===============================
#   API LẤY TẤT CẢ REVIEW
# ===============================
@review_router.get("/get_reviews")
def get_all_reviews(conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    rv.ReviewID,
                    c.FullName AS GuestName,
                    r.RoomNumber,
                    rt.Name AS RoomType,
                    rv.Rating,
                    rv.ReviewText,
                    rv.CreateAt
                FROM Review rv
                JOIN Customer c ON rv.CustomerID = c.CustomerID
                JOIN Room r ON rv.RoomID = r.RoomID
                JOIN RoomType rt ON r.RoomTypeID = rt.RoomTypeID
                ORDER BY rv.CreateAt DESC
                """
            )
            return cursor.fetchall()

    except Exception as e:
        print("SERVER ERROR:", e)
        raise HTTPException(status_code=500, detail="Lỗi server")
