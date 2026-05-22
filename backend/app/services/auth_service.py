from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories.user_responsitory import UserRepository
from app.models.users import User
from app.schemas.user import UserCreateRequest, UserResponse

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token
)
class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
    
    def register_user(self, user_data: UserCreateRequest) -> User:
        existing_username = self.user_repository.get_user_by_username(user_data.username)
        existing_email = self.user_repository.get_user_by_email(user_data.email)
        if existing_username:
            raise ValueError("Username already registered")
        if existing_email:
            raise ValueError("Email already registered")

        hashed_pwd = hash_password(user_data.password)
        user_create = UserCreateRequest(
            username=user_data.username,
            email=user_data.email,
            password=hashed_pwd,
            full_name=user_data.full_name,
            avatar_url=user_data.avatar_url,
            is_active=user_data.is_active
        )
        return self.user_repository.create_user(user_create)

    def authenticate_user(self, username: str, password: str) -> User | None:
        user = self.user_repository.get_user_by_username(username)
        if not user:
            raise ValueError("User not found")
        if not verify_password(password, user.hashed_password):
            raise ValueError("Invalid username or password")
        return user

    def login_user(self, username: str, password: str) -> dict:
        user = self.authenticate_user(username, password)
        if not user:
            raise ValueError("Invalid username or password")
        
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user)
        }

    def refresh_access_token(self, refresh_token: str) -> dict:
        refresh_data = verify_refresh_token(refresh_token)
        user_id = refresh_data["user_id"]
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        

        new_access_token = create_access_token(data={"sub": str(user_id)})
        new_refresh_token = create_refresh_token(data={"sub": str(user_id)})

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }


    