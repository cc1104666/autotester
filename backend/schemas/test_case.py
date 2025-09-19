from pydantic import BaseModel
from typing import Optional, Dict, Any, Literal
from datetime import datetime

class TestCaseBase(BaseModel):
    name: str
    type: Literal["api", "ui"]
    description: Optional[str] = None
    test_data: Optional[Dict[str, Any]] = None

class TestCaseCreate(TestCaseBase):
    project_id: int

class TestCaseUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[Literal["api", "ui"]] = None
    description: Optional[str] = None
    test_data: Optional[Dict[str, Any]] = None

class TestCase(TestCaseBase):
    id: int
    project_id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
