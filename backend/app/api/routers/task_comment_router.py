from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.base import get_db
from app.services.task_comment_service import TaskCommentService
from app.schemas.task_comment import TaskCommentResponse, TaskCommentCreateRequest, TaskCommentUpdateRequest
from app.core.deps import get_current_user

router = APIRouter(
    prefix="/tasks/{task_id}/comments",
    tags=["task-comments"]
)

@router.get("/", response_model=List[TaskCommentResponse])
def read_task_comments(
    task_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    comment_service = TaskCommentService(db)
    try:
        return comment_service.get_task_comments(task_id, current_user["user_id"], skip, limit)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.post("/", response_model=TaskCommentResponse)
def create_comment(
    task_id: int,
    comment: TaskCommentCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Ensure the task_id in URL matches the one in request
    if comment.task_id != task_id:
        raise HTTPException(status_code=400, detail="Task ID mismatch")

    comment_service = TaskCommentService(db)
    try:
        return comment_service.create_comment(comment, current_user["user_id"])
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.put("/{comment_id}", response_model=TaskCommentResponse)
def update_comment(
    task_id: int,
    comment_id: int,
    comment: TaskCommentUpdateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    comment_service = TaskCommentService(db)
    try:
        db_comment = comment_service.update_comment(comment_id, comment, current_user["user_id"])
        if db_comment is None:
            raise HTTPException(status_code=404, detail="Comment not found")
        return db_comment
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.delete("/{comment_id}")
def delete_comment(
    task_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    comment_service = TaskCommentService(db)
    try:
        success = comment_service.delete_comment(comment_id, current_user["user_id"])
        if not success:
            raise HTTPException(status_code=404, detail="Comment not found")
        return {"message": "Comment deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))