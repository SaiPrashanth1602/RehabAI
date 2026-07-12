"""
RehabAI - Exercise Domain Model
Author: Senior Backend Engineer
Description: Defines the core Pydantic domain models for prescribed rehabilitation exercises.
             Enforces strict type systems and validation rules over geometric joint boundaries,
             instruction series metadata, and targeting profiles for computer vision execution.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ExerciseBase(BaseModel):
    """
    Base structural data model mapping fundamental biometric and protocol fields of a rehabilitation movement.
    """
    exercise_name: str = Field(..., description="Patient-facing standard name of the exercise", min_length=1)
    clinical_name: str = Field(..., description="Formal medical/orthopedic designation used by physiotherapists")
    description: str = Field(..., description="High-level introductory summary detailing the movement arc")
    purpose: str = Field(..., description="Target functional recovery objective or primary movement benefit")
    
    rehabilitation_phase: str = Field("Phase I", description="Clinical pathway layer restriction (Phase I, II, III, Return to Sport)")
    difficulty: str = Field("Easy", description="Anatomical load rating classification (Easy, Medium, Hard)")
    estimated_duration_minutes: int = Field(5, description="Expected operational block limit to finish all sets", ge=1)
    
    # Kinematics Target Framework Boundaries
    target_rom_min: float = Field(0.0, description="Minimum acceptable angle boundary threshold in degrees", ge=0.0, le=180.0)
    target_rom_max: float = Field(180.0, description="Maximum objective angle target parameter in degrees", ge=0.0, le=180.0)
    target_repetitions: int = Field(10, description="Prescribed iteration count required per discrete set matching form parameters", gt=0)
    target_sets: int = Field(3, description="Total sequential validation blocks required to conclude the exercise element", gt=0)
    hold_duration_seconds: int = Field(0, description="Required isometric contraction window at peak angle threshold", ge=0)
    rest_between_sets_seconds: int = Field(30, description="Configured inter-set physical recovery interval in seconds", ge=0)
    
    # Instruction Text Sequences & Kinematic Warnings
    instructions: List[str] = Field(default_factory=list, description="Ordered chronological training list elements for patient navigation")
    common_mistakes: List[str] = Field(default_factory=list, description="List of negative behavioral patterns or mechanical deviations to avoid")
    
    # Computer Vision Engine Staging Framework Parameters
    camera_view: str = Field("Side View", description="Required camera device alignment orientation grid (e.g., Side View, Front View)")
    required_landmarks: List[str] = Field(default_factory=list, description="MediaPipe anatomical joint node identifiers required for tracking calculations")
    ai_features: List[str] = Field(default_factory=list, description="Extracted mathematical pipelines executed over video array frames")
    model_name: str = Field("random_forest_v1.pkl", description="Identifier of the serialized machine learning model grading form metrics")
    
    status: str = Field("Assigned", description="Current behavioral planning state token (Assigned, In Progress, Completed)")
    is_active: bool = Field(True, description="Conditional flag managing resource visibility across standard directories")


class ExerciseCreate(ExerciseBase):
    """
    Data validation structure used when clinical administrators register or append new protocols to system libraries.
    """
    exercise_id: str = Field(..., description="Unique alphanumeric identifier mapping the primary exercise asset structure")


class ExerciseUpdate(BaseModel):
    """
    Delta schema enabling granular modification patches (PATCH) on dynamic exercise properties.
    """
    exercise_name: Optional[str] = Field(None, min_length=1)
    clinical_name: Optional[str] = None
    description: Optional[str] = None
    purpose: Optional[str] = None
    rehabilitation_phase: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_duration_minutes: Optional[int] = Field(None, ge=1)
    target_rom_min: Optional[float] = Field(None, ge=0.0, le=180.0)
    target_rom_max: Optional[float] = Field(None, ge=0.0, le=180.0)
    target_repetitions: Optional[int] = Field(None, gt=0)
    target_sets: Optional[int] = Field(None, gt=0)
    hold_duration_seconds: Optional[int] = Field(None, ge=0)
    rest_between_sets_seconds: Optional[int] = Field(None, ge=0)
    instructions: Optional[List[str]] = None
    common_mistakes: Optional[List[str]] = None
    camera_view: Optional[str] = None
    required_landmarks: Optional[List[str]] = None
    ai_features: Optional[List[str]] = None
    model_name: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None


class Exercise(ExerciseBase):
    """
    Defines the final instantiated Exercise state mapping object matching core database storage schemas.
    """
    exercise_id: str = Field(..., description="Unique business primary key identifier mapping the exercise instance record")
    
    # Audit trail trackers
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="ISO timestamp for database row allocation")
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="ISO timestamp for record modifications")

    class Config:
        """
        Pydantic operational configuration specification mapping rules.
        """
        populate_by_name = True
        str_strip_whitespace = True
        json_schema_extra = {
            "example": {
                "exercise_id": "EX_HS_001",
                "exercise_name": "Heel Slide",
                "clinical_name": "Knee Flexion in Supine Position",
                "description": "Slowly slide the heel backward while maintaining surface interaction to improve knee range of motion.",
                "purpose": "Increase Knee Flexion Range of Motion and reduce general post-operative stiffness.",
                "rehabilitation_phase": "Phase I",
                "difficulty": "Easy",
                "estimated_duration_minutes": 5,
                "target_rom_min": 90.0,
                "target_rom_max": 100.0,
                "target_repetitions": 10,
                "target_sets": 3,
                "hold_duration_seconds": 5,
                "rest_between_sets_seconds": 30,
                "instructions": [
                    "Lie comfortably flat on your back upon an exercise mat surface.",
                    "Slowly pull the designated heel backward toward your hip.",
                    "Hold the contraction at maximum depth parameter guidelines for 5 seconds.",
                    "Gently return the foot to extended neutral base baseline orientation."
                ],
                "common_mistakes": [
                    "Lifting the heel off the ground completely during horizontal translation.",
                    "Rotating the hip joint internally or externally to cheat depth boundaries."
                ],
                "camera_view": "Side View",
                "required_landmarks": ["LEFT_HIP", "LEFT_KNEE", "LEFT_ANKLE"],
                "ai_features": ["Knee Flexion Angle", "Angular Velocity Profile"],
                "model_name": "knee_flexion_rf.pkl",
                "status": "Assigned",
                "is_active": True,
                "created_at": "2026-07-03T12:00:00Z",
                "updated_at": "2026-07-03T12:00:00Z"
            }
        }