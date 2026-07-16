"""
RehabAI - Patient Portal Exercise API Transport Broker
Author: Senior Systems Architect
Description: Centralizes HTTP REST routines for fetching dynamic prescriptions
             and physical library content profiles from the backend.
"""

import requests
import logging
from typing import List, Dict, Any
from frontend.common.utils.config import API_URL, REQUEST_TIMEOUT
from frontend.common.services.patient_service import BackendConnectionError, APIResponseError

logger = logging.getLogger("RehabAI.FrontendExerciseService")

class ExerciseService:
    def __init__(self, timeout_seconds: float = REQUEST_TIMEOUT) -> None:
        base_api = API_URL.rstrip('/')
        if not base_api.endswith('/api/v1'):
            self.base_url = f"{base_api}/api/v1"
        else:
            self.base_url = base_api
        self.timeout = timeout_seconds

    def get_assigned_exercises(self, plan_id: str, patient_id: str = None) -> List[Dict[str, Any]]:
        """
        Queries the backend dashboard endpoint to pull active exercises.
        patient_id is required to fetch the correct patient's exercises.
        If not provided, derives it from plan_id as a last resort.
        """
        # Resolve patient_id: prefer explicit argument, fallback to session_state, finally derive from plan_id
        if patient_id is None:
            try:
                import streamlit as st
                patient_id = st.session_state.get("patient_id")
            except Exception:
                patient_id = None

        if patient_id is None:
            # Last resort: extract patient ID segment from plan_id format PLN_<PATIENT_ID>_<PHASE>
            parts = plan_id.split("_")
            if len(parts) >= 3:
                patient_id = "_".join(parts[1:-1])
            else:
                patient_id = plan_id

        url = f"{self.base_url}/dashboard/{patient_id}"
        try:
            response = requests.get(url, timeout=self.timeout)
            if response.status_code >= 400:
                raise APIResponseError(response.status_code, response.text)

            # The dashboard returns a nested structure; extract the 'exercises' payload array cleanly
            data = response.json()
            if isinstance(data, dict) and "exercises" in data:
                return data["exercises"]
            return data
        except requests.RequestException as e:
            logger.error(f"Failed streaming dashboard components over network: {e}")
            raise BackendConnectionError(f"Backend microservice unreachable: {e}")

    def get_exercise_details(self, exercise_code: str) -> Dict[str, Any]:
        """Fetches instructions and landmarks directly through the dashboard router channel."""
        url = f"{self.base_url}/dashboard/exercise-library/{exercise_code}"
        try:
            response = requests.get(url, timeout=self.timeout)
            if response.status_code >= 400:
                raise APIResponseError(response.status_code, response.text)
            return response.json()
        except requests.RequestException as e:
            raise BackendConnectionError(f"Link architecture offline: {e}")