from pydantic import BaseModel

class User(BaseModel):
    username: str
    fullname: str
    email: str
    phonenumber: str
    role_id: int = 1
    disabled: bool | None = None
    customer_id: int | None = None   

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

# ========= History Models =========
class BookingHistory(BaseModel):
    TransactionID: int
    RoomNumber: str
    RoomType: str
    Status: str
    BookingDate: str

# ========= Reviews Models =========
class ReviewCreate(BaseModel):
    transaction_id: int
    rating: int
    comment: str

# ============ Incident =================
class IncidentCreate(BaseModel):
    transaction_id: int
    description: str

class IncidentUpdate(BaseModel):
    status: str