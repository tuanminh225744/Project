from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.project_members import ProjectMember
from app.schemas.project_member import ProjectMemberResponse, ProjectMemberCreateRequest, ProjectMemberUpdateRequest
from app.repositories.project_member_responsitory import ProjectMemberRepository
from app.repositories.project_responsitory import ProjectRepository


class ProjectMemberService:
    def __init__(self, db: Session):
        self.db = db
        self.project_member_repository = ProjectMemberRepository(db)
        self.project_repository = ProjectRepository(db)

    def get_project_members(self, project_id: int, user_id: int) -> List[ProjectMemberResponse]:
        # Check if user can access project
        if not self._can_access_project(project_id, user_id):
            raise ValueError("Access denied")

        members = self.project_member_repository.get_project_members(project_id)
        return [ProjectMemberResponse.model_validate(member) for member in members]

    def add_member_to_project(self, member_data: ProjectMemberCreateRequest, requester_id: int) -> ProjectMemberResponse:
        # Check if requester can add members
        if not self._can_modify_members(member_data.project_id, requester_id):
            raise ValueError("Permission denied")

        # Check if user is already a member
        if self.project_member_repository.is_user_in_project(member_data.project_id, member_data.user_id):
            raise ValueError("User is already a member of this project")

        member = self.project_member_repository.create_project_member(member_data)
        return ProjectMemberResponse.model_validate(member)

    def update_member_role(self, member_id: int, member_update: ProjectMemberUpdateRequest, requester_id: int) -> Optional[ProjectMemberResponse]:
        member = self.project_member_repository.get_project_member(member_id)
        if not member:
            raise ValueError("Member not found")

        # Check if requester can update members
        if not self._can_modify_members(member.project_id, requester_id):
            raise ValueError("Permission denied")

        updated = self.project_member_repository.update_project_member(member_id, member_update)
        return ProjectMemberResponse.model_validate(updated) if updated else None

    def remove_member_from_project(self, project_id: int, user_id: int, requester_id: int) -> bool:
        # Check if requester can remove members
        if not self._can_modify_members(project_id, requester_id):
            raise ValueError("Permission denied")

        # Cannot remove owner
        project = self.project_repository.get_project(project_id)
        if project and project.owner_id == user_id:
            raise ValueError("Cannot remove project owner")

        return self.project_member_repository.remove_user_from_project(project_id, user_id)

    def leave_project(self, project_id: int, user_id: int) -> bool:
        # Check if user is owner (owner cannot leave, must delete project)
        project = self.project_repository.get_project(project_id)
        if project and project.owner_id == user_id:
            raise ValueError("Project owner cannot leave project. Delete project instead.")

        return self.project_member_repository.remove_user_from_project(project_id, user_id)

    def _can_access_project(self, project_id: int, user_id: int) -> bool:
        """Check if user can access the project"""
        project = self.project_repository.get_project(project_id)
        if project and project.owner_id == user_id:
            return True
        return self.project_member_repository.is_user_in_project(project_id, user_id)

    def _can_modify_members(self, project_id: int, user_id: int) -> bool:
        project = self.project_repository.get_project(project_id)
        if project and project.owner_id == user_id:
            return True

        user_member = self.project_member_repository.get_project_member_by_user(project_id, user_id)
        return bool(user_member and user_member.role == "owner")
