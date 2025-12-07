from fastapi import FastAPI
from routers.auth import auth_router
from routers.user import user_router
from routers.role import role_router
from routers.profile import profile_router
from routers.rooms import room_router
from routers.booking import booking_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(role_router)
app.include_router(profile_router)
app.include_router(room_router)
app.include_router(booking_router)
