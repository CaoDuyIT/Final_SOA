from fastapi import APIRouter, Depends
transaction_router = APIRouter(prefix="/transctions", tags=["Transctions"])

@transaction_router.get("/send-otp")
async def send_otp():
    return {"message": "OTP sent"}