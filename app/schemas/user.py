from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional
from app.utils.validators import validate_no_space


class UserBase(BaseModel):
    name: str
    email: EmailStr
    @field_validator("name")
    @classmethod
    def check_username(cls, v):
        return validate_no_space(v)

class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True  