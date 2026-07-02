"""
patients.py

Patient API Routes
"""

from typing import List

from fastapi import APIRouter, HTTPException, status

from backend.schemas import (
    PatientCreate,
    PatientResponse,
    PatientUpdate,
)

from backend.services.patient_service import patient_service


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


# -------------------------------------------------------
# Create Patient
# -------------------------------------------------------

@router.post(
    "/",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED
)
def create_patient(patient: PatientCreate):

    return patient_service.create_patient(patient)


# -------------------------------------------------------
# Get All Patients
# -------------------------------------------------------

@router.get(
    "/",
    response_model=List[PatientResponse]
)
def get_all_patients():

    return patient_service.get_all_patients()


# -------------------------------------------------------
# Get Single Patient
# -------------------------------------------------------

@router.get(
    "/{patient_id}",
    response_model=PatientResponse
)
def get_patient(patient_id: str):

    patient = patient_service.get_patient(patient_id)

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return patient


# -------------------------------------------------------
# Update Patient
# -------------------------------------------------------

@router.put(
    "/{patient_id}",
    response_model=PatientResponse
)
def update_patient(
    patient_id: str,
    patient: PatientUpdate
):

    updated = patient_service.update_patient(
        patient_id,
        patient
    )

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return updated


# -------------------------------------------------------
# Delete Patient
# -------------------------------------------------------

@router.delete(
    "/{patient_id}"
)
def delete_patient(patient_id: str):

    deleted = patient_service.delete_patient(
        patient_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return {
        "message": "Patient deleted successfully"
    }