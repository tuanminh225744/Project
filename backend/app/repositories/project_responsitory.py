from sqlalchemy.orm import Session
from sqlalchemy import and_, func, or_
from typing import List, Optional
from datetime import date
from app.models.project_members import ProjectMember
from app.models.projects import Project
from app.schemas.project import ProjectCreateRequest, ProjectUpdateRequest


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_project(self, project_id: int) -> Optional[Project]:
        return self.db.query(Project).filter(Project.id == project_id).first()

    def get_projects(self, skip: int = 0, limit: int = 100) -> List[Project]:
        return self.db.query(Project).offset(skip).limit(limit).all()

    def get_projects_by_owner(self, owner_id: int, skip: int = 0, limit: int = 100) -> List[Project]:
        return self.db.query(Project).filter(Project.owner_id == owner_id).offset(skip).limit(limit).all()

    def get_accessible_projects_by_filters(
        self,
        user_id: int,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Project]:
        query = self.db.query(Project).outerjoin(
            ProjectMember,
            and_(
                ProjectMember.project_id == Project.id,
                ProjectMember.user_id == user_id
            )
        ).filter(
            or_(
                Project.owner_id == user_id,
                ProjectMember.user_id == user_id
            )
        )

        if status is not None:
            query = query.filter(Project.status == status)
        if priority is not None:
            query = query.filter(Project.priority == priority)
        if due_date is not None:
            query = query.filter(func.date(Project.due_date) == due_date)

        return query.distinct().offset(skip).limit(limit).all()

    def create_project(self, project_data: ProjectCreateRequest, owner_id: int) -> Project:
        project = Project(
            name=project_data.name,
            description=project_data.description,
            status=project_data.status,
            priority=project_data.priority,
            due_date=project_data.due_date,
            owner_id=owner_id
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def update_project(self, project_id: int, project_update: ProjectUpdateRequest) -> Optional[Project]:
        db_project = self.get_project(project_id)
        if db_project:
            update_data = project_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_project, field, value)
            self.db.commit()
            self.db.refresh(db_project)
        return db_project

    def delete_project(self, project_id: int) -> bool:
        db_project = self.get_project(project_id)
        if db_project:
            self.db.delete(db_project)
            self.db.commit()
            return True
        return False
