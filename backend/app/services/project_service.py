import json
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from app.models.projects import Project
from app.schemas.project import ProjectResponse, ProjectCreateRequest, ProjectUpdateRequest
from app.repositories.project_responsitory import ProjectRepository
from app.repositories.project_member_responsitory import ProjectMemberRepository
from app.core.cache import redis_client
from fastapi.encoders import jsonable_encoder


class ProjectService:
    def __init__(self, db: Session):
        self.db = db
        self.project_repository = ProjectRepository(db)
        self.project_member_repository = ProjectMemberRepository(db)

    def _project_cache_key(self, project_id: int) -> str:
        return f"project:{project_id}"

    def _projects_cache_key(self, owner_id: int, skip: int, limit: int) -> str:
        return f"projects:owner:{owner_id}:{skip}:{limit}"

    def _invalidate_project_cache(self, project_id: int):
        redis_client.delete(self._project_cache_key(project_id))
        keys = redis_client.keys("projects:*")
        for key in keys:
            redis_client.delete(key)

    def get_project(self, project_id: int, user_id: int = None) -> Optional[ProjectResponse]:
        # Check if user has access to project
        if user_id and not self._can_access_project(project_id, user_id):
            raise ValueError("Access denied")

        cache_key = self._project_cache_key(project_id)
        cached_project = redis_client.get(cache_key)
        if cached_project:
            project_data = json.loads(cached_project)
            return ProjectResponse.model_validate(project_data)

        project = self.project_repository.get_project(project_id)
        if not project:
            return None

        project_response = ProjectResponse.model_validate(project)
        redis_client.setex(cache_key, 300, json.dumps(jsonable_encoder(project_response)))
        return project_response

    def get_projects_by_owner(self, owner_id: int, skip: int = 0, limit: int = 100) -> List[ProjectResponse]:
        cache_key = self._projects_cache_key(owner_id, skip, limit)
        cached_projects = redis_client.get(cache_key)
        if cached_projects:
            projects_data = json.loads(cached_projects)
            return [ProjectResponse.model_validate(item) for item in projects_data]

        projects = self.project_repository.get_projects_by_owner(owner_id, skip, limit)
        project_responses = [ProjectResponse.model_validate(project) for project in projects]
        redis_client.setex(cache_key, 300, json.dumps(jsonable_encoder(project_responses)))
        return project_responses

    def get_user_projects(self, user_id: int, skip: int = 0, limit: int = 100) -> List[ProjectResponse]:
        # Get projects where user is a member
        members = self.project_member_repository.get_user_projects(user_id)
        project_ids = [member.project_id for member in members]

        projects = []
        for project_id in project_ids[skip:skip + limit]:
            project = self.project_repository.get_project(project_id)
            if project:
                projects.append(project)

        return [ProjectResponse.model_validate(project) for project in projects]

    def get_projects_by_filters(
        self,
        user_id: int,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ProjectResponse]:
        projects = self.project_repository.get_accessible_projects_by_filters(
            user_id=user_id,
            status=status,
            priority=priority,
            due_date=due_date,
            skip=skip,
            limit=limit
        )
        return [ProjectResponse.model_validate(project) for project in projects]

    def create_project(self, project_data: ProjectCreateRequest, owner_id: int) -> ProjectResponse:
        project = self.project_repository.create_project(project_data, owner_id)
        if project and project.id:
            self._invalidate_project_cache(project.id)
        return ProjectResponse.model_validate(project)

    def update_project(self, project_id: int, project_update: ProjectUpdateRequest, user_id: int) -> Optional[ProjectResponse]:
        # Check if user can update project (owner or admin)
        if not self._can_modify_project(project_id, user_id):
            raise ValueError("Permission denied")

        updated = self.project_repository.update_project(project_id, project_update)
        if updated:
            self._invalidate_project_cache(project_id)
        return ProjectResponse.model_validate(updated) if updated else None

    def delete_project(self, project_id: int, user_id: int) -> bool:
        # Check if user is owner
        project = self.project_repository.get_project(project_id)
        if not project or project.owner_id != user_id:
            raise ValueError("Only project owner can delete project")

        success = self.project_repository.delete_project(project_id)
        if success:
            self._invalidate_project_cache(project_id)
        return success

    def _can_access_project(self, project_id: int, user_id: int) -> bool:
        project = self.project_repository.get_project(project_id)
        if project and project.owner_id == user_id:
            return True
        return self.project_member_repository.is_user_in_project(project_id, user_id)

    def _can_modify_project(self, project_id: int, user_id: int) -> bool:
        project = self.project_repository.get_project(project_id)
        if project and project.owner_id == user_id:
            return True

        member = self.project_member_repository.get_project_members(project_id)
        user_member = next((m for m in member if m.user_id == user_id), None)
        return user_member and user_member.role == "admin"
