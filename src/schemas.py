"""Pydantic schemas for request/response validation."""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from models import UserRole


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    name: str
    grade_level: Optional[str] = None
    role: UserRole = UserRole.STUDENT


class UserCreate(UserBase):
    """User creation schema with password."""
    password: str


class UserUpdate(BaseModel):
    """User update schema."""
    name: Optional[str] = None
    grade_level: Optional[str] = None


class User(UserBase):
    """User response schema."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ActivityBase(BaseModel):
    """Base activity schema."""
    name: str
    description: str
    category: str  # "technical", "non-technical", "sports"
    schedule: str
    location: Optional[str] = None
    max_participants: int


class ActivityCreate(ActivityBase):
    """Activity creation schema."""
    pass


class ActivityUpdate(BaseModel):
    """Activity update schema."""
    description: Optional[str] = None
    schedule: Optional[str] = None
    location: Optional[str] = None
    max_participants: Optional[int] = None
    is_active: Optional[bool] = None


class Activity(ActivityBase):
    """Activity response schema."""
    id: int
    organizer_id: Optional[int]
    participant_count: int
    available_spots: int
    is_full: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ActivityWithParticipants(Activity):
    """Activity response with participants list."""
    participants: List[User] = []


class SignupRequest(BaseModel):
    """Signup request schema."""
    email: EmailStr


class SignupResponse(BaseModel):
    """Signup response schema."""
    message: str
    activity: Activity
