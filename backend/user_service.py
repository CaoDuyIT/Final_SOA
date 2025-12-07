from models import UserInDB
from db_connection import get_connection

def get_user(username: str):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM Customer WHERE UserName = %s", (username,)
            )
            result = cursor.fetchone()
            if result:
                return UserInDB(
                    username=result["UserName"],
                    fullname=result["FullName"],
                    email=result["Email"],
                    phonenumer=result["PhoneNumber"],
                    role_id=result["RoleID"],
                    hashed_password=result["HashPassword"]
                )
    finally:
        conn.close()
    return None
