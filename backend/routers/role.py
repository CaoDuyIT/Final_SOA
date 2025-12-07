from fastapi import APIRouter, Depends
from db_connection import get_connection, get_db

role_router = APIRouter(prefix="/roles", tags=["Roles"])

@role_router.get("/")
async def get_roles(db=Depends(get_db)):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Role")
            return {"roles": cursor.fetchall()}
    finally:
        conn.close()