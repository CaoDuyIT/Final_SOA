from pydantic import BaseModel

class User(BaseModel):
    username: str
    fullname: str
    email: str
    phonenumer: str
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

# ============ Booking Model ==============
class Rooms(BaseModel):
    RoomTypeID: int
    Quantity: int = 1

class RoomsBooking(BaseModel):
    CustomerID: int
    RoomRequests: list[Rooms]
    CheckIn: str
    CheckOut: str