from fastapi import APIRouter, Depends
from db_connection import get_db, get_connection
from models import UserInDB
from security import pwd_context

user_router = APIRouter(prefix="/users", tags=["Users"])

@user_router.get("/")
async def get_customers(db=Depends(get_db)):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Customer")
            return {"customers": cursor.fetchall()}
    finally:
        conn.close()

@user_router.post("/add-customer")
async def add_customer(customer: UserInDB, db=Depends(get_db)):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            
            sql = "INSERT INTO Customer (UserName, FullName, Email, PhoneNumber, HashPassword, RoleID) VALUES (%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql, (customer.username, customer.fullname, customer.email,
                                 customer.phonenumber, pwd_context.hash(customer.hashed_password),
                                 customer.role_id))
            conn.commit()
            return {"message": "Customer added"}
    finally:
        conn.close()
