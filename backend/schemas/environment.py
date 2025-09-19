from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class EnvironmentBase(BaseModel):
    name: str
    base_url: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class EnvironmentCreate(EnvironmentBase):
    project_id: int

class EnvironmentUpdate(BaseModel):
    name: Optional[str] = None
    base_url: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class Environment(EnvironmentBase):
    id: int
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True
