"""
RehabAI - Patient Portal API Communication Client Service
Author: Senior Full Stack Engineer
Description: Centralizes HTTP transport layer operations connecting the Streamlit frontends
             to the FastAPI backend services. Implements rigorous error checking, custom
             timeout fallbacks, and response parsing exceptions for Patient entities.
"""

import logging
from typing import List, Dict, Any, Optional
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError
from frontend.common.utils.config import API_URL, REQUEST_TIMEOUT

# Configure systemic tracking logging format rules
logger = logging.getLogger("RehabAI.FrontendPatientService")


class BackendConnectionError(Exception):
    """Raised when the backend API service is structural or network unreachable."""
    pass


class APIResponseError(Exception):
    """Raised when the backend API returns a non-2xx failure status code response."""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Backend API Exception [{status_code}]: {detail}")


class PatientService:
    """
    Client-side broker management interface handling REST communication with the FastAPI /patients endpoint resource space.
    """

    def __init__(self, timeout_seconds: float = REQUEST_TIMEOUT) -> None:
        """
        Initializes the communication proxy abstraction mapping the underlying connection attributes.
        """
        # FIXED: Injected /api/v1 structure pattern safely to map with settings.API_V1_STR routing prefixes
        base_api = API_URL.rstrip('/')
        if not base_api.endswith('/api/v1'):
            self.base_url = f"{base_api}/api/v1/patients"
        else:
            self.base_url = f"{base_api}/patients"
            
        self.timeout = timeout_seconds

    def _execute_request(self, method: str, url: str, **kwargs) -> Any:
        """
        Internal request dispatcher wrapper mechanism applying defensive exception handling over the wire.
        """
        try:
            kwargs.setdefault("timeout", self.timeout)
            response = requests.request(method, url, **kwargs)
            
            if response.status_code >= 400:
                try:
                    error_detail = response.json().get("detail", response.text)
                except ValueError:
                    error_detail = response.text
                logger.error(f"HTTP Transaction Fault targeting {url} [{response.status_code}]: {error_detail}")
                raise APIResponseError(response.status_code, error_detail)
                
            if response.status_code == 204:
                return True
                
            return response.json()

        except Timeout as e:
            logger.critical(f"Network Timeout boundary triggered while processing transaction targeting: {url}")
            raise BackendConnectionError(f"Network transport timeout latency limit exceeded: {str(e)}")
        except ConnectionError as e:
            logger.critical(f"Refused transport bridge linking root location address: {url}")
            raise BackendConnectionError(f"Backend microservice offline or connection boundary refused: {str(e)}")
        except RequestException as e:
            logger.critical(f"Systemic Request error intercept handling on network routing pool: {str(e)}")
            raise BackendConnectionError(f"Network connection layer fatal execution pipeline failure: {str(e)}")

    def get_patient(self, patient_id: str) -> Dict[str, Any]:
        """
        Requests specific dataset matching structural lookup identifier configurations.
        """
        url = f"{self.base_url}/{patient_id}"
        return self._execute_request("GET", url)

    def create_patient(self, patient_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pushes structural JSON serialization models downstream to spawn database records.
        """
        return self._execute_request("POST", self.base_url, json=patient_payload)

    def update_patient(self, patient_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Applies incremental dictionary adjustments over targeted persistence fields.
        """
        url = f"{self.base_url}/{patient_id}"
        return self._execute_request("PUT", url, json=updates)

    def delete_patient(self, patient_id: str) -> Dict[str, str]:
        """
        Fires execution script parameters requesting resource deactivation workflows.
        """
        url = f"{self.base_url}/{patient_id}"
        return self._execute_request("DELETE", url)

    def list_patients(self) -> List[Dict[str, Any]]:
        """
        Fetches directory streams logging all globally visible target data rows.
        """
        return self._execute_request("GET", self.base_url)

    def patient_exists(self, patient_id: str) -> bool:
        """
        Pings confirmation mapping nodes to evaluate tracking bounds availability.
        """
        url = f"{self.base_url}/{patient_id}/exists"
        result = self._execute_request("GET", url)
        return result.get("exists", False)

    def update_recovery_metrics(
        self, 
        patient_id: str, 
        recovery_score: float, 
        current_rom: float, 
        movement_quality: float
    ) -> Dict[str, Any]:
        """
        Transmits high-speed edge processing telemetry arrays generated via local spatial engines.
        """
        url = f"{self.base_url}/{patient_id}/recovery"
        metrics_payload = {
            "recovery_score": float(recovery_score),
            "current_rom": float(current_rom),
            "movement_quality": float(movement_quality)
        }
        return self._execute_request("PATCH", url, json=metrics_payload)