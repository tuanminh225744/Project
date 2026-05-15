from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class TaskCommentBase(BaseModel):
    content: str


class TaskCommentCreateRequest(TaskCommentBase):
    task_id: int
    user_id: int


class TaskCommentUpdateRequest(BaseModel):
    content: Optional[str] = None


class TaskCommentResponse(TaskCommentBase):
    id: int
    task_id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(
        from_attributes=True
    )