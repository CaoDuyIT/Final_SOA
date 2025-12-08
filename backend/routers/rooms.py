from fastapi import APIRouter, Depends, HTTPException
from db_connection import get_db
from typing import List
from models import RoomRequest, User, RoomType
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