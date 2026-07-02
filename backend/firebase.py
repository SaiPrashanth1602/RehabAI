"""
firebase.py

Initializes Firebase Admin SDK and exposes a reusable
Firestore database instance.
"""

from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore


# Singleton instances
_app = None
_db = None


def initialize_firebase():
    """
    Initialize Firebase only once.
    """

    global _app

    if _app is None:
        credentials_path = (
            Path(__file__).parent
            / "credentials"
            / "firebase_key.json"
        )

        cred = credentials.Certificate(str(credentials_path))

        _app = firebase_admin.initialize_app(cred)

    return _app


def get_firestore_db():
    """
    Returns Firestore database instance.
    """

    global _db

    if _db is None:
        initialize_firebase()
        _db = firestore.client()

    return _db