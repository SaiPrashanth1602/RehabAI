# Inside backend/schemas.py
from datetime import datetime
from typing import Optional, List, Any, Dict
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

    model_config = {"from_attributes": True}

# ==========================================================
# Session & AI Processing Schemas
# ==========================================================
class SessionBase(BaseModel):
    patient_id: str
    plan_id: str
    plan_exercise_id: str
    exercise_code: str
    exercise_name: str
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    duration_seconds: int = 0
    status: str = "Scheduled"
    camera_status: str = "Not Started"

class SessionCreate(BaseModel):
    patient_id: str
    plan_id: str
    plan_exercise_id: str
    exercise_code: str
    exercise_name: str

class CameraStatePayload(BaseModel):
    session_id: str

class SessionEndPayload(BaseModel):
    session_id: str
    patient_id: str
    exercise_name: str
    total_reps: int
    correct_count: int
    accuracy: float
    avg_confidence: float
    recovery_score: float
    recovery_deviation: float
    trend: str
    recommendation: str
    duration_seconds: int = 0
    avg_rom: float = 0.0
    avg_movement_quality: float = 0.0

class SessionResponse(SessionBase):
    session_id: str
    timestamp: datetime

    model_config = {"from_attributes": True}

# ==========================================================
# Dashboard & Analytics Responses
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

class RecommendationResponse(BaseModel):
    id: str
    patient_id: str
    doctor_id: str
    text: str
    created_at: datetime