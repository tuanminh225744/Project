from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional
from app.db.base import get_db
from app.services.project_service import ProjectService
from app.schemas.project import ProjectResponse, ProjectCreateRequest, ProjectUpdateRequest
from app.core.deps import get_current_user

router = APIRouter(
    prefix="/projects",
    tags=["projects"]
)

@router.post("/", response_model=ProjectResponse)
def create_project(
    project: ProjectCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    project_service = ProjectService(db)
    try:
        return project_service.create_project(project, current_user["user_id"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[ProjectResponse])
def read_user_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    project_service = ProjectService(db)
    try:
        return project_service.get_user_projects(current_user["user_id"], skip, limit)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.get("/owned", response_model=List[ProjectResponse])
def read_owned_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    project_service = ProjectService(db)
    return project_service.get_projects_by_owner(current_user["user_id"], skip, limit)

@router.get("/search", response_model=List[ProjectResponse])
def search_projects(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    project_service = ProjectService(db)
    try:
        return project_service.get_projects_by_filters(
            user_id=current_user["user_id"],
            status=status,
            priority=priority,
            due_date=due_date,
            skip=skip,
            limit=limit
        )
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.get("/{project_id}", response_model=ProjectResponse)
def read_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    project_service = ProjectService(db)
    try:
        db_project = project_service.get_project(project_id, current_user["user_id"])
        if db_project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        return db_project
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project: ProjectUpdateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    project_service = ProjectService(db)
    try:
        db_project = project_service.update_project(project_id, project, current_user["user_id"])
        if db_project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        return db_project
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    project_service = ProjectService(db)
    try:
        success = project_service.delete_project(project_id, current_user["user_id"])
        if not success:
            raise HTTPException(status_code=404, detail="Project not found")
        return {"message": "Project deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
