import os
import json

import firebase_admin
from firebase_admin import credentials, firestore

_app = None
_db = None


def initialize_firebase():
    global _app

    if _app is None:
        firebase_json = os.environ.get("FIREBASE_CREDENTIALS")

        if not firebase_json:
            raise RuntimeError("FIREBASE_CREDENTIALS environment variable not found.")

        cred_dict = json.loads(firebase_json)

        cred = credentials.Certificate(cred_dict)

        _app = firebase_admin.initialize_app(cred)

    return _app


def get_firestore_db():
    global _db

    if _db is None:
        initialize_firebase()
        _db = firestore.client()

    return _db