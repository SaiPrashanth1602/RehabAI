from fastapi import APIRouter, HTTPException, status
from backend.firebase import get_firestore_db

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

@router.get("/{patient_id}", status_code=status.HTTP_200_OK)
def get_patient_dashboard_data(patient_id: str):
    db = get_firestore_db()
    
    try:
        # 1. Pull dynamic matching fields out of the plan_exercises collection
        exercises_stream = db.collection("plan_exercises").where("patient_id", "==", patient_id).stream()
        exercises_list = []
        
        for doc in exercises_stream:
            ex_data = doc.to_dict()
            ex_data["plan_exercise_id"] = doc.id
            exercises_list.append(ex_data)
            
        # 2. Return a unified response structure matching what dashboard.py expects
        return {
            "patient_id": patient_id,
            "exercises": exercises_list,
            "timestamp": "2026-07-07T11:27:00Z"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Firestore tracking lookup dropped an error line: {str(e)}"
        )
@router.get("/exercise-library/{exercise_code}", status_code=status.HTTP_200_OK)
def get_exercise_library_item(exercise_code: str):
    db = get_firestore_db()
    
    # Check for direct key match first
    doc = db.collection("exercise_library").document(exercise_code).get()
    if doc.exists:
        return doc.to_dict()
        
    # Fallback to appending numeric variants generated during raw seeding rules
    fallback_code = f"{exercise_code}_01"
    doc_fallback = db.collection("exercise_library").document(fallback_code).get()
    if doc_fallback.exists:
        return doc_fallback.to_dict()
        
    raise HTTPException(status_code=404, detail=f"Exercise {exercise_code} not found inside registry library.")