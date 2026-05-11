from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserUpdateRequest

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()

    def get_users(self, skip: int = 0, limit: int = 100):
            return self.db.query(User).offset(skip).limit(limit).all()

    def update_user(self, user_id: int, user_update: UserUpdateRequest):
            db_user = self.get_user(user_id)
            if db_user:
                update_data = user_update.model_dump(exclude_unset=True)
                for field, value in update_data.items():
                    setattr(db_user, field, value)
                self.db.commit()
                self.db.refresh(db_user)
            return db_user

    def delete_user(self, user_id: int):
            db_user = self.get_user(user_id)
            if db_user:
                self.db.delete(db_user)
                self.db.commit()
                return True
            return False
    
    def create_user(self, username: str, email: str, hashed_password: str) -> User:
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()
    