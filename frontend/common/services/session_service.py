"""
RehabAI - Patient Portal Session API Communication Client Service
Author: Senior Full Stack Engineer
Description: Centralizes HTTP transport layer operations connecting the Streamlit frontends
             to the FastAPI backend session lifecycle and camera orchestration endpoints.
"""

import logging
from typing import Dict, Any
import requests
from frontend.common.utils.config import API_URL, REQUEST_TIMEOUT
from frontend.common.services.patient_service import BackendConnectionError, APIResponseError

logger = logging.getLogger("RehabAI.FrontendSessionService")


class SessionService:
    def __init__(self, timeout_seconds: float = REQUEST_TIMEOUT) -> None:
        base_api = API_URL.rstrip('/')
        if "/api/v1" in base_api:
            self.base_url = base_api
        else:
            self.base_url = f"{base_api}/api/v1"
        self.timeout = timeout_seconds

    def start_session(self, patient_id: str, plan_id: str, plan_exercise_id: str, exercise_code: str, exercise_name: str) -> Dict[str, Any]:
        """Dispatches payload allocation parameters to safely spawn an active Firestore session block."""
        url = f"{self.base_url}/sessions/start"
        payload = {
            "patient_id": patient_id,
            "plan_id": plan_id,
            "plan_exercise_id": plan_exercise_id,
            "exercise_code": exercise_code,
            "exercise_name": exercise_name
        }
        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            if response.status_code >= 400:
                raise APIResponseError(response.status_code, response.text)
            return response.json()
        except requests.RequestException as e:
            logger.error(f"HTTP Session Transaction Fault targeting {url}: {e}")
            raise BackendConnectionError(f"Backend Session API Exception: {e}")

    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Fetches runtime structural attributes of an active session document."""
        url = f"{self.base_url}/sessions/{session_id}"
        try:
            response = requests.get(url, timeout=self.timeout)
            if response.status_code >= 400:
                raise APIResponseError(response.status_code, response.text)
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed pulling real-time metadata from {url}: {e}")
            raise BackendConnectionError(f"Session data pipeline link dropped: {e}")

    def start_camera(self, session_id: str) -> Dict[str, Any]:
        """Signals hardware capture layer to begin frame processing runs."""
        url = f"{self.base_url}/sessions/camera/start"
        try:
            response = requests.post(url, json={"session_id": session_id}, timeout=self.timeout)
            if response.status_code >= 400:
                raise APIResponseError(response.status_code, response.text)
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Hardware camera initialization handshake fault at {url}: {e}")
            raise BackendConnectionError(f"Device optic thread block failure: {e}")

    def camera_active(self, session_id: str) -> Dict[str, Any]:
        """Updates transactional flag indicating steady video data pipeline streaming."""
        url = f"{self.base_url}/sessions/camera/active"
        try:
            response = requests.post(url, json={"session_id": session_id}, timeout=self.timeout)
            if response.status_code >= 400:
                raise APIResponseError(response.status_code, response.text)
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to post camera active flag state: {e}")
            raise BackendConnectionError(f"Operational state synchronization aborted: {e}")

    def stop_camera(self, session_id: str) -> Dict[str, Any]:
        """Drops active camera frame allocation buffers."""
        url = f"{self.base_url}/sessions/camera/stop"
        try:
            response = requests.post(url, json={"session_id": session_id}, timeout=self.timeout)
            if response.status_code >= 400:
                raise APIResponseError(response.status_code, response.text)
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed spinning down video capture lines: {e}")
            raise BackendConnectionError(f"Optic connection bus tracking error: {e}")

    def end_session(self, session_id: str) -> Dict[str, Any]:
        """Triggers aggregation calculators to close out and save the operational session summary."""
        url = f"{self.base_url}/sessions/end"
        try:
            response = requests.post(url, json={"session_id": session_id}, timeout=self.timeout)
            if response.status_code >= 400:
                raise APIResponseError(response.status_code, response.text)
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Session teardown sequence run dropped exception lines targeting {url}: {e}")
            raise BackendConnectionError(f"Database session aggregation closeout failure: {e}")