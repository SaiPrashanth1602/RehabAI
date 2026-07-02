from fastapi import APIRouter

from backend.schemas import DashboardResponse
from backend.services.dashboard_service import dashboard_service

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/overview")
def get_overview():
    return dashboard_service.get_overview()


@router.get(
    "/{patient_id}",
    response_model=DashboardResponse
)
def get_dashboard(patient_id: str):
    return dashboard_service.get_dashboard(patient_id)