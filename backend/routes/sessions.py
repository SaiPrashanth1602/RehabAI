"""
sessions.py

Session API Routes
"""

from typing import List

from fastapi import APIRouter, status

from backend.schemas import (
    SessionCreate,
    SessionResponse
)

from backend.services.session_service import session_service


router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"]
)


# --------------------------------------------------
# Create Session
# --------------------------------------------------

@router.post(
    "/",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_session(session: SessionCreate):

    return session_service.create_session(session)


# --------------------------------------------------
# Get All Sessions
# --------------------------------------------------

@router.get(
    "/",
    response_model=List[SessionResponse]
)
def get_sessions():

    return session_service.get_all_sessions()


# --------------------------------------------------
# Get Sessions By Patient
# --------------------------------------------------

@router.get(
    "/{patient_id}",
    response_model=List[SessionResponse]
)
def get_patient_sessions(patient_id: str):

    return session_service.get_patient_sessions(
        patient_id
    )