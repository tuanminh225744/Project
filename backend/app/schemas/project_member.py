from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Literal, Optional

from app.schemas.user import UserBase
from app.schemas.project import ProjectBase


class ProjectMemberBase(BaseModel):
    project_id: int
    user_id: int
    role: Literal["member", "owner"] = "member"


class ProjectMemberCreateRequest(ProjectMemberBase):
    pass


class ProjectMemberUpdateRequest(BaseModel):
    role: Optional[Literal["member", "owner"]] = None


class ProjectMemberResponse(ProjectMemberBase):
    id: int
    joined_at: datetime
    user: UserBase
    project: ProjectBase

    model_config = ConfigDict(
        from_attributes=True
    )
