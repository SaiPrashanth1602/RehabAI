"""
session_service.py

Handles Firestore operations related to rehabilitation sessions.
"""

from datetime import datetime

from backend.firebase import get_firestore_db


class SessionService:

    def __init__(self):
        self.db = get_firestore_db()
        self.collection = self.db.collection("sessions")

    # --------------------------------------------------
    # Create Session
    # --------------------------------------------------

    def create_session(self, session):

        now = datetime.utcnow()

        data = session.model_dump()

        data["timestamp"] = now

        doc_ref = self.collection.document()

        doc_ref.set(data)

        data["id"] = doc_ref.id

        return data

    # --------------------------------------------------
    # Get All Sessions
    # --------------------------------------------------

    def get_all_sessions(self):

        sessions = []

        docs = self.collection.order_by(
            "timestamp",
            direction="DESCENDING"
        ).stream()

        for doc in docs:

            data = doc.to_dict()

            data["id"] = doc.id

            sessions.append(data)

        return sessions

    # --------------------------------------------------
    # Get Sessions By Patient
    # --------------------------------------------------

    def get_patient_sessions(self, patient_id):

        docs = self.collection.stream()

        sessions = []

        for doc in docs:

            data = doc.to_dict()

            if data.get("patient_id") == patient_id:

                data["id"] = doc.id

                sessions.append(data)

        sessions.sort(
            key=lambda x: x["timestamp"],
            reverse=True
        )

        return sessions


session_service = SessionService()