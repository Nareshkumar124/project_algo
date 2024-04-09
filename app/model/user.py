from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId


class TokenData(BaseModel):
    id: str
    username: str
    email: EmailStr


class User(BaseModel):
    username: str = Field(min_length=3, max_length=50)  # pattern=r"^[a-zA-Z0-9_-]+$"
    password: str = Field(
        min_length=8,
        max_length=50,
        
    )

    email: EmailStr
    # pattern=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",


class UserDb(BaseModel):
    id: str
    username: str
    hash_password: str
    email: EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str
