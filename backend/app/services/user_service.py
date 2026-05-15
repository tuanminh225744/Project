import json
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.users import User
from app.schemas.user import UserResponse, UserUpdateRequest
from app.repositories.user_responsitory import UserRepository
from app.core.cache import redis_client
from fastapi.encoders import jsonable_encoder

class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)

    def _user_cache_key(self, user_id: int) -> str:
        return f"user:{user_id}"

    def _users_cache_key(self, skip: int, limit: int) -> str:
        return f"users:{skip}:{limit}"

    def _invalidate_user_cache(self, user_id: int):
        redis_client.delete(self._user_cache_key(user_id))
        keys = redis_client.keys(f"users:*")
        for key in keys:
            redis_client.delete(key)

    def get_user(self, user_id: int) -> Optional[UserResponse]:
        cache_key = self._user_cache_key(user_id)
        cached_user = redis_client.get(cache_key)
        if cached_user:
            user_data = json.loads(cached_user)
            return UserResponse.model_validate(user_data)

        user = self.user_repository.get_user(user_id)
        if not user:
            return None

        user_response = UserResponse.model_validate(user)
        redis_client.setex(cache_key, 300, json.dumps(jsonable_encoder(user_response)))
        return user_response

    def get_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        cache_key = self._users_cache_key(skip, limit)
        cached_users = redis_client.get(cache_key)
        if cached_users:
            users_data = json.loads(cached_users)
            return [UserResponse.model_validate(item) for item in users_data]

        users = self.user_repository.get_users(skip, limit)
        user_responses = [UserResponse.model_validate(user) for user in users]
        redis_client.setex(cache_key, 300, json.dumps(jsonable_encoder(user_responses)))
        return [UserResponse.model_validate(data) for data in user_responses]

    def update_user(self, user_id: int, user_update: UserUpdateRequest) -> Optional[UserResponse]:
        user = self.user_repository.get_user(user_id)
        if not user:
            raise ValueError("User not found")

        updated = self.user_repository.update_user(user_id, user_update)
        self._invalidate_user_cache(user_id)
        return UserResponse.model_validate(updated) if updated else None

    def delete_user(self, user_id: int) -> bool:
        user = self.user_repository.get_user(user_id)
        if not user:
            raise ValueError("User not found")

        success = self.user_repository.delete_user(user_id)
        if success:
            self._invalidate_user_cache(user_id)
        return success
    