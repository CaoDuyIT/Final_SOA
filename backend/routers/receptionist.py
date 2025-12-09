from fastapi import APIRouter, Depends, HTTPException, Query
from db_connection import get_db
from services.receptionist_service import search_bookings, check_in, check_out

receptionist_router = APIRouter(prefix="/receptionist", tags=["Receptionist"])

@receptionist_router.get("/bookings/search")
async def search_bookings_endpoint(query: str = Query(None, min_length=0), db=Depends(get_db)):
    """
    Search bookings by Customer Name, Transaction ID, or Phone Number.
    If query is empty, returns all bookings.
    """
    return await search_bookings(query, db)

@receptionist_router.post("/bookings/{transaction_id}/check-in")
async def check_in_endpoint(transaction_id: int, db=Depends(get_db)):
    """
    Perform check-in for a booking. Updates Transaction status to 'Occupied' and Room status to 'Occupied'.
    """
    return await check_in(transaction_id, db)

@receptionist_router.post("/bookings/{transaction_id}/check-out")
async def check_out_endpoint(transaction_id: int, db=Depends(get_db)):
    """
    Perform check-out for a booking. Updates Transaction status to 'Completed' and Room status to 'Need Clean'.
    """
    return await check_out(transaction_id, db)