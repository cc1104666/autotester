from pydantic import BaseModel
from typing import Optional, Dict, Any, Literal, List
from datetime import datetime

class TestExecutionBase(BaseModel):
    status: Literal["pending", "running", "passed", "failed"] = "pending"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    report_path: Optional[str] = None

class TestExecutionCreate(BaseModel):
    project_id: int
    environment_id: int
    test_case_ids: Optional[List[int]] = None

class TestExecutionUpdate(BaseModel):
    status: Optional[Literal["pending", "running", "passed", "failed"]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    report_path: Optional[str] = None

class TestExecution(TestExecutionBase):
    id: int
    project_id: int
    environment_id: int
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True
