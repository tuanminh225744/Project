from datetime import datetime
from unittest.mock import Mock, patch

import pytest
import json
from app.models.users import User
from app.schemas.user import UserUpdateRequest
from app.services.user_service import UserService



def make_user(user_id=1):
    return User(
        id=user_id,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User",
        avatar_url=None,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def service():
    return UserService(db=Mock())


def test_get_user_from_repository_when_cache_miss(service):
    user = make_user()
    service.user_repository.get_user = Mock(return_value=user)

    with patch("app.services.user_service.redis_client") as redis_mock:
        redis_mock.get.return_value = None

        result = service.get_user(1)

        assert result.id == 1
        assert result.username == "testuser"
        service.user_repository.get_user.assert_called_once_with(1)
        redis_mock.setex.assert_called_once()

def test_get_user_from_cache():
    service = UserService(db=Mock())
    service.user_repository.get_user = Mock()

    cached_user = {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "avatar_url": None,
        "is_active": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    with patch("app.services.user_service.redis_client") as redis_mock:
        redis_mock.get.return_value = json.dumps(cached_user)

        result = service.get_user(1)

        assert result.id == 1
        assert result.username == "testuser"
        assert result.email == "test@example.com"

        service.user_repository.get_user.assert_not_called()
        redis_mock.get.assert_called_once_with("user:1")
        redis_mock.setex.assert_not_called()


def test_get_user_returns_none_when_not_found(service):
    service.user_repository.get_user = Mock(return_value=None)

    with patch("app.services.user_service.redis_client") as redis_mock:
        redis_mock.get.return_value = None

        result = service.get_user(999)

        assert result is None
        service.user_repository.get_user.assert_called_once_with(999)
        redis_mock.setex.assert_not_called()


def test_get_users_from_repository_when_cache_miss(service):
    users = [make_user(1), make_user(2)]
    service.user_repository.get_users = Mock(return_value=users)

    with patch("app.services.user_service.redis_client") as redis_mock:
        redis_mock.get.return_value = None

        result = service.get_users(skip=0, limit=10)

        assert len(result) == 2
        assert result[0].id == 1
        service.user_repository.get_users.assert_called_once_with(0, 10)
        redis_mock.setex.assert_called_once()

def test_get_users_from_cache():
    service = UserService(db=Mock())
    service.user_repository.get_users = Mock()

    cached_users = [
        {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "avatar_url": None,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
    ]

    with patch("app.services.user_service.redis_client") as redis_mock:
        redis_mock.get.return_value = json.dumps(cached_users)

        result = service.get_users(skip=0, limit=10)

        assert len(result) == 1
        assert result[0].id == 1

        service.user_repository.get_users.assert_not_called()
        redis_mock.get.assert_called_once_with("users:0:10")
        redis_mock.setex.assert_not_called()

def test_update_user_success(service):
    user = make_user()
    updated_user = make_user()
    updated_user.full_name = "Updated Name"

    service.user_repository.get_user = Mock(return_value=user)
    service.user_repository.update_user = Mock(return_value=updated_user)

    with patch.object(service, "_invalidate_user_cache") as invalidate_mock:
        result = service.update_user(
            1,
            UserUpdateRequest(full_name="Updated Name"),
        )

        assert result.full_name == "Updated Name"
        service.user_repository.get_user.assert_called_once_with(1)
        service.user_repository.update_user.assert_called_once()
        invalidate_mock.assert_called_once_with(1)


def test_update_user_not_found(service):
    service.user_repository.get_user = Mock(return_value=None)

    with pytest.raises(ValueError, match="User not found"):
        service.update_user(999, UserUpdateRequest(full_name="Updated Name"))


def test_delete_user_success(service):
    service.user_repository.get_user = Mock(return_value=make_user())
    service.user_repository.delete_user = Mock(return_value=True)

    with patch.object(service, "_invalidate_user_cache") as invalidate_mock:
        result = service.delete_user(1)

        assert result is True
        service.user_repository.delete_user.assert_called_once_with(1)
        invalidate_mock.assert_called_once_with(1)


def test_delete_user_not_found(service):
    service.user_repository.get_user = Mock(return_value=None)

    with pytest.raises(ValueError, match="User not found"):
        service.delete_user(999)
