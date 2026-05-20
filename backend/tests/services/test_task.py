import json
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from app.models.project_members import ProjectMember
from app.models.projects import Project
from app.models.tasks import Task
from app.schemas.task_schema import TaskCreateRequest, TaskUpdateRequest
from app.services.task_service import TaskService


def make_task(task_id=1, project_id=1, created_by=10, assignee_id=20):
    return Task(
        id=task_id,
        project_id=project_id,
        title="Test Task",
        description="Test description",
        status="todo",
        priority="medium",
        assignee_id=assignee_id,
        created_by=created_by,
        due_date=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


def make_project(project_id=1, owner_id=10):
    return Project(
        id=project_id,
        name="Test Project",
        description="Test description",
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
    return TaskService(db=Mock())


def test_get_task_returns_none_when_not_found(service):
    service.task_repository.get_task = Mock(return_value=None)

    result = service.get_task(task_id=999, user_id=10)

    assert result is None
    service.task_repository.get_task.assert_called_once_with(999)


def test_get_task_denies_access(service):
    service.task_repository.get_task = Mock(return_value=make_task())

    with patch.object(service, "_can_access_project", return_value=False):
        with pytest.raises(ValueError, match="Access denied"):
            service.get_task(task_id=1, user_id=99)


def test_get_task_from_cache(service):
    service.task_repository.get_task = Mock(return_value=make_task())
    cached_task = {
        "id": 1,
        "project_id": 1,
        "title": "Test Task",
        "description": "Test description",
        "status": "todo",
        "priority": "medium",
        "assignee_id": 20,
        "created_by": 10,
        "due_date": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    with patch.object(service, "_can_access_project", return_value=True):
        with patch("app.services.task_service.redis_client") as redis_mock:
            redis_mock.get.return_value = json.dumps(cached_task)

            result = service.get_task(task_id=1, user_id=10)

            assert result.id == 1
            assert result.title == "Test Task"
            redis_mock.get.assert_called_once_with("task:1")
            redis_mock.setex.assert_not_called()


def test_get_task_from_repository_when_cache_miss(service):
    service.task_repository.get_task = Mock(return_value=make_task())

    with patch.object(service, "_can_access_project", return_value=True):
        with patch("app.services.task_service.redis_client") as redis_mock:
            redis_mock.get.return_value = None

            result = service.get_task(task_id=1, user_id=10)

            assert result.id == 1
            assert result.project_id == 1
            service.task_repository.get_task.assert_called_once_with(1)
            redis_mock.setex.assert_called_once()


def test_get_tasks_by_project_denies_access(service):
    service.task_repository.get_tasks_by_project = Mock()

    with patch.object(service, "_can_access_project", return_value=False):
        with pytest.raises(ValueError, match="Access denied"):
            service.get_tasks_by_project(project_id=1, user_id=99)

    service.task_repository.get_tasks_by_project.assert_not_called()


def test_get_tasks_by_project_from_cache(service):
    service.task_repository.get_tasks_by_project = Mock()
    cached_tasks = [
        {
            "id": 1,
            "project_id": 1,
            "title": "Test Task",
            "description": "Test description",
            "status": "todo",
            "priority": "medium",
            "assignee_id": 20,
            "created_by": 10,
            "due_date": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
    ]

    with patch.object(service, "_can_access_project", return_value=True):
        with patch("app.services.task_service.redis_client") as redis_mock:
            redis_mock.get.return_value = json.dumps(cached_tasks)

            result = service.get_tasks_by_project(project_id=1, user_id=10, skip=0, limit=10)

            assert len(result) == 1
            assert result[0].id == 1
            service.task_repository.get_tasks_by_project.assert_not_called()
            redis_mock.get.assert_called_once_with("tasks:project:1:0:10")
            redis_mock.setex.assert_not_called()


def test_get_tasks_by_project_from_repository_when_cache_miss(service):
    service.task_repository.get_tasks_by_project = Mock(
        return_value=[make_task(1), make_task(2)]
    )

    with patch.object(service, "_can_access_project", return_value=True):
        with patch("app.services.task_service.redis_client") as redis_mock:
            redis_mock.get.return_value = None

            result = service.get_tasks_by_project(project_id=1, user_id=10, skip=0, limit=10)

            assert len(result) == 2
            assert result[0].id == 1
            service.task_repository.get_tasks_by_project.assert_called_once_with(1, 0, 10)
            redis_mock.setex.assert_called_once()


def test_get_tasks_by_assignee_denies_other_user(service):
    service.task_repository.get_tasks_by_assignee = Mock()

    with pytest.raises(ValueError, match="Access denied"):
        service.get_tasks_by_assignee(assignee_id=20, user_id=10)

    service.task_repository.get_tasks_by_assignee.assert_not_called()


def test_get_tasks_by_assignee_filters_inaccessible_projects(service):
    tasks = [make_task(1, project_id=1), make_task(2, project_id=2)]
    service.task_repository.get_tasks_by_assignee = Mock(return_value=tasks)

    with patch.object(service, "_can_access_project", side_effect=[True, False]):
        result = service.get_tasks_by_assignee(assignee_id=20, user_id=20, skip=0, limit=10)

    assert len(result) == 1
    assert result[0].id == 1
    service.task_repository.get_tasks_by_assignee.assert_called_once_with(20, 0, 10)


def test_get_my_tasks_combines_deduplicates_and_filters_access(service):
    created_task = make_task(1, project_id=1, created_by=10, assignee_id=None)
    shared_task = make_task(2, project_id=2, created_by=10, assignee_id=10)
    inaccessible_task = make_task(3, project_id=3, created_by=99, assignee_id=10)

    service.task_repository.get_tasks_by_creator = Mock(return_value=[created_task, shared_task])
    service.task_repository.get_tasks_by_assignee = Mock(return_value=[shared_task, inaccessible_task])

    def can_access(project_id, user_id):
        return project_id in [1, 2]

    with patch.object(service, "_can_access_project", side_effect=can_access):
        result = service.get_my_tasks(user_id=10, skip=0, limit=10)

    assert len(result) == 2
    assert sorted(task.id for task in result) == [1, 2]
    service.task_repository.get_tasks_by_creator.assert_called_once_with(10, 0, 10)
    service.task_repository.get_tasks_by_assignee.assert_called_once_with(10, 0, 10)


def test_create_task_success_sets_created_by(service):
    created_task = make_task(created_by=10)
    service.task_repository.create_task = Mock(return_value=created_task)
    task_data = TaskCreateRequest(
        project_id=1,
        title="Test Task",
        description="Test description",
        created_by=999,
    )

    with patch.object(service, "_can_access_project", return_value=True):
        result = service.create_task(task_data, creator_id=10)

    assert result.id == 1
    assert result.created_by == 10
    created_arg = service.task_repository.create_task.call_args.args[0]
    assert created_arg.created_by == 10


def test_create_task_denies_access(service):
    service.task_repository.create_task = Mock()
    task_data = TaskCreateRequest(project_id=1, title="Test Task", created_by=10)

    with patch.object(service, "_can_access_project", return_value=False):
        with pytest.raises(ValueError, match="Access denied"):
            service.create_task(task_data, creator_id=10)

    service.task_repository.create_task.assert_not_called()


def test_update_task_success_when_creator(service):
    updated_task = make_task(created_by=10)
    updated_task.title = "Updated Task"
    service.task_repository.get_task = Mock(return_value=make_task(created_by=10))
    service.task_repository.update_task = Mock(return_value=updated_task)

    with patch.object(service, "_can_access_project", return_value=True):
        with patch.object(service, "_invalidate_task_cache") as invalidate_mock:
            result = service.update_task(
                1,
                TaskUpdateRequest(title="Updated Task"),
                user_id=10,
            )

    assert result.title == "Updated Task"
    service.task_repository.update_task.assert_called_once()
    invalidate_mock.assert_called_once_with(1)


def test_update_task_success_when_assignee(service):
    updated_task = make_task(created_by=10, assignee_id=20)
    updated_task.status = "done"
    service.task_repository.get_task = Mock(return_value=make_task(created_by=10, assignee_id=20))
    service.task_repository.update_task = Mock(return_value=updated_task)

    with patch.object(service, "_can_access_project", return_value=True):
        with patch.object(service, "_invalidate_task_cache") as invalidate_mock:
            result = service.update_task(
                1,
                TaskUpdateRequest(status="done"),
                user_id=20,
            )

    assert result.status == "done"
    invalidate_mock.assert_called_once_with(1)


def test_update_task_success_when_project_owner(service):
    updated_task = make_task(created_by=10, assignee_id=20)
    updated_task.priority = "high"
    service.task_repository.get_task = Mock(return_value=make_task(created_by=10, assignee_id=20))
    service.task_repository.update_task = Mock(return_value=updated_task)

    with patch.object(service, "_can_access_project", return_value=True):
        with patch.object(service, "_is_project_owner", return_value=True):
            with patch.object(service, "_invalidate_task_cache") as invalidate_mock:
                result = service.update_task(
                    1,
                    TaskUpdateRequest(priority="high"),
                    user_id=30,
                )

    assert result.priority == "high"
    invalidate_mock.assert_called_once_with(1)


def test_update_task_not_found(service):
    service.task_repository.get_task = Mock(return_value=None)

    with pytest.raises(ValueError, match="Task not found"):
        service.update_task(999, TaskUpdateRequest(title="Updated Task"), user_id=10)


def test_update_task_denies_access(service):
    service.task_repository.get_task = Mock(return_value=make_task())
    service.task_repository.update_task = Mock()

    with patch.object(service, "_can_access_project", return_value=False):
        with pytest.raises(ValueError, match="Access denied"):
            service.update_task(1, TaskUpdateRequest(title="Updated Task"), user_id=99)

    service.task_repository.update_task.assert_not_called()


def test_update_task_denies_user_without_modify_permission(service):
    service.task_repository.get_task = Mock(return_value=make_task(created_by=10, assignee_id=20))
    service.task_repository.update_task = Mock()

    with patch.object(service, "_can_access_project", return_value=True):
        with patch.object(service, "_is_project_owner", return_value=False):
            with pytest.raises(ValueError, match="Permission denied"):
                service.update_task(1, TaskUpdateRequest(title="Updated Task"), user_id=30)

    service.task_repository.update_task.assert_not_called()


def test_delete_task_success_when_creator(service):
    service.task_repository.get_task = Mock(return_value=make_task(created_by=10))
    service.task_repository.delete_task = Mock(return_value=True)

    with patch.object(service, "_can_access_project", return_value=True):
        with patch.object(service, "_invalidate_task_cache") as invalidate_mock:
            result = service.delete_task(task_id=1, user_id=10)

    assert result is True
    service.task_repository.delete_task.assert_called_once_with(1)
    invalidate_mock.assert_called_once_with(1)


def test_delete_task_success_when_project_owner(service):
    service.task_repository.get_task = Mock(return_value=make_task(created_by=10))
    service.task_repository.delete_task = Mock(return_value=True)

    with patch.object(service, "_can_access_project", return_value=True):
        with patch.object(service, "_is_project_owner", return_value=True):
            with patch.object(service, "_invalidate_task_cache") as invalidate_mock:
                result = service.delete_task(task_id=1, user_id=30)

    assert result is True
    service.task_repository.delete_task.assert_called_once_with(1)
    invalidate_mock.assert_called_once_with(1)


def test_delete_task_not_found(service):
    service.task_repository.get_task = Mock(return_value=None)

    with pytest.raises(ValueError, match="Task not found"):
        service.delete_task(task_id=999, user_id=10)


def test_delete_task_denies_access(service):
    service.task_repository.get_task = Mock(return_value=make_task())
    service.task_repository.delete_task = Mock()

    with patch.object(service, "_can_access_project", return_value=False):
        with pytest.raises(ValueError, match="Access denied"):
            service.delete_task(task_id=1, user_id=99)

    service.task_repository.delete_task.assert_not_called()


def test_delete_task_denies_user_without_permission(service):
    service.task_repository.get_task = Mock(return_value=make_task(created_by=10))
    service.task_repository.delete_task = Mock()

    with patch.object(service, "_can_access_project", return_value=True):
        with patch.object(service, "_is_project_owner", return_value=False):
            with pytest.raises(ValueError, match="Permission denied"):
                service.delete_task(task_id=1, user_id=30)

    service.task_repository.delete_task.assert_not_called()


def test_can_access_project_returns_true_for_owner(service):
    service.project_member_repository.is_user_in_project = Mock()

    with patch("app.repositories.project_responsitory.ProjectRepository") as project_repository_mock:
        project_repository_mock.return_value.get_project.return_value = make_project(owner_id=10)

        result = service._can_access_project(project_id=1, user_id=10)

    assert result is True
    service.project_member_repository.is_user_in_project.assert_not_called()


def test_can_access_project_checks_membership_for_non_owner(service):
    service.project_member_repository.is_user_in_project = Mock(return_value=True)

    with patch("app.repositories.project_responsitory.ProjectRepository") as project_repository_mock:
        project_repository_mock.return_value.get_project.return_value = make_project(owner_id=10)

        result = service._can_access_project(project_id=1, user_id=20)

    assert result is True
    service.project_member_repository.is_user_in_project.assert_called_once_with(1, 20)


def test_is_project_owner_returns_true_for_project_owner(service):
    service.project_member_repository.get_project_member_by_user = Mock()

    with patch("app.repositories.project_responsitory.ProjectRepository") as project_repository_mock:
        project_repository_mock.return_value.get_project.return_value = make_project(owner_id=10)

        result = service._is_project_owner(project_id=1, user_id=10)

    assert result is True
    service.project_member_repository.get_project_member_by_user.assert_not_called()


def test_is_project_owner_returns_true_for_owner_member(service):
    service.project_member_repository.get_project_member_by_user = Mock(
        return_value=make_project_member(project_id=1, user_id=20, role="owner")
    )

    with patch("app.repositories.project_responsitory.ProjectRepository") as project_repository_mock:
        project_repository_mock.return_value.get_project.return_value = make_project(owner_id=10)

        result = service._is_project_owner(project_id=1, user_id=20)

    assert result is True
    service.project_member_repository.get_project_member_by_user.assert_called_once_with(1, 20)
