from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models.tasks import Task
from app.models.project_members import ProjectMember
from app.models.projects import Project
from app.schemas.task_schema import TaskCreateRequest, TaskUpdateRequest
from sqlalchemy import and_, or_


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_task(self, task_id: int) -> Optional[Task]:
        return self.db.query(Task).filter(Task.id == task_id).first()

    def get_tasks(self, skip: int = 0, limit: int = 100) -> List[Task]:
        return self.db.query(Task).offset(skip).limit(limit).all()

    def get_tasks_by_project(self, project_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        return self.db.query(Task).filter(Task.project_id == project_id).offset(skip).limit(limit).all()

    def get_tasks_by_assignee(self, assignee_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        return self.db.query(Task).filter(Task.assignee_id == assignee_id).offset(skip).limit(limit).all()

    def get_tasks_by_creator(self, creator_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        return self.db.query(Task).filter(Task.created_by == creator_id).offset(skip).limit(limit).all()

    def get_accessible_tasks_by_filters(
        self,
        user_id: int,
        status: Optional[str] = None,
        assignee_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        query = self.db.query(Task).join(
            Project,
            Project.id == Task.project_id
        ).outerjoin(
            ProjectMember,
            and_(
                ProjectMember.project_id == Task.project_id,
                ProjectMember.user_id == user_id
            )
        ).filter(
            or_(
                Project.owner_id == user_id,
                Task.created_by == user_id,
                Task.assignee_id == user_id,
                ProjectMember.user_id == user_id
            )
        )

        if status is not None:
            query = query.filter(Task.status == status)
        if assignee_id is not None:
            query = query.filter(Task.assignee_id == assignee_id)
        if start_date is not None:
            query = query.filter(Task.due_date >= start_date)
        if end_date is not None:
            query = query.filter(Task.due_date <= end_date)

        return query.distinct().offset(skip).limit(limit).all()

    def create_task(self, task_data: TaskCreateRequest) -> Task:
        task = Task(
            project_id=task_data.project_id,
            title=task_data.title,
            description=task_data.description,
            status=task_data.status,
            priority=task_data.priority,
            assignee_id=task_data.assignee_id,
            created_by=task_data.created_by,
            due_date=task_data.due_date
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update_task(self, task_id: int, task_update: TaskUpdateRequest) -> Optional[Task]:
        db_task = self.get_task(task_id)
        if db_task:
            update_data = task_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_task, field, value)
            self.db.commit()
            self.db.refresh(db_task)
        return db_task

    def delete_task(self, task_id: int) -> bool:
        db_task = self.get_task(task_id)
        if db_task:
            self.db.delete(db_task)
            self.db.commit()
            return True
        return False
