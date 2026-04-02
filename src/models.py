"""SQLAlchemy ORM models for activities, users, and signups."""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum


class UserRole(str, enum.Enum):
    """User role enumeration."""
    STUDENT = "student"
    ORGANIZER = "organizer"
    ADMIN = "admin"


# Association table for many-to-many relationship between User and Activity
activity_participants = Table(
    "activity_participants",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id"), primary_key=True),
    Column("activity_id", Integer, ForeignKey("activity.id"), primary_key=True),
    Column("signup_date", DateTime, default=datetime.utcnow)
)


class User(Base):
    """User model - represents students, organizers, and admins."""
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    grade_level = Column(String(50), nullable=True)  # e.g., "10th", "11th", "12th"
    role = Column(SQLEnum(UserRole), default=UserRole.STUDENT)
    is_active = Column(Integer, default=1)  # SQLite uses Integer for boolean
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organized_activities = relationship(
        "Activity",
        back_populates="organizer",
        foreign_keys="Activity.organizer_id"
    )
    registered_activities = relationship(
        "Activity",
        secondary=activity_participants,
        back_populates="participants"
    )

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class Activity(Base):
    """Activity model - represents extracurricular activities."""
    __tablename__ = "activity"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # "technical", "non-technical", "sports"
    schedule = Column(String(255), nullable=False)  # e.g., "Fridays, 3:30 PM - 5:00 PM"
    location = Column(String(255), nullable=True)  # e.g., "Room 101"
    max_participants = Column(Integer, nullable=False)
    organizer_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organizer = relationship(
        "User",
        back_populates="organized_activities",
        foreign_keys=[organizer_id]
    )
    participants = relationship(
        "User",
        secondary=activity_participants,
        back_populates="registered_activities"
    )

    def __repr__(self):
        return f"<Activity {self.name}>"

    @property
    def participant_count(self):
        """Get current number of participants."""
        return len(self.participants)

    @property
    def available_spots(self):
        """Get number of available spots."""
        return max(0, self.max_participants - self.participant_count)

    @property
    def is_full(self):
        """Check if activity is at max capacity."""
        return self.participant_count >= self.max_participants
