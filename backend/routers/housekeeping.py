from fastapi import APIRouter, Depends, HTTPException
from db_connection import get_db
from models import RoomStatusUpdate
from services.housekeeping_service import get_rooms_to_clean, update_room_status

housekeeping_router = APIRouter(prefix="/housekeeping", tags=["Housekeeping"])

@housekeeping_router.get("/rooms-to-clean")
async def get_rooms_to_clean_endpoint(db=Depends(get_db)):
    return await get_rooms_to_clean(db)

@housekeeping_router.put("/rooms/{room_number}/status")
async def update_room_status_endpoint(room_number: str, status_update: RoomStatusUpdate, db=Depends(get_db)):
    return await update_room_status(room_number, status_update, db)