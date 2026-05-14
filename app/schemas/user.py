from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from datetime import datetime
from typing import Optional
from app.utils.validators import validate_no_space


class UserBase(BaseModel):
    username: str
    email: EmailStr
    @field_validator("username")
    @classmethod
    def check_username(cls, v):
        return validate_no_space(v)

class UserCreateRequest(UserBase):
    pass


class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None

class UserResponse(UserBase):
    id: int
    role: str
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(
        from_attributes=True
    )  