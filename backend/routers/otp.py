from fastapi import APIRouter, Depends
from otp_service import generate_otp, send_otp_email
from models import User
from auth_service import get_current_active_user

opt_router = APIRouter(prefix="/otp", tags=["OTP"])

@opt_router.get("/send-otp")
async def send_otp(current_user: User = Depends(get_current_active_user)):
    otp = generate_otp()
    send_otp_email(current_user.email, otp)
    return {"message": "OTP sent"}