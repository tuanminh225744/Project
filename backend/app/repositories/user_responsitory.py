from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.users import User
from app.schemas.user import UserCreateRequest, UserUpdateRequest


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.db.query(User).offset(skip).limit(limit).all()

    def create_user(self, user_data: UserCreateRequest) -> User:
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=user_data.password,  # Note: password should be hashed before calling this
            full_name=user_data.full_name,
            avatar_url=user_data.avatar_url,
            is_active=user_data.is_active
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user(self, user_id: int, user_update: UserUpdateRequest) -> Optional[User]:
        db_user = self.get_user(user_id)
        if db_user:
            update_data = user_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_user, field, value)
            self.db.commit()
            self.db.refresh(db_user)
        return db_user

    def delete_user(self, user_id: int) -> bool:
        db_user = self.get_user(user_id)
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return True
        return False

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    