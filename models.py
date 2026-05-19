from pydantic import BaseModel
from typing import Optional


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class RoleInfo(BaseModel):
    id: int
    name: str
    description: Optional[str] = None


class ProfileData(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None
    role: Optional[RoleInfo] = None


class ProfileMeResponse(BaseModel):
    message: str
    profile: ProfileData