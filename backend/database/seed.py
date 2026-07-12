"""
RehabAI V1 - Production Database Architecture Ingestion Seed Script
Author: Sai Prashanth Ramesh & Core Systems Architecture
Description: Safely flushes old database documents and re-seeds presentation-ready 
             profiles linked with the independent V1 exercise quality models.
"""

import sys
import os
from datetime import datetime, timedelta

# Ensure workspace modules resolve cleanly from the system path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.firebase import get_firestore_db


def seed_production_database() -> None:
    print("🚀 Initiating RehabAI Database Wipe & Presentation Seeding Run...")
    db = get_firestore_db()

    patient_id = "PAT_24MIS1033"
    plan_id = "PLN_24MIS1033_PH1"
    doctor_id = "DOC_77A91"
    now = datetime.utcnow()

    # Define the primary collections we need to flush to get a true clean slate
    collections_to_flush = [
        "exercise_library", 
        "patients", 
        "rehab_plans", 
        "plan_exercises", 
        "recovery_progress", 
        "analytics", 
        "notifications",
        "sessions",          
        "session_summary"    
    ]

    try:
        # ===========================================================================
        # 0. DELETION BUFFER BLOCK: SAFE CLEAN SLATE FLUSH
        # ===========================================================================
        print("🧹 Flushing obsolete document collections from cloud cluster storage...")
        for coll_name in collections_to_flush:
            docs_stream = db.collection(coll_name).stream()
            deleted_count = 0
            for doc in docs_stream:
                doc.reference.delete()
                deleted_count += 1
            if deleted_count > 0:
                print(f"   🗑️ Purged {deleted_count} stale documents from collection: '{coll_name}'")

        print("")

        # ===========================================================================
        # 1. SEED EXERCISE LIBRARY BLUEPRINTS (V1 MODEL ALIGNED)
        # ===========================================================================
        print("⚡ Seeding V1 aligned 'exercise_library' collection definitions...")
        library = {
            "EX_LN": {
                "name": "Inline Lunge",
                "description": "Unilateral lower extremity stability and movement symmetry quality assessment tracking.",
                "animation_url": "https://cdn.rehabai.com/assets/animations/lunge.gif",
                "thumbnail_url": "https://cdn.rehabai.com/assets/thumbs/lunge.png",
                "video_url": "https://cdn.rehabai.com/assets/videos/lunge_inst.mp4",
                "acl_rehabilitation_phase": "Phase I",
                "target_muscles": ["Quadriceps", "Hamstrings", "Gastrocnemius"],
                "mediapipe_landmarks": [11, 12, 23, 24, 25, 26, 27, 28, 29, 30],
                "biomechanical_features": ["Hip_Angle", "Knee_Angle", "Ankle_Angle", "Knee_ROM"],
                "random_forest_model": "Lunge_RF.pkl",
                "default_target_rom": 90.0,
                "default_target_hold": 2,
                "default_target_sets": 3,
                "default_target_reps": 10
            },
            "EX_STS": {
                "name": "Sit-to-Stand",
                "description": "Functional biomechanic trajectory assessment for lower-body power and ascent speed balance.",
                "animation_url": "https://cdn.rehabai.com/assets/animations/sit_to_stand.gif",
                "thumbnail_url": "https://cdn.rehabai.com/assets/thumbs/sit_to_stand.png",
                "video_url": "https://cdn.rehabai.com/assets/videos/sts_inst.mp4",
                "acl_rehabilitation_phase": "Phase I",
                "target_muscles": ["Quadriceps", "Gluteus Maximus", "Hamstrings"],
                "mediapipe_landmarks": [11, 12, 23, 24, 25, 26, 27, 28, 29, 30],
                "biomechanical_features": ["Knee_Angle", "Hip_Angle", "Rise_Duration"],
                "random_forest_model": "STS_RF.pkl",
                "default_target_rom": 95.0,
                "default_target_hold": 1,
                "default_target_sets": 3,
                "default_target_reps": 10
            },
            "EX_ASLR": {
                "name": "Active Straight Leg Raise",
                "description": "Isolated anterior hip chain and core integration control quality validation analyzer.",
                "animation_url": "https://cdn.rehabai.com/assets/animations/aslr.gif",
                "thumbnail_url": "https://cdn.rehabai.com/assets/thumbs/aslr.png",
                "video_url": "https://cdn.rehabai.com/assets/videos/aslr_inst.mp4",
                "acl_rehabilitation_phase": "Phase I",
                "target_muscles": ["Iliopsoas", "Rectus Femoris", "Core Stabilizers"],
                "mediapipe_landmarks": [11, 12, 23, 24, 25, 26, 27, 28, 29, 30],
                "biomechanical_features": ["Hip_Angle", "Knee_Extension_Hold", "Max_Elevation"],
                "random_forest_model": "ASLR_RF.pkl",
                "default_target_rom": 75.0,
                "default_target_hold": 2,
                "default_target_sets": 3,
                "default_target_reps": 10
            }
        }
        for code, data in library.items():
            db.collection("exercise_library").document(code).set(data)

        # ===========================================================================
        # 2. SEED STATIC PATIENT CORE PROFILE RECORD
        # ===========================================================================
        print("⚡ Seeding 'patients' profile data collection...")
        db.collection("patients").document(patient_id).set({
            "patient_id": patient_id,
            "first_name": "Sai Prashanth",
            "last_name": "Ramesh",
            "email": "sai.prashanth@example.com",
            "phone": "+919876543210",
            "age": 20,
            "gender": "Male",
            "height_cm": 180.0,
            "weight_kg": 52.0,
            "bmi": 16.05,
            "diagnosis": "Anterior Cruciate Ligament (ACL) Reconstruction Recovery",
            "injured_leg": "Right",
            "acl_grade": "Grade III",
            "date_of_surgery": "2026-06-01T00:00:00Z",
            "current_active_plan_id": plan_id,
            "doctor_id": doctor_id,
            "doctor_name": "Dr. John Smith",
            "is_active": True,
            "created_at": now,
            "updated_at": now
        })

        # ===========================================================================
        # 3. SEED THE CLINICAL TREATMENT PLAN
        # ===========================================================================
        print("⚡ Seeding 'rehab_plans' root configurations...")
        db.collection("rehab_plans").document(plan_id).set({
            "plan_id": plan_id,
            "plan_name": "Post-Op ACL Acute Mobilization Plan",
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "phase": "Phase I",
            "start_date": now - timedelta(days=18),
            "end_date": now + timedelta(days=24),
            "status": "Active",
            "target_goals": [
                "Restore full terminal knee extension thresholds smoothly",
                "Maximize unilateral balance stabilization metrics on Lunges",
                "Achieve 70 degrees pain-free lag-free elevation during ASLR sets"
            ],
            "expected_completion_weeks": 6,
            "created_at": now - timedelta(days=18),
            "updated_at": now - timedelta(days=18)
        })

        # ===========================================================================
        # 4. SEED DETAILED PRESCRIBED EXERCISES TIMELINE MATRIX
        # ===========================================================================
        print("⚡ Seeding 'plan_exercises' prescription layout tracks...")
        for idx, (code, data) in enumerate(library.items(), 1):
            pex_id = f"PEX_{plan_id}_{code}"
            db.collection("plan_exercises").document(pex_id).set({
                "plan_exercise_id": pex_id,
                "plan_id": plan_id,
                "patient_id": patient_id,
                "exercise_name": data["name"],
                "exercise_code": code,
                "week_number": 3,
                "day_number": 2,
                "exercise_order": idx,
                "prescribed_sets": 3,
                "prescribed_reps": 10,
                "hold_duration_seconds": data["default_target_hold"],
                "rest_duration_seconds": 15,
                "expected_duration_minutes": 5,
                "target_rom_degrees": data["default_target_rom"],
                "target_accuracy_percentage": 85.0,
                "difficulty_rating": "Medium" if code == "EX_LN" else "Easy",
                "is_mandatory": True,
                "random_forest_model_name": data["random_forest_model"],
                "clinical_notes": "Maintain strict hip centering symmetry during extension phases.",
                "created_at": now - timedelta(days=18),
                "updated_at": now - timedelta(days=18)
            })

        # ===========================================================================
        # 5. SEED HISTORICAL RECOVERY PROGRESS CHART RECORDS
        # ===========================================================================
        print("⚡ Seeding 'recovery_progress' baseline time-series curves...")
        for i in range(5):
            log_date = now - timedelta(days=4-i)
            prog_id = f"PRG_{patient_id}_{log_date.strftime('%Y%m%d')}"
            db.collection("recovery_progress").document(prog_id).set({
                "progress_id": prog_id,
                "patient_id": patient_id,
                "log_date": log_date.isoformat(),
                "recovery_score": 75.0 + (i * 1.4),
                "recovery_trend": "Improving",
                "rom_progress": 85.0 + (i * 2.2),
                "correct_rep_percentage": 80.0 + (i * 2.5),
                "average_session_score": 78.0 + (i * 1.8),
                "interval_type": "Daily",
                "current_phase": "Phase I"
            })

        # ===========================================================================
        # 6. SEED DYNAMIC GLOBAL AGGREGATED ANALYTICS CARD
        # ===========================================================================
        print("⚡ Seeding 'analytics' profile summary blocks...")
        db.collection("analytics").document(f"ANL_{patient_id}").set({
            "analytics_id": f"ANL_{patient_id}",
            "patient_id": patient_id,
            "total_sessions": 14,
            "current_streak": 6,
            "exercises_completed": 42,
            "average_recovery": 82.0,
            "average_rom": 96.0,
            "average_correct_percentage": 88.5,
            "weekly_exercise_time_seconds": 4368,
            "monthly_exercise_time_seconds": 18450,
            "last_updated_at": now.isoformat()
        })

        # ===========================================================================
        # 7. SEED NOTIFICATIONS SUMMARY MATRIX
        # ===========================================================================
        print("⚡ Seeding 'notifications' transaction data nodes...")
        db.collection("notifications").document(f"NTF_INIT_MOCK").set({
            "notification_id": "NTF_INIT_MOCK",
            "patient_id": patient_id,
            "type": "Recovery Sync Alert",
            "title": "V1 ML Core Active! 🎯",
            "message": "Independent classifiers for Lunge, STS, and ASLR successfully mounted to the ingestion endpoints.",
            "is_read": False,
            "timestamp": now.isoformat()
        })  

        print("\n🎉 SUCCESS: Database completely re-seeded and aligned for your presentation layout flow!")

    except Exception as e:
        print(f"❌ Exception intercepted during seeding run: {e}")
        sys.exit(1)


if __name__ == "__main__":
    seed_production_database()