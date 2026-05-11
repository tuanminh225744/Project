from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserUpdateRequest
from typing import List, Optional
from app.repositories.user_responsitory import UserRepository

class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
    
    def get_user(self, user_id: int) -> Optional[User]:
        return self.user_repository.get_user(user_id)

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.user_repository.get_users(skip, limit)

    def update_user(self, user_id: int, user_update: UserUpdateRequest) -> Optional[User]:
        return self.user_repository.update_user(user_id, user_update)

    def delete_user(self, user_id: int) -> bool:
        return self.user_repository.delete_user(user_id)
    