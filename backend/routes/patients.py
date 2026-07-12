"""
RehabAI - Patient Management REST API Routing Controller
Author: Senior Backend Engineer
Description: Implements thin API routing definitions for Patient lifecycle resources.
             Decouples HTTP routing logic and transport rules from underlying core persistent 
             storage layers by executing transactions strictly via PatientService.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status, Body
from backend.models.patient import Patient
# FIXED: Import the initialized global singleton instead of the class blueprint
from backend.services.patient_service import patient_service

# ---------------------------------------------------------------------------
# 1. ROUTER & SYSTEM LAYER INITIALIZATION
# ---------------------------------------------------------------------------
router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


# ---------------------------------------------------------------------------
# 2. REST API RESOURCE CONTROLLER INTERFACE ENDPOINTS
# ---------------------------------------------------------------------------

@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_new_patient(patient: Patient) -> Dict[str, Any]:
    """
    Registers a new clinical patient profile into the persistent ecosystem layer.
    """
    try:
        return patient_service.create_patient(patient)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute patient creation resource script: {str(e)}"
        )


@router.get("/", response_model=List[Dict[str, Any]], status_code=status.HTTP_200_OK)
def list_all_active_patients() -> List[Dict[str, Any]]:
    """
    Fetches a flat stream directory tracking all globally available active patient files.
    """
    try:
        # FIXED: Mapped to real method get_all_patients()
        return patient_service.get_all_patients()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stream target active directory lists: {str(e)}"
        )


@router.get("/{patient_id}", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
def get_patient_details(patient_id: str) -> Dict[str, Any]:
    """
    Extracts a consolidated profile snapshot corresponding to an explicit business reference key.
    """
    try:
        record = patient_service.get_patient(patient_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient target document location '{patient_id}' does not exist inside active context."
            )
        return record
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Runtime link fault during transaction parsing lookup: {str(e)}"
        )


@router.get("/{patient_id}/exists", response_model=Dict[str, bool], status_code=status.HTTP_200_OK)
def check_patient_existence(patient_id: str) -> Dict[str, bool]:
    """
    High-speed lookup checking structural indexing boundaries for registration confirmation.
    """
    try:
        return {"exists": patient_service.patient_exists(patient_id)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Persistence engine failed to validate registration metrics index: {str(e)}"
        )


@router.put("/{patient_id}", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
def update_patient_profile(patient_id: str, updates: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """
    Applies incremental modifications over an explicitly designated profile reference address.
    """
    try:
        record = patient_service.update_patient(patient_id, updates)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient target document location '{patient_id}' does not exist."
            )
        return record
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Modification transaction engine failed to process payload delta: {str(e)}"
        )


@router.patch("/{patient_id}/recovery", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
def patch_patient_recovery_metrics(
    patient_id: str,
    recovery_score: float = Body(..., embed=True, ge=0.0, le=100.0),
    current_rom: float = Body(..., embed=True, ge=0.0, le=180.0),
    movement_quality: float = Body(..., embed=True, ge=0.0, le=100.0)
) -> Dict[str, Any]:
    """
    Dedicated pipeline node capturing real-time edge processing kinematics directly from computer vision engines.
    """
    try:
        return patient_service.update_recovery_metrics(
            patient_id=patient_id,
            recovery_score=recovery_score,
            current_rom=current_rom,
            movement_quality=movement_quality
        )
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to synchronize live kinematics tracking pipelines to storage: {str(e)}"
        )


@router.delete("/{patient_id}", response_model=Dict[str, str], status_code=status.HTTP_200_OK)
def deactivate_patient(patient_id: str) -> Dict[str, str]:
    """
    Flags the target profile context index as unavailable within general system operational listings.
    """
    try:
        success = patient_service.delete_patient(patient_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient target document location '{patient_id}' does not exist."
            )
        return {"message": "Patient deactivated successfully"}
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"System tracking loop failure during resource deactivation routines: {str(e)}"
        )