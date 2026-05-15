from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.task_comments import TaskComment
from app.schemas.task_comment import TaskCommentCreateRequest, TaskCommentUpdateRequest


class TaskCommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_task_comment(self, comment_id: int) -> Optional[TaskComment]:
        return self.db.query(TaskComment).filter(TaskComment.id == comment_id).first()

    def get_task_comments(self, task_id: int, skip: int = 0, limit: int = 100) -> List[TaskComment]:
        return self.db.query(TaskComment).filter(TaskComment.task_id == task_id).offset(skip).limit(limit).all()

    def get_comments_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[TaskComment]:
        return self.db.query(TaskComment).filter(TaskComment.user_id == user_id).offset(skip).limit(limit).all()

    def create_task_comment(self, comment_data: TaskCommentCreateRequest) -> TaskComment:
        comment = TaskComment(
            task_id=comment_data.task_id,
            user_id=comment_data.user_id,
            content=comment_data.content
        )
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def update_task_comment(self, comment_id: int, comment_update: TaskCommentUpdateRequest) -> Optional[TaskComment]:
        db_comment = self.get_task_comment(comment_id)
        if db_comment:
            update_data = comment_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_comment, field, value)
            self.db.commit()
            self.db.refresh(db_comment)
        return db_comment

    def delete_task_comment(self, comment_id: int) -> bool:
        db_comment = self.get_task_comment(comment_id)
        if db_comment:
            self.db.delete(db_comment)
            self.db.commit()
            return True
        return False