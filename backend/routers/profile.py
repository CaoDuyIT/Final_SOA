from fastapi import APIRouter, Depends
from models import User
from services.auth_service import get_current_active_user

profile_router = APIRouter(prefix="/profile", tags=["Profile"])

@profile_router.get("/me", response_model=User)
async def read_current_user(current_user: User = Depends(get_current_active_user)):
    return current_user
