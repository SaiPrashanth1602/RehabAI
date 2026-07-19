# frontend/utils/config.py

API_URL = "https://rehabai-backend-j814.onrender.com/api/v1"
APP_NAME = "RehabAI"
VERSION = "1.0.0"
REQUEST_TIMEOUT = 10
DEFAULT_THEME = "Dark"

# Clinician-friendly UI Copy Dictionary
UI_MESSAGES = {
    "api_success": "Session uploaded successfully.",
    "camera_ready": "Camera ready.",
    "ai_ready": "AI Engine Ready.",
    "payload_received": "Session Received.",
    "network_error": "Unable to connect to the clinical server. Please check your network status.",
    "timeout_error": "The server request timed out. Retrying transmission...",
    "empty_state": "No patient profiles or logs matched your selection filters.",
    "server_error": "Internal clinical management server exception encountered."
}