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
