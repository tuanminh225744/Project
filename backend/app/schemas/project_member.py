from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Literal, Optional

from app.schemas.user import UserBase

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

    model_config = ConfigDict(
        from_attributes=True
    )
