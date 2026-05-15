from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class ProjectMemberBase(BaseModel):
    project_id: int
    user_id: int
    role: str = "member"


class ProjectMemberCreateRequest(ProjectMemberBase):
    pass


class ProjectMemberUpdateRequest(BaseModel):
    role: Optional[str] = None


class ProjectMemberResponse(ProjectMemberBase):
    id: int
    joined_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )