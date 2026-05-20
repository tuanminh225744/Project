import json
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from app.models.project_members import ProjectMember
from app.models.projects import Project
from app.schemas.project import ProjectCreateRequest, ProjectUpdateRequest
from app.services.project_service import ProjectService


def make_project(project_id=1, owner_id=10, status="todo", priority="medium"):
    return Project(
        id=project_id,
        name="Test Project",
        description="Test description",
        status=status,
        priority=priority,
        due_date=None,
        owner_id=owner_id,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


def make_project_member(member_id=1, project_id=1, user_id=10, role="member"):
    return ProjectMember(
        id=member_id,
        project_id=project_id,
        user_id=user_id,
        role=role,
        joined_at=datetime.now(),
    )


@pytest.fixture
def service():
    return ProjectService(db=Mock())


def test_get_project_from_cache(service):
    service.project_repository.get_project = Mock()

    cached_project = {
        "id": 1,
        "name": "Test Project",
        "description": "Test description",
        "status": "todo",
        "priority": "medium",
        "due_date": None,
        "owner_id": 10,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    with patch("app.services.project_service.redis_client") as redis_mock:
        redis_mock.get.return_value = json.dumps(cached_project)

        result = service.get_project(1)

        assert result.id == 1
        assert result.name == "Test Project"
        assert result.owner_id == 10
        service.project_repository.get_project.assert_not_called()
        redis_mock.get.assert_called_once_with("project:1")
        redis_mock.setex.assert_not_called()


def test_get_project_from_repository_when_cache_miss(service):
    project = make_project()
    service.project_repository.get_project = Mock(return_value=project)

    with patch("app.services.project_service.redis_client") as redis_mock:
        redis_mock.get.return_value = None

        result = service.get_project(1)

        assert result.id == 1
        assert result.name == "Test Project"
        service.project_repository.get_project.assert_called_once_with(1)
        redis_mock.setex.assert_called_once()


def test_get_project_returns_none_when_not_found(service):
    service.project_repository.get_project = Mock(return_value=None)

    with patch("app.services.project_service.redis_client") as redis_mock:
        redis_mock.get.return_value = None

        result = service.get_project(999)

        assert result is None
        service.project_repository.get_project.assert_called_once_with(999)
        redis_mock.setex.assert_not_called()


def test_get_project_denies_access_when_user_is_not_owner_or_member(service):
    service.project_repository.get_project = Mock(return_value=make_project(owner_id=10))
    service.project_member_repository.is_user_in_project = Mock(return_value=False)

    with pytest.raises(ValueError, match="Access denied"):
        service.get_project(1, user_id=99)

    service.project_member_repository.is_user_in_project.assert_called_once_with(1, 99)


def test_get_projects_by_owner_from_cache(service):
    service.project_repository.get_projects_by_owner = Mock()

    cached_projects = [
        {
            "id": 1,
            "name": "Test Project",
            "description": "Test description",
            "status": "todo",
            "priority": "medium",
            "due_date": None,
            "owner_id": 10,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
    ]

    with patch("app.services.project_service.redis_client") as redis_mock:
        redis_mock.get.return_value = json.dumps(cached_projects)

        result = service.get_projects_by_owner(owner_id=10, skip=0, limit=10)

        assert len(result) == 1
        assert result[0].id == 1
        service.project_repository.get_projects_by_owner.assert_not_called()
        redis_mock.get.assert_called_once_with("projects:owner:10:0:10")
        redis_mock.setex.assert_not_called()


def test_get_projects_by_owner_from_repository_when_cache_miss(service):
    projects = [make_project(1), make_project(2)]
    service.project_repository.get_projects_by_owner = Mock(return_value=projects)

    with patch("app.services.project_service.redis_client") as redis_mock:
        redis_mock.get.return_value = None

        result = service.get_projects_by_owner(owner_id=10, skip=0, limit=10)

        assert len(result) == 2
        assert result[0].id == 1
        service.project_repository.get_projects_by_owner.assert_called_once_with(10, 0, 10)
        redis_mock.setex.assert_called_once()


def test_get_user_projects_returns_member_projects(service):
    members = [
        make_project_member(project_id=1, user_id=20),
        make_project_member(project_id=2, user_id=20),
    ]
    service.project_member_repository.get_user_projects = Mock(return_value=members)
    service.project_repository.get_project = Mock(
        side_effect=[make_project(1, owner_id=10), make_project(2, owner_id=11)]
    )

    result = service.get_user_projects(user_id=20, skip=0, limit=10)

    assert len(result) == 2
    assert [project.id for project in result] == [1, 2]
    service.project_member_repository.get_user_projects.assert_called_once_with(20)


def test_create_project_creates_owner_member(service):
    project = make_project(project_id=1, owner_id=10)
    service.project_repository.create_project = Mock(return_value=project)
    service.project_member_repository.create_project_member = Mock()

    result = service.create_project(
        ProjectCreateRequest(name="Test Project", description="Test description"),
        owner_id=10,
    )

    assert result.id == 1
    assert result.owner_id == 10
    service.project_repository.create_project.assert_called_once()


def test_update_project_success_when_owner(service):
    updated_project = make_project()
    updated_project.name = "Updated Project"
    service.project_repository.get_project = Mock(return_value=make_project(owner_id=10))
    service.project_repository.update_project = Mock(return_value=updated_project)

    with patch.object(service, "_invalidate_project_cache") as invalidate_mock:
        result = service.update_project(
            1,
            ProjectUpdateRequest(name="Updated Project"),
            user_id=10,
        )

        assert result.name == "Updated Project"
        service.project_repository.update_project.assert_called_once()
        invalidate_mock.assert_called_once_with(1)

def test_delete_project_success_when_owner(service):
    service.project_repository.get_project = Mock(return_value=make_project(owner_id=10))
    service.project_repository.delete_project = Mock(return_value=True)

    with patch.object(service, "_invalidate_project_cache") as invalidate_mock:
        result = service.delete_project(1, user_id=10)

        assert result is True
        service.project_repository.delete_project.assert_called_once_with(1)
        invalidate_mock.assert_called_once_with(1)


def test_delete_project_denies_non_owner(service):
    service.project_repository.get_project = Mock(return_value=make_project(owner_id=10))
    service.project_repository.delete_project = Mock()

    with pytest.raises(ValueError, match="Only project owner can delete project"):
        service.delete_project(1, user_id=20)

    service.project_repository.delete_project.assert_not_called()
