from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.task_comments import TaskComment
from app.models.tasks import Task
from app.schemas.task_comment import TaskCommentResponse, TaskCommentCreateRequest, TaskCommentUpdateRequest
from app.repositories.task_comment_responsitory import TaskCommentRepository
from app.repositories.task_responsitory import TaskRepository


class TaskCommentService:
    def __init__(self, db: Session):
        self.db = db
        self.task_comment_repository = TaskCommentRepository(db)
        self.task_repository = TaskRepository(db)

    def get_task_comments(self, task_id: int, user_id: int, skip: int = 0, limit: int = 100) -> List[TaskCommentResponse]:
        # Check if user can access the task's project
        task = self.task_repository.get_task(task_id)
        if not task:
            raise ValueError("Task not found")

        if not self._can_access_task(task, user_id):
            raise ValueError("Access denied")

        comments = self.task_comment_repository.get_task_comments(task_id, skip, limit)
        return [TaskCommentResponse.model_validate(comment) for comment in comments]

    def create_comment(self, comment_data: TaskCommentCreateRequest, user_id: int) -> TaskCommentResponse:
        # Check if user can access the task
        task = self.task_repository.get_task(comment_data.task_id)
        if not task:
            raise ValueError("Task not found")

        if not self._can_access_task(task, user_id):
            raise ValueError("Access denied")

        # Set user_id to the commenter
        comment_data.user_id = user_id

        comment = self.task_comment_repository.create_task_comment(comment_data)
        return TaskCommentResponse.model_validate(comment)

    def update_comment(self, comment_id: int, comment_update: TaskCommentUpdateRequest, user_id: int) -> Optional[TaskCommentResponse]:
        comment = self.task_comment_repository.get_task_comment(comment_id)
        if not comment:
            raise ValueError("Comment not found")

        # Check if user can access the task
        task = self.task_repository.get_task(comment.task_id)
        if not task or not self._can_access_task(task, user_id):
            raise ValueError("Access denied")

        # Only comment author can update
        if comment.user_id != user_id:
            raise ValueError("Permission denied")

        updated = self.task_comment_repository.update_task_comment(comment_id, comment_update)
        return TaskCommentResponse.model_validate(updated) if updated else None

    def delete_comment(self, comment_id: int, user_id: int) -> bool:
        comment = self.task_comment_repository.get_task_comment(comment_id)
        if not comment:
            raise ValueError("Comment not found")

        # Check if user can access the task
        task = self.task_repository.get_task(comment.task_id)
        if not task or not self._can_access_task(task, user_id):
            raise ValueError("Access denied")

        # Comment author or task creator or project admin can delete
        can_delete = (
            comment.user_id == user_id or  # Author
            task.created_by == user_id or  # Task creator
            self._is_project_admin(task.project_id, user_id)  # Project admin
        )

        if not can_delete:
            raise ValueError("Permission denied")

        return self.task_comment_repository.delete_task_comment(comment_id)

    def _can_access_task(self, task: Task, user_id: int) -> bool:
        """Check if user can access the task's project"""
        from app.repositories.project_member_responsitory import ProjectMemberRepository
        from app.repositories.project_responsitory import ProjectRepository

        project_repo = ProjectRepository(self.db)
        member_repo = ProjectMemberRepository(self.db)

        project = project_repo.get_project(task.project_id)
        if project and project.owner_id == user_id:
            return True
        return member_repo.is_user_in_project(task.project_id, user_id)

    def _is_project_admin(self, project_id: int, user_id: int) -> bool:
        """Check if user is project admin"""
        from app.repositories.project_responsitory import ProjectRepository
        from app.repositories.project_member_responsitory import ProjectMemberRepository

        project_repo = ProjectRepository(self.db)
        member_repo = ProjectMemberRepository(self.db)

        project = project_repo.get_project(project_id)
        if project and project.owner_id == user_id:
            return True

        members = member_repo.get_project_members(project_id)
        user_member = next((m for m in members if m.user_id == user_id), None)
        return user_member and user_member.role == "admin"