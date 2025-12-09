import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import dotenv
from models import User
from services.auth_service import get_current_active_user
from db_connection import get_db
from fastapi import Depends

dotenv.load_dotenv()
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")

def send_reciept_email(transaction_id, current_user: User = Depends(get_current_active_user), db=Depends(get_db)):
    receiver_email = current_user.email
    receiver_name = current_user.fullname
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM `Transaction` WHERE TransactionID=%s", (transaction_id,))
            transaction = cursor.fetchone()
            if not transaction:
                raise Exception("Transaction not found")
    except Exception as e:
        print("Database error:", e)
        return
    
    booked_rooms = []
    try:
        with db.cursor() as cursor:
            cursor.execute("""
            SELECT r.RoomNumber
            FROM TransactionRoom tr
            JOIN Room r ON tr.RoomID = r.RoomID
            WHERE tr.TransactionID = %s
            """, (transaction_id,))
            booked_rooms = cursor.fetchall()
    except Exception as e:
        print("Database error:", e)
        return

    # --- Tạo nội dung mail ---
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email
    msg["Subject"] = "Hóa đơn thanh toán phòng của Hotel"

    body = """
    Ngày giao dịch: """ + str(transaction["PaidAt"]) + """
    Người đặt phòng: """ + str(receiver_name) + """
    Tổng số tiền: """ + str(transaction["TotalPrice"]) + """ VND
    Phòng đã đặt: """ + ", ".join([room["RoomNumber"] for room in booked_rooms]) + """
    
    Cảm ơn Quý khách đã sử dụng dịch vụ của Hotel
    """

    msg.attach(MIMEText(body, "plain"))

    # --- Gửi email ---
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # mã hóa kết nối
            server.login(SENDER_EMAIL, EMAIL_APP_PASSWORD)
            server.send_message(msg)
            print("Email sent successfully!")
    except Exception as e:
        print("Error:", e)