# login.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from dotenv import dotenv_values
from passlib.context import CryptContext
from user_service import get_user
from pwdlib import PasswordHash
from models import LoginRequest
from auth_service import authenticate_user

login_router = APIRouter(prefix="/login", tags=["Login"])

# --- Config ---
config = dotenv_values(".env")

SECRET_KEY = config["SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 100

pwd_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ========= JWT Token Creation =========
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ========= JSON login endpoint =========
@login_router.post("")
async def login_alias(loginReq: LoginRequest):
    username = loginReq.username
    password = loginReq.password

    if not username or not password:
        raise HTTPException(status_code=400, detail="Missing credentials")

    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role_id},
        expires_delta=access_token_expires
    )
    print("success")
    return {"access_token": access_token, "token_type": "bearer", "role": user.role_id}

# ========= Current user from token =========
# def get_current_user(token: str = Depends(oauth2_scheme)):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username = payload.get("sub")
#         role = payload.get("role")
#         if not username:
#             raise HTTPException(status_code=401, detail="Token missing user info")
#         return {"username": username, "role": role}
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")
