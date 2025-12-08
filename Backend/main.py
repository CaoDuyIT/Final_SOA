from fastapi import FastAPI
from routers.auth import auth_router
from routers.user import user_router
from routers.role import role_router
from routers.profile import profile_router
from routers.rooms import room_router
from routers.booking import booking_router
from routers.login import login_router
from routers.review import review_router
from routers.incident import incident_router

from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(role_router)
app.include_router(profile_router)
app.include_router(room_router)
app.include_router(booking_router)
app.include_router(login_router)
app.include_router(review_router)
app.include_router(incident_router)

# Allow frontend dev server (Live Server) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500",
                   "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)