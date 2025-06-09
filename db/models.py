# db/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

# تغییر اینجا: Base باید از db.db ایمپورت شود
from db.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, default="user") # 'admin', 'staff', 'user'
    admin_id = Column(Integer, ForeignKey('users.id'), nullable=True) # برای نسبت دادن نیرو به ادمین

    tasks = relationship("Task", back_populates="assigned_staff")
    staff_members = relationship("User", back_populates="admin", remote_side=[id])
    admin = relationship("User", back_populates="staff_members", remote_side=[admin_id])

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, name='{self.name}', role='{self.role}')>"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    time_estimate = Column(String, nullable=True)
    priority = Column(String, nullable=True) # 'high', 'medium', 'low'
    expected_results = Column(String, nullable=True)
    status = Column(String, default="pending") # 'pending', 'in_progress', 'completed', 'cancelled'
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    assigned_staff_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    assigned_staff = relationship("User", back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>"