# frontend/utils/mock_data.py
import datetime

_today = datetime.date.today()

DASHBOARD_STATS_MOCK = {
    "kpis": {
        "recovery_score": {"value": 84, "max_value": 100, "delta": "+6%", "status": "normal"},
        "movement_quality": {"value": 91, "max_value": 100, "delta": "+3%", "status": "normal"},
        "range_of_motion": {"value": 88, "unit": "degrees", "delta": "+5°", "status": "normal"},
        "pain_score": {"value": 2, "max_value": 10, "delta": "-1", "status": "inverse"}
    },
    "vitals": {"active_patients": 18, "sessions_today": 42, "critical_alerts": 3},
    "system_status": {"ai_engine": "Online", "backend_connected": True, "database_connected": True}
}

PATIENTS_MOCK = [
    {"id": 1, "name": "John Doe", "age": 42, "gender": "Male", "injury": "ACL Reconstruction", "metrics_summary": {"recovery_score": "84/100", "pain_score": "2/10", "rom": "88° / 120°"}, "status": "🟢 Improving"},
    {"id": 2, "name": "Jane Smith", "age": 29, "gender": "Female", "injury": "Rotator Cuff Tear", "metrics_summary": {"recovery_score": "91/100", "pain_score": "1/10", "rom": "165° / 180°"}, "status": "🟢 Improving"},
    {"id": 3, "name": "Robert Chen", "age": 61, "gender": "Male", "injury": "Total Knee Arthroplasty", "metrics_summary": {"recovery_score": "68/100", "pain_score": "4/10", "rom": "78° / 110°"}, "status": "🟡 Stable"},
    {"id": 4, "name": "Sarah Jenkins", "age": 35, "gender": "Female", "injury": "Ankle Sprain", "metrics_summary": {"recovery_score": "95/100", "pain_score": "0/10", "rom": "42° / 45°"}, "status": "🟢 Improving"},
    {"id": 5, "name": "Michael Brown", "age": 50, "gender": "Male", "injury": "Stroke Recovery", "metrics_summary": {"recovery_score": "72/100", "pain_score": "3/10", "rom": "70% Function"}, "status": "🔴 Attention Needed"},
    {"id": 6, "name": "Elena Rostova", "age": 27, "gender": "Female", "injury": "Achilles Tendonitis", "metrics_summary": {"recovery_score": "59/100", "pain_score": "5/10", "rom": "30° / 50°"}, "status": "🟡 Stable"}
]

TRENDS_MOCK = {
    "sessions": [f"Sess {i}" for i in range(1, 13)],
    "weeks": ["Wk 1", "Wk 2", "Wk 3", "Wk 4", "Wk 5", "Wk 6"],
    "recovery_series": [60, 62, 65, 68, 70, 72, 75, 76, 78, 80, 82, 84],
    "pain_series": [8, 7, 7, 6, 5, 5, 4, 3, 3, 2, 2, 2],
    "movement_quality_series": [78, 80, 81, 83, 85, 84, 88, 89, 91, 90, 92, 91],
    "rom_series": [65, 68, 70, 72, 75, 78, 80, 82, 85, 86, 88, 88],
    "exercise_distribution": {"completed": [24, 26, 28, 30, 32, 35], "missed": [4, 3, 2, 1, 1, 0]}
}

RECOMMENDATIONS_MOCK = [
    {"id": 1, "patient_name": "John Doe", "current_biometrics": {"recovery_score": "84/100", "pain_index": "2/10"}, "directive": "Increase extension ceiling by 5° and establish higher pacing consistency.", "confidence_percentage": 94.2, "priority": "High", "status": "Pending"},
    {"id": 2, "patient_name": "Jane Smith", "current_biometrics": {"recovery_score": "91/100", "pain_index": "1/10"}, "directive": "Transition baseline resistance to Level 2 bands; maintain 12 structural reps.", "confidence_percentage": 89.5, "priority": "Medium", "status": "Approved"}
]

SESSIONS_MOCK = [
    {
        "date": (_today - datetime.timedelta(days=i)).strftime("%Y-%m-%d"),
        "exercise_name": name, "rom_range": rom, "recovery_score": score, "pain_index": pain, "assigned_directive": directive
    }
    for i, (name, rom, score, pain, directive) in enumerate(zip(
        ["Knee Extension", "Knee Extension", "Squats (Assisted)", "Squats (Assisted)", "Leg Press"],
        ["120° / 5°", "118° / 5°", "95° / 0°", "90° / 0°", "100° / 10°"],
        [84, 82, 80, 79, 76], ["2 / 10", "3 / 10", "3 / 10", "4 / 10", "4 / 10"],
        ["Increase flexion target by 5°", "Maintain current velocity profile", "Add load resistance (+2kg)", "Hold terminal extension 2s longer", "Reduce depth variation"]
    ))
]