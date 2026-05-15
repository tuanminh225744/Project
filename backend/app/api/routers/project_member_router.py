from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.base import get_db
from app.services.project_member_service import ProjectMemberService
from app.schemas.project_member import ProjectMemberResponse, ProjectMemberCreateRequest, ProjectMemberUpdateRequest
from app.core.deps import get_current_user

router = APIRouter(
    prefix="/projects/{project_id}/members",
    tags=["project-members"]
)

@router.get("/", response_model=List[ProjectMemberResponse])
def read_project_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    member_service = ProjectMemberService(db)
    try:
        return member_service.get_project_members(project_id, current_user["user_id"])
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.post("/", response_model=ProjectMemberResponse)
def add_project_member(
    project_id: int,
    member: ProjectMemberCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Ensure the project_id in URL matches the one in request
    if member.project_id != project_id:
        raise HTTPException(status_code=400, detail="Project ID mismatch")

    member_service = ProjectMemberService(db)
    try:
        return member_service.add_member_to_project(member, current_user["user_id"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{member_id}", response_model=ProjectMemberResponse)
def update_project_member(
    project_id: int,
    member_id: int,
    member: ProjectMemberUpdateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    member_service = ProjectMemberService(db)
    try:
        db_member = member_service.update_member_role(member_id, member, current_user["user_id"])
        if db_member is None:
            raise HTTPException(status_code=404, detail="Member not found")
        return db_member
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.delete("/{user_id}")
def remove_project_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    member_service = ProjectMemberService(db)
    try:
        success = member_service.remove_member_from_project(project_id, user_id, current_user["user_id"])
        if not success:
            raise HTTPException(status_code=404, detail="Member not found")
        return {"message": "Member removed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.delete("/leave")
def leave_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    member_service = ProjectMemberService(db)
    try:
        success = member_service.leave_project(project_id, current_user["user_id"])
        if not success:
            raise HTTPException(status_code=404, detail="Not a member of this project")
        return {"message": "Left project successfully"}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))