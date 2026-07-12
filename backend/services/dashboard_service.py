from backend.services.patient_service import patient_service
from backend.services.session_service import session_service


class DashboardService:

    def get_dashboard(self, patient_id):
        # CHANGED: Match the actual method name in session_service.py
        sessions = session_service.list_patient_sessions(patient_id)

        if len(sessions) == 0:
            return {
                "patient_id": patient_id,
                "exercise": "",
                "status": "WAITING_FOR_SETUP",
                "rep_count": 0,
                "rom": 0.0,
                "movement_quality": 0.0,
                "recovery_score": 0.0,
                "recovery_deviation": 0.0,
                "trend": "N/A",
                "recommendation": "No rehabilitation sessions available."
            }

        latest = sessions[0]

        return {
            "patient_id": latest.get("patient_id", patient_id),
            "exercise": latest.get("exercise_name", ""),
            "status": latest.get("status", "Unknown"),
            "rep_count": latest.get("rep_count", 0),
            "rom": latest.get("rom", 0.0),
            "movement_quality": latest.get("movement_quality", 0.0),
            "recovery_score": latest.get("recovery_score", 0.0),
            "recovery_deviation": latest.get("recovery_deviation", 0.0),
            "trend": latest.get("trend", "N/A"),
            "recommendation": latest.get("recommendation", "")
        }

    def get_overview(self):
        patients = patient_service.get_all_patients()
        
        # CHANGED: Safely fall back to an empty list if get_all_sessions doesn't exist yet
        try:
            sessions = session_service.get_all_sessions()
        except AttributeError:
            sessions = []

        total_patients = len(patients)
        total_sessions = len(sessions)

        if total_sessions == 0:
            return {
                "total_patients": total_patients,
                "total_sessions": 0,
                "average_recovery_score": 0,
                "average_movement_quality": 0,
                "average_rom": 0,
                "active_patients": 0
            }

        avg_recovery = sum(
            s.get("recovery_score", 0) for s in sessions
        ) / total_sessions

        avg_quality = sum(
            s.get("movement_quality", 0) for s in sessions
        ) / total_sessions

        avg_rom = sum(
            s.get("rom", 0) for s in sessions
        ) / total_sessions

        return {
            "total_patients": total_patients,
            "total_sessions": total_sessions,
            "average_recovery_score": round(avg_recovery, 1),
            "average_movement_quality": round(avg_quality, 1),
            "average_rom": round(avg_rom, 1),
            "active_patients": total_patients
        }


dashboard_service = DashboardService()