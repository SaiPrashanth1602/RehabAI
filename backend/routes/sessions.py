# backend/routes/sessions.py
import uuid
import numpy as np
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Body
from backend.firebase import get_firestore_db
from backend.schemas import SessionCreate, CameraStatePayload, SessionEndPayload

router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"]
)

@router.post("/start", status_code=status.HTTP_201_CREATED)
def start_rehabilitation_session(payload: SessionCreate):
    db = get_firestore_db()

    try:
        generated_session_id = f"SES_{uuid.uuid4().hex.upper()[:10]}"
        now_iso = datetime.utcnow().isoformat() + "Z"

        session_document = {
            "session_id": generated_session_id,
            "patient_id": payload.patient_id,
            "plan_id": payload.plan_id,
            "plan_exercise_id": payload.plan_exercise_id,
            "exercise_code": payload.exercise_code,
            "exercise_name": payload.exercise_name,
            "started_at": now_iso,
            "ended_at": None,
            "duration_seconds": 0,
            "status": "In Progress",
            "camera_status": "Starting",
            "timestamp": now_iso
        }

        db.collection("sessions").document(generated_session_id).set(session_document)

        return {
            "status": "SUCCESS",
            "session_id": generated_session_id,
            "message": "Clinical telemetry loop initialized successfully."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize database session record: {str(e)}"
        )

@router.post("/camera/start", status_code=status.HTTP_200_OK)
def update_camera_active_state(payload: CameraStatePayload):
    db = get_firestore_db()
    try:
        session_ref = db.collection("sessions").document(payload.session_id)
        if not session_ref.get().exists:
            raise HTTPException(status_code=404, detail="Target session reference not found.")

        session_ref.update({
            "camera_status": "Active",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        })
        return {"status": "SUCCESS", "message": "Camera optical feed flagged as ACTIVE."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/end", status_code=status.HTTP_200_OK)
def end_rehabilitation_session(payload: SessionEndPayload):
    db = get_firestore_db()
    now_iso = datetime.utcnow().isoformat() + "Z"

    try:
        session_ref = db.collection("sessions").document(payload.session_id)
        if not session_ref.get().exists:
            raise HTTPException(status_code=404, detail="Target session index invalid.")

        incorrect_reps = max(payload.total_reps - payload.correct_count, 0)

        # 1. Store performance summary inside session_summary indexed by session_id
        summary_ref = db.collection("session_summary").document(payload.session_id)
        summary_document = {
            "summary_id": payload.session_id,
            "session_id": payload.session_id,
            "patient_id": payload.patient_id,
            "exercise_name": payload.exercise_name,
            "total_reps_completed": payload.total_reps,
            "correct_reps": payload.correct_count,
            "incorrect_reps": incorrect_reps,
            "session_accuracy_percentage": payload.accuracy,
            "average_model_confidence": payload.avg_confidence,
            "duration_seconds": payload.duration_seconds,
            "avg_rom": payload.avg_rom,
            "avg_movement_quality": payload.avg_movement_quality,
            "status": "Completed",
            "timestamp": now_iso
        }
        summary_ref.set(summary_document)

        # 2. Compute recovery score from accuracy + confidence (backend-authoritative calculation)
        computed_score = round((payload.accuracy * 0.7) + (payload.avg_confidence * 0.3), 1)
        new_recovery_score = min(max(computed_score, 0.0), 100.0)

        # 3. Update recovery_progress collection
        progress_ref = db.collection("recovery_progress").document(payload.patient_id)
        progress_ref.set({
            "patient_id": payload.patient_id,
            "recovery_score": new_recovery_score,
            "recent_exercise": payload.exercise_name,
            "recovery_trend": payload.trend,
            "recovery_deviation": payload.recovery_deviation,
            "recommendation": payload.recommendation,
            "last_updated": now_iso
        }, merge=True)

        # 4. Update the patients collection so dashboard reflects new metrics immediately
        patient_ref = db.collection("patients").document(payload.patient_id)
        if patient_ref.get().exists:
            patient_update = {
                "recovery_score": new_recovery_score,
                "updated_at": now_iso
            }
            if payload.avg_rom > 0.0:
                patient_update["current_rom"] = payload.avg_rom
            patient_ref.update(patient_update)

        # 5. Finalize the main session record
        session_ref.update({
            "status": "Completed",
            "camera_status": "Stopped",
            "ended_at": now_iso,
            "duration_seconds": payload.duration_seconds,
            "updated_at": now_iso
        })

        return {
            "status": "SUCCESS",
            "message": "Session metrics aggregated and persistent tracking profiles updated.",
            "recovery_score_registered": new_recovery_score
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed transaction closure loop: {str(e)}")


@router.get("/{session_id}", status_code=status.HTTP_200_OK)
def get_session_summary_data(session_id: str):
    db = get_firestore_db()
    try:
        # Check inside the session_summary collection directly using the tracking token
        summary_doc = db.collection("session_summary").document(session_id).get()

        if summary_doc.exists:
            return summary_doc.to_dict()

        # Fallback: if summary hasn't landed yet, scrape the core session metrics
        fallback_doc = db.collection("sessions").document(session_id).get()
        if not fallback_doc.exists:
            raise HTTPException(status_code=404, detail=f"Session token {session_id} not initialized in records.")

        return fallback_doc.to_dict()
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading telemetry document context: {str(e)}")