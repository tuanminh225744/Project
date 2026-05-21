from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from typing import Optional
from app.schema.project_member import ProjectMemberBase

PROJECT_PRIORITIES = {"low", "medium", "high"}


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "todo"
    priority: str = "medium"
    due_date: Optional[datetime] = None
    members: Optional[ProjectMemberBase] = None

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value: str) -> str:
        if value not in PROJECT_PRIORITIES:
            raise ValueError("priority must be one of: low, medium, high")
        return value


class ProjectCreateRequest(ProjectBase):
    pass


class ProjectUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in PROJECT_PRIORITIES:
            raise ValueError("priority must be one of: low, medium, high")
        return value


class ProjectResponse(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(
        from_attributes=True
    )
