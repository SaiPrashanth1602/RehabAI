"""
RehabAI - Patient Domain Model
Author: Senior Backend Engineer
Description: Defines the core Pydantic domain models for an ACL rehabilitation patient. 
             Separates static registration attributes from dynamic treatment metrics 
             and resolves native Firestore timestamp parsing compatibility.
"""

from typing import Optional, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, model_validator


class PatientBase(BaseModel):
    """
    Static registration profile fields. These are the ONLY fields required 
    when first creating or registering a patient file.
    """
    first_name: str = Field(..., description="Patient's legal first name", min_length=1)
    last_name: str = Field(..., description="Patient's legal last name", min_length=1)
    email: EmailStr = Field(..., description="Unique contact and authentication email address")
    phone: str = Field(..., description="Primary contact mobile or telephone number")
    
    age: int = Field(..., description="Patient age in years", ge=0, le=120)
    gender: str = Field(..., description="Self-identified clinical gender classification")
    height_cm: float = Field(..., description="Patient height measured in centimeters", gt=0)
    weight_kg: float = Field(..., description="Patient weight measured in kilograms", gt=0)
    
    diagnosis: str = Field("ACL Reconstruction Rehabilitation", description="Primary orthopedic diagnosis summary")
    injured_leg: str = Field(..., description="Designation of the pathological limb (Left / Right)")
    acl_grade: str = Field("Grade III", description="Clinical severity classification of the ligament injury")
    date_of_surgery: Optional[str] = Field(None, description="Date of surgical repair")
    current_phase: str = Field("Phase I", description="Current clinical rehabilitation pathway classification")
    recovery_day: int = Field(1, description="Days elapsed since surgery day", ge=0)
    
    doctor_id: str = Field(..., description="Unique system reference ID of the supervising practitioner")
    doctor_name: str = Field("Dr. Placeholder", description="Legal name of the attending clinical specialist")
    
    is_active: bool = Field(True, description="Conditional flag controlling patient record availability")


class PatientCreate(PatientBase):
    """
    Data validation schema used strictly during patient registration.
    """
    pass


class Patient(PatientBase):
    """
    The full operational Patient record model inside core runtime memory pipelines.
    Includes automated metric calculations and dynamic treatment metrics that are empty at start.
    """
    patient_id: str = Field(..., description="Unique absolute business primary key identifier for the patient")
    bmi: float = Field(0.0, description="Calculated Body Mass Index value")
    
    # Biomechanical Performance Metrics Matrix (Default to 0.0, populated during exercise runs)
    recovery_score: float = Field(0.0, description="Aggregated clinical functional milestone score", ge=0.0, le=100.0)
    current_rom: float = Field(0.0, description="Peak Range of Motion degree registration", ge=0.0, le=180.0)
    movement_quality: float = Field(0.0, description="AI Evaluated movement accuracy and stability metric", ge=0.0, le=100.0)
    
    # Core Audit Metrics
    created_at: Any = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: Any = Field(default_factory=lambda: datetime.utcnow().isoformat())

    @model_validator(mode="before")
    @classmethod
    def calculate_metrics_and_format_timestamps(cls, data: dict) -> dict:
        if isinstance(data, dict):
            height_cm = data.get("height_cm")
            weight_kg = data.get("weight_kg")
            if height_cm and weight_kg:
                height_m = height_cm / 100.0
                data["bmi"] = round(weight_kg / (height_m ** 2), 2)
            
            for field in ["created_at", "updated_at"]:
                val = data.get(field)
                if val and not isinstance(val, str) and hasattr(val, "isoformat"):
                    data[field] = val.isoformat()
                elif val and not isinstance(val, str):
                    data[field] = str(val)
        return data

    class Config:
        populate_by_name = True
        str_strip_whitespace = True