from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.base import get_db
from app.services.task_service import TaskService
from app.schemas.task_schema import TaskResponse, TaskCreateRequest, TaskUpdateRequest
from app.core.deps import get_current_user

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)

@router.post("/", response_model=TaskResponse)
def create_task(
    task: TaskCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    task_service = TaskService(db)
    try:
        return task_service.create_task(task, current_user["user_id"])
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.get("/", response_model=List[TaskResponse])
def read_my_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    task_service = TaskService(db)
    return task_service.get_my_tasks(current_user["user_id"], skip, limit)

@router.get("/assigned", response_model=List[TaskResponse])
def read_assigned_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    task_service = TaskService(db)
    try:
        return task_service.get_tasks_by_assignee(current_user["user_id"], current_user["user_id"], skip, limit)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.get("/project/{project_id}", response_model=List[TaskResponse])
def read_project_tasks(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    task_service = TaskService(db)
    try:
        return task_service.get_tasks_by_project(project_id, current_user["user_id"], skip, limit)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.get("/{task_id}", response_model=TaskResponse)
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    task_service = TaskService(db)
    try:
        db_task = task_service.get_task(task_id, current_user["user_id"])
        if db_task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return db_task
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task: TaskUpdateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    task_service = TaskService(db)
    try:
        db_task = task_service.update_task(task_id, task, current_user["user_id"])
        if db_task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return db_task
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    task_service = TaskService(db)
    try:
        success = task_service.delete_task(task_id, current_user["user_id"])
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"message": "Task deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))