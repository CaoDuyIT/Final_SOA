from pydantic import BaseModel

class User(BaseModel):
    username: str
    fullname: str
    email: str
    phonenumber: str
    role_id: int = 1
    disabled: bool | None = None

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

# ============ Room Model ==============
class RoomRequest(BaseModel):
    RoomID: int
    RoomNumber: str
    RoomTypeID: int
    StatusID: int

class RoomType(BaseModel):
    ID: int
    Name: str
    Description: str
    Price: int # Hoặc Decimal nếu bạn dùng
    MaxPeople: int
    BedCount: int

# ============ Booking Model ==============
class Rooms(BaseModel):
    RoomTypeID: int
    Quantity: int = 1


class RoomsBooking(BaseModel):
    CustomerID: int
    RoomRequests: list[Rooms]
    CheckIn: str
    CheckOut: str

# ========= Login Models =========
class LoginRequest(BaseModel):
    username: str
    password: str