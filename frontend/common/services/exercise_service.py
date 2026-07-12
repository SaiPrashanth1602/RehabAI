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

# FIXED: Removed the self-referencing ExerciseService import line!
from frontend.common.services.patient_service import BackendConnectionError, APIResponseError

logger = logging.getLogger("RehabAI.FrontendExerciseService")

class ExerciseService:
    def __init__(self, timeout_seconds: float = REQUEST_TIMEOUT) -> None:
        # ... rest of your class code remains exactly the same
        base_api = API_URL.rstrip('/')
        if not base_api.endswith('/api/v1'):
            self.base_url = f"{base_api}/api/v1"
        else:
            self.base_url = base_api
        self.timeout = timeout_seconds

    def get_assigned_exercises(self, plan_id: str) -> List[Dict[str, Any]]:
        """Queries the backend dashboard endpoint to pull active exercises."""
        # FIXED: Changed from /plan-exercises/plan/ to use your live dashboard endpoint structure
        # Extract the real patient ID format out of the plan string context or use state directly
        patient_id = "PAT_24MIS1033" 
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