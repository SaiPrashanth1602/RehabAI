"""
patient_service.py

Handles all Firestore operations related to patients.
"""

from datetime import datetime
from backend.firebase import get_firestore_db


class PatientService:

    def __init__(self):
        self.db = get_firestore_db()
        self.collection = self.db.collection("patients")

    # ---------------------------------------------------
    # Create Patient
    # ---------------------------------------------------
    def create_patient(self, patient):
        now = datetime.utcnow()
        data = patient.model_dump()
        data["created_at"] = now
        data["updated_at"] = now

        # ✅ FIX: Pass the structural patient_id string to lock it as the Firestore document name
        patient_id = data.get("patient_id")
        if patient_id:
            doc_ref = self.collection.document(patient_id)
        else:
            doc_ref = self.collection.document()

        doc_ref.set(data)
        data["id"] = doc_ref.id
        return data

    # ---------------------------------------------------
    # Get All Patients
    # ---------------------------------------------------
    def get_all_patients(self):
        patients = []
        docs = self.collection.stream()
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            patients.append(data)
        return patients

    # ---------------------------------------------------
    # Get Patient
    # ---------------------------------------------------
    def get_patient(self, patient_id):
        doc = self.collection.document(patient_id).get()
        if not doc.exists:
            return None
        data = doc.to_dict()
        data["id"] = doc.id
        return data

    # ---------------------------------------------------
    # Patient Exists (FIXED: Added missing method)
    # ---------------------------------------------------
    def patient_exists(self, patient_id: str) -> bool:
        doc = self.collection.document(patient_id).get()
        return doc.exists

    # ---------------------------------------------------
    # Update Patient
    # ---------------------------------------------------
    def update_patient(self, patient_id, patient_updates):
        doc_ref = self.collection.document(patient_id)
        doc = doc_ref.get()
        if not doc.exists:
            return None

        # FIXED: Handles raw dict payload instead of assuming it's a Pydantic object
        if hasattr(patient_updates, "model_dump"):
            update_data = patient_updates.model_dump(exclude_none=True)
        else:
            update_data = {k: v for k, v in patient_updates.items() if v is not None}

        update_data["updated_at"] = datetime.utcnow()
        doc_ref.update(update_data)

        updated = doc_ref.get().to_dict()
        updated["id"] = patient_id
        return updated

    # ---------------------------------------------------
    # Update Recovery Metrics (FIXED: Added missing method)
    # ---------------------------------------------------
    def update_recovery_metrics(self, patient_id: str, recovery_score: float, current_rom: float, movement_quality: float):
        doc_ref = self.collection.document(patient_id)
        if not doc_ref.get().exists:
            raise KeyError(f"Patient profile record key '{patient_id}' not found.")

        metrics_payload = {
            "recovery_score": recovery_score,
            "current_rom": current_rom,
            "movement_quality": movement_quality,
            "updated_at": datetime.utcnow()
        }
        doc_ref.update(metrics_payload)
        
        updated = doc_ref.get().to_dict()
        updated["id"] = patient_id
        return updated

    # ---------------------------------------------------
    # Delete Patient
    # ---------------------------------------------------
    def delete_patient(self, patient_id):
        doc_ref = self.collection.document(patient_id)
        doc = doc_ref.get()
        if not doc.exists:
            return False
        doc_ref.delete()
        return True


patient_service = PatientService()