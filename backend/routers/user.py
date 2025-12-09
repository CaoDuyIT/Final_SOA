from fastapi import APIRouter, Depends, HTTPException
from db_connection import get_db, get_connection
from models import UserInDB, User
from security import pwd_context
from pydantic import BaseModel
from typing import Optional

user_router = APIRouter(prefix="/users", tags=["Users"])

class UserUpdate(BaseModel):
    fullname: str
    email: str
    phonenumber: str
    role_id: int
    username: str # Added username to be editable if needed, or just for display consistency

@user_router.get("/")
async def get_users(db=Depends(get_db)):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            SELECT c.CustomerID, c.UserName, c.FullName, c.Email, c.PhoneNumber, c.RoleID, r.Name AS RoleName
            FROM Customer c
            JOIN Role r ON c.RoleID = r.RoleID
            ORDER BY c.CustomerID DESC
            """)
            return {"users": cursor.fetchall()}
    finally:
        conn.close()

@user_router.post("/")
async def add_user(user: UserInDB, db=Depends(get_db)):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Check if username or email exists
            cursor.execute("SELECT CustomerID FROM Customer WHERE UserName = %s OR Email = %s", (user.username, user.email))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Username or Email already exists")

            sql = "INSERT INTO Customer (UserName, FullName, Email, PhoneNumber, HashPassword, RoleID) VALUES (%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql, (user.username, user.fullname, user.email,
                                 user.phonenumber, pwd_context.hash(user.hashed_password),
                                 user.role_id))
            conn.commit()
            return {"message": "User added successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@user_router.put("/{user_id}")
async def update_user(user_id: int, user: UserUpdate, db=Depends(get_db)):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Check if user exists
            cursor.execute("SELECT CustomerID FROM Customer WHERE CustomerID = %s", (user_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="User not found")

            # Check if role exists
            cursor.execute("SELECT RoleID FROM Role WHERE RoleID = %s", (user.role_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=400, detail="Invalid Role ID")

            sql = """
                UPDATE Customer 
                SET FullName = %s, Email = %s, PhoneNumber = %s, RoleID = %s, UserName = %s
                WHERE CustomerID = %s
            """
            cursor.execute(sql, (user.fullname, user.email, user.phonenumber, user.role_id, user.username, user_id))
            conn.commit()
            return {"message": "User updated successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@user_router.delete("/{user_id}")
async def delete_user(user_id: int, db=Depends(get_db)):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Check if user exists
            cursor.execute("SELECT CustomerID FROM Customer WHERE CustomerID = %s", (user_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="User not found")

            # 1. Delete from Staff first (to satisfy FK_Staff_Customer)
            cursor.execute("DELETE FROM Staff WHERE StaffID = %s", (user_id,))

            # 2. Delete Reviews
            cursor.execute("DELETE FROM Review WHERE CustomerID = %s", (user_id,))

            # 3. Delete Incidents
            cursor.execute("DELETE FROM Incident WHERE CustomerID = %s", (user_id,))

            # 4. Delete Transactions (and associated TransactionRooms)
            # First, get all TransactionIDs for this user
            cursor.execute("SELECT TransactionID FROM `Transaction` WHERE CustomerID = %s", (user_id,))
            transactions = cursor.fetchall()
            transaction_ids = [t['TransactionID'] for t in transactions]

            if transaction_ids:
                # Delete from TransactionRoom first
                format_strings = ','.join(['%s'] * len(transaction_ids))
                cursor.execute(f"DELETE FROM TransactionRoom WHERE TransactionID IN ({format_strings})", tuple(transaction_ids))
                
                # Then delete from Transaction
                cursor.execute(f"DELETE FROM `Transaction` WHERE TransactionID IN ({format_strings})", tuple(transaction_ids))

            # 5. Finally delete from Customer
            cursor.execute("DELETE FROM Customer WHERE CustomerID = %s", (user_id,))
            conn.commit()
            return {"message": "User and all associated data deleted successfully"}
    except Exception as e:
        conn.rollback()
        # Handle other FK constraints (like Transactions, Reviews)
        if "foreign key constraint fails" in str(e):
             raise HTTPException(status_code=400, detail="Cannot delete user: User has associated data (Bookings, Reviews, etc.) that prevents deletion.")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()