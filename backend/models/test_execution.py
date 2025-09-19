from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, JSON
from sqlalchemy.orm import relationship
from core.database import Base

class TestExecution(Base):
    __tablename__ = "test_executions"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    environment_id = Column(Integer, ForeignKey("environments.id"))
    status = Column(String(20), default="pending")  # pending, running, passed, failed
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    result = Column(JSON)
    report_path = Column(String(255))
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    project = relationship("Project", back_populates="test_executions")
    environment = relationship("Environment", back_populates="test_executions")
    creator = relationship("User", back_populates="test_executions")
