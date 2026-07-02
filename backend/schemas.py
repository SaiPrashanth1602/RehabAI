"""
schemas.py

Pydantic schemas for RehabAI Backend.
Defines request and response models used by the API.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ==========================================================
# Patient Schemas
# ==========================================================

class PatientBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., ge=1, le=120)
    gender: str = Field(..., examples=["Male", "Female", "Other"])
    injury: str = Field(..., examples=["ACL Reconstruction"])
    doctor: str = Field(..., examples=["Dr. Kumar"])


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    injury: Optional[str] = None
    doctor: Optional[str] = None


class PatientResponse(PatientBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


# ==========================================================
# Session Schemas
# ==========================================================

class SessionBase(BaseModel):
    patient_id: str
    exercise: str

    status: str
    rep_count: int

    rom: float

    movement_quality: float

    recovery_score: float

    recovery_deviation: float

    trend: str

    recommendation: str

    timestamp: datetime


class SessionCreate(SessionBase):
    pass


class SessionResponse(SessionBase):
    id: str
    timestamp: datetime

    model_config = {
        "from_attributes": True
    }


# ==========================================================
# Dashboard
# ==========================================================

class DashboardResponse(BaseModel):
    patient_id: str
    exercise: str
    status: str
    rep_count: int
    rom: float
    movement_quality: float
    recovery_score: float
    recovery_deviation: float
    trend: str
    recommendation: str


# ==========================================================
# Recommendation
# ==========================================================

class RecommendationResponse(BaseModel):
    patient_id: str

    recommendation: str

    priority: str

    confidence: float