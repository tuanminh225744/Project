from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.models.project_members import ProjectMember
from app.schemas.project_member import ProjectMemberCreateRequest, ProjectMemberUpdateRequest


class ProjectMemberRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_project_member(self, member_id: int) -> Optional[ProjectMember]:
        return self.db.query(ProjectMember).options(
                joinedload(ProjectMember.user),
            ).filter(ProjectMember.id == member_id).first()

    def get_project_members(self, project_id: int) -> List[ProjectMember]:
        return self.db.query(ProjectMember).options(
                joinedload(ProjectMember.user),
            ).filter(ProjectMember.project_id == project_id).all()

    def get_project_member_by_user(self, project_id: int, user_id: int) -> Optional[ProjectMember]:
        return self.db.query(ProjectMember).options(
                joinedload(ProjectMember.user),
            ).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id
        ).first()

    def get_user_projects(self, user_id: int) -> List[ProjectMember]:
        return self.db.query(ProjectMember).options(
                joinedload(ProjectMember.user),
            ).filter(ProjectMember.user_id == user_id).all()

    def is_user_in_project(self, project_id: int, user_id: int) -> bool:
        return self.get_project_member_by_user(project_id, user_id) is not None

    def create_project_member(self, member_data: ProjectMemberCreateRequest) -> ProjectMember:
        member = ProjectMember(
            project_id=member_data.project_id,
            user_id=member_data.user_id,
            role=member_data.role
        )
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member

    def update_project_member(self, member_id: int, member_update: ProjectMemberUpdateRequest) -> Optional[ProjectMember]:
        db_member = self.get_project_member(member_id)
        if db_member:
            update_data = member_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_member, field, value)
            self.db.commit()
            self.db.refresh(db_member)
        return db_member

    def delete_project_member(self, member_id: int) -> bool:
        db_member = self.get_project_member(member_id)
        if db_member:
            self.db.delete(db_member)
            self.db.commit()
            return True
        return False

    def remove_user_from_project(self, project_id: int, user_id: int) -> bool:
        db_member = self.get_project_member_by_user(project_id, user_id)
        if db_member:
            self.db.delete(db_member)
            self.db.commit()
            return True
        return False
