"""
api.py

Utility functions for communicating with the RehabAI FastAPI backend.
"""

import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"


# =====================================================
# PATIENTS
# =====================================================

def get_patients():
    response = requests.get(f"{BASE_URL}/patients/")
    response.raise_for_status()
    return response.json()


def get_patient(patient_id):
    response = requests.get(
        f"{BASE_URL}/patients/{patient_id}"
    )
    response.raise_for_status()
    return response.json()


def create_patient(patient):
    response = requests.post(
        f"{BASE_URL}/patients/",
        json=patient
    )
    response.raise_for_status()
    return response.json()


def update_patient(patient_id, patient):
    response = requests.put(
        f"{BASE_URL}/patients/{patient_id}",
        json=patient
    )
    response.raise_for_status()
    return response.json()


def delete_patient(patient_id):
    response = requests.delete(
        f"{BASE_URL}/patients/{patient_id}"
    )
    response.raise_for_status()
    return response.json()


# =====================================================
# SESSIONS
# =====================================================

def get_sessions():
    response = requests.get(
        f"{BASE_URL}/sessions/"
    )
    response.raise_for_status()
    return response.json()


def get_patient_sessions(patient_id):
    response = requests.get(
        f"{BASE_URL}/sessions/{patient_id}"
    )
    response.raise_for_status()
    return response.json()


def create_session(session):
    response = requests.post(
        f"{BASE_URL}/sessions/",
        json=session
    )
    response.raise_for_status()
    return response.json()


# =====================================================
# DASHBOARD
# =====================================================

def get_dashboard(patient_id):
    response = requests.get(
        f"{BASE_URL}/dashboard/{patient_id}"
    )
    response.raise_for_status()
    return response.json()

def get_dashboard_overview():

    response = requests.get(
        f"{BASE_URL}/dashboard/overview"
    )

    response.raise_for_status()

    return response.json()