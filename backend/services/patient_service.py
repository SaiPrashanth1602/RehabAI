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
    # Update Patient
    # ---------------------------------------------------

    def update_patient(self, patient_id, patient):

        doc_ref = self.collection.document(patient_id)

        doc = doc_ref.get()

        if not doc.exists:
            return None

        update_data = patient.model_dump(exclude_none=True)

        update_data["updated_at"] = datetime.utcnow()

        doc_ref.update(update_data)

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