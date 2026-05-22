import json
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.tasks import Task
from app.schemas.task_schema import TaskResponse, TaskCreateRequest, TaskUpdateRequest
from app.repositories.task_responsitory import TaskRepository
from app.repositories.project_member_responsitory import ProjectMemberRepository
from app.core.cache import redis_client
from fastapi.encoders import jsonable_encoder


class TaskService:
    def __init__(self, db: Session):
        self.db = db
        self.task_repository = TaskRepository(db)
        self.project_member_repository = ProjectMemberRepository(db)

    def _task_cache_key(self, task_id: int) -> str:
        return f"task:{task_id}"

    def _tasks_cache_key(self, project_id: int, skip: int, limit: int) -> str:
        return f"tasks:project:{project_id}:{skip}:{limit}"

    def _invalidate_task_cache(self, task_id: int):
        redis_client.delete(self._task_cache_key(task_id))
        keys = redis_client.keys("tasks:*")
        for key in keys:
            redis_client.delete(key)

    def get_task(self, task_id: int, user_id: int) -> Optional[TaskResponse]:
        task = self.task_repository.get_task(task_id)
        if not task:
            return None

        # Check if user can access the project
        if not self._can_access_project(task.project_id, user_id):
            raise ValueError("Access denied")

        cache_key = self._task_cache_key(task_id)
        cached_task = redis_client.get(cache_key)
        if cached_task:
            task_data = json.loads(cached_task)
            return TaskResponse.model_validate(task_data)

        task_response = TaskResponse.model_validate(task)
        redis_client.setex(cache_key, 300, json.dumps(jsonable_encoder(task_response)))
        return task_response

    def get_tasks_by_project(self, project_id: int, user_id: int, skip: int = 0, limit: int = 100) -> List[TaskResponse]:
        # Check if user can access the project
        if not self._can_access_project(project_id, user_id):
            raise ValueError("Access denied")

        cache_key = self._tasks_cache_key(project_id, skip, limit)
        cached_tasks = redis_client.get(cache_key)
        if cached_tasks:
            tasks_data = json.loads(cached_tasks)
            return [TaskResponse.model_validate(item) for item in tasks_data]

        tasks = self.task_repository.get_tasks_by_project(project_id, skip, limit)
        task_responses = [TaskResponse.model_validate(task) for task in tasks]
        redis_client.setex(cache_key, 300, json.dumps(jsonable_encoder(task_responses)))
        return task_responses

    def get_tasks_by_assignee(self, assignee_id: int, user_id: int, skip: int = 0, limit: int = 100) -> List[TaskResponse]:
        # User can only see tasks assigned to themselves or if they have access to the projects
        if assignee_id != user_id:
            raise ValueError("Access denied")

        tasks = self.task_repository.get_tasks_by_assignee(assignee_id, skip, limit)
        # Filter tasks where user has access to the project
        accessible_tasks = []
        for task in tasks:
            if self._can_access_project(task.project_id, user_id):
                accessible_tasks.append(task)

        return [TaskResponse.model_validate(task) for task in accessible_tasks]

    def get_my_tasks(self, user_id: int, skip: int = 0, limit: int = 100) -> List[TaskResponse]:
        # Get tasks created by user or assigned to user
        created_tasks = self.task_repository.get_tasks_by_creator(user_id, skip, limit)
        assigned_tasks = self.task_repository.get_tasks_by_assignee(user_id, skip, limit)

        # Combine and deduplicate
        all_tasks = list(set(created_tasks + assigned_tasks))

        # Filter by project access
        accessible_tasks = []
        for task in all_tasks:
            if self._can_access_project(task.project_id, user_id):
                accessible_tasks.append(task)

        return [TaskResponse.model_validate(task) for task in accessible_tasks[skip:skip + limit]]

    def get_tasks_by_filters(
        self,
        user_id: int,
        status: Optional[str] = None,
        assignee_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[TaskResponse]:
        tasks = self.task_repository.get_accessible_tasks_by_filters(
            user_id=user_id,
            status=status,
            assignee_id=assignee_id,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit
        )
        return [TaskResponse.model_validate(task) for task in tasks]

    def create_task(self, task_data: TaskCreateRequest, creator_id: int) -> TaskResponse:
        # Check if user can access the project
        if not self._can_access_project(task_data.project_id, creator_id):
            raise ValueError("Access denied")

        # Always trust the authenticated user, not client-provided created_by.
        task_data.created_by = creator_id

        task = self.task_repository.create_task(task_data)
        return TaskResponse.model_validate(task)

    def update_task(self, task_id: int, task_update: TaskUpdateRequest, user_id: int) -> Optional[TaskResponse]:
        task = self.task_repository.get_task(task_id)
        if not task:
            raise ValueError("Task not found")

        # Check if user can access the project
        if not self._can_access_project(task.project_id, user_id):
            raise ValueError("Access denied")

        # Check if user can modify the task
        if not self._can_modify_task(task, user_id):
            raise ValueError("Permission denied")

        updated = self.task_repository.update_task(task_id, task_update)
        if updated:
            self._invalidate_task_cache(task_id)
        return TaskResponse.model_validate(updated) if updated else None

    def delete_task(self, task_id: int, user_id: int) -> bool:
        task = self.task_repository.get_task(task_id)
        if not task:
            raise ValueError("Task not found")

        # Check if user can access the project
        if not self._can_access_project(task.project_id, user_id):
            raise ValueError("Access denied")

        # Only creator or project owner can delete
        if task.created_by != user_id and not self._is_project_owner(task.project_id, user_id):
            raise ValueError("Permission denied")

        success = self.task_repository.delete_task(task_id)
        if success:
            self._invalidate_task_cache(task_id)
        return success

    def _can_access_project(self, project_id: int, user_id: int) -> bool:
        """Check if user can access the project"""
        from app.repositories.project_responsitory import ProjectRepository
        project_repo = ProjectRepository(self.db)
        project = project_repo.get_project(project_id)
        if project and project.owner_id == user_id:
            return True
        return self.project_member_repository.is_user_in_project(project_id, user_id)

    def _can_modify_task(self, task: Task, user_id: int) -> bool:
        """Check if user can modify the task"""
        # Creator can always modify
        if task.created_by == user_id:
            return True
        # Assignee can modify
        if task.assignee_id == user_id:
            return True
        # Project owner can modify
        return self._is_project_owner(task.project_id, user_id)

    def _is_project_owner(self, project_id: int, user_id: int) -> bool:
        """Check if user is project owner"""
        from app.repositories.project_responsitory import ProjectRepository
        project_repo = ProjectRepository(self.db)
        project = project_repo.get_project(project_id)
        if project and project.owner_id == user_id:
            return True

        user_member = self.project_member_repository.get_project_member_by_user(project_id, user_id)
        return bool(user_member and user_member.role == "owner")
