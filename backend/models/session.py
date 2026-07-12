"""
RehabAI - Rehabilitation Session Domain Model
Author: Senior Backend Engineer
Description: Defines the full production model fields mapping exercise sessions,
             incorporating aggregate scoring nodes queried by the portal dashboard.
"""

from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, model_validator


class SessionBase(BaseModel):
    patient_id: str = Field(..., description="Unique reference mapping the active patient")
    plan_id: str = Field(..., description="Unique reference mapping the treatment plan context")
    plan_exercise_id: str = Field(..., description="Unique reference mapping the prescribed exercise configuration")
    exercise_code: str = Field(..., description="Static identifier blueprint key (e.g., EX_HS)")
    exercise_name: str = Field(..., description="Clear name string of the selected exercise protocol")
    
    started_at: Any = Field(default_factory=lambda: datetime.utcnow().isoformat())
    ended_at: Optional[Any] = Field(None)
    duration_seconds: int = Field(0, description="Total running duration interval in seconds", ge=0)
    
    status: str = Field("Scheduled", description="Operational tracking state: Scheduled, In Progress, Completed, Cancelled")
    camera_status: str = Field("Not Started", description="Optic connection capture link state: Not Started, Starting, Active, Stopped")


class SessionCreate(BaseModel):
    patient_id: str
    plan_id: str
    plan_exercise_id: str
    exercise_code: str
    exercise_name: str


class Session(SessionBase):
    session_id: str = Field(..., description="Unique transactional primary key token identifying this session document")
    created_at: Any = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: Any = Field(default_factory=lambda: datetime.utcnow().isoformat())

    @model_validator(mode="before")
    @classmethod
    def format_timestamps(cls, data: dict) -> dict:
        if isinstance(data, dict):
            for field in ["started_at", "ended_at", "created_at", "updated_at"]:
                val = data.get(field)
                if val and not isinstance(val, str) and hasattr(val, "isoformat"):
                    data[field] = val.isoformat()
        return data

    class Config:
        populate_by_name = True