from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel
from ..books import schemas

class UserStatus(str, Enum):
    SUPERUSER = "superuser"
    ADMIN = "admin"
    USER = "user"

class UserBase(BaseModel):
    email: str
    name: str
    age: int

class User(UserBase):
    id: int
    status: UserStatus 
    is_active: bool
    is_borrower: bool
    is_member: bool
    borrowed_books: list[schemas.Book]
    registered_date: date   

    class Config:
        orm_mode = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: str | None = None
    name: str | None = None
    age: int | None = None
    password: str | None = None
    
class JWTTokenData(BaseModel):
    email: str
    scope: str | None 
    expire_date: datetime 