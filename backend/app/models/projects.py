from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (
        CheckConstraint(
            "status IN ('todo', 'inprogress', 'done')", 
            name="valid_status_check"
        ),
        CheckConstraint(
            "priority IN ('low', 'medium', 'high')", 
            name="valid_priority_check"
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(30), nullable=False, default="todo", server_default="todo")
    priority = Column(String(30), nullable=False, default="medium", server_default="medium")
    due_date = Column(DateTime(timezone=True), nullable=True)
    owner_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="owned_projects")
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
