"""
RehabAI Real-Time Patient Feedback Engine
Sprint 2 Component - Universal 5-Exercise Biofeedback Logic
"""

from typing import Dict, Any

class RecommendationEngine:
    @staticmethod
    def generate_feedback(ex_id: str, features: Dict[str, Any], analytics: Dict[str, Any]) -> str:
        if analytics.get("critical_violation_count", 0) > 3 or analytics.get("session_compliance_score", 100.0) < 70.0:
            return "Halt session. Excessive alignment deviations detected. Please rest."

        if ex_id == "EX-001":
            return "Upper safety limit approached. Ease back." if features.get("knee_flexion_angle", 0.0) > 95.0 else "Good control. Maintain smooth pacing."
        elif ex_id == "EX-002":
            return "Keep knee locked! Eliminate flexion lag." if features.get("extensor_lag_angle", 0.0) > 2.0 else "Excellent locked elevation extension."
        elif ex_id == "EX-003":
            return "Focus on complete straight extension." if features.get("terminal_extension_deviation", 0.0) > 5.0 else "Perfect terminal quadriceps squeeze."
        elif ex_id == "EX-004":
            return "Watch knee positioning! Avoid valgus buckle." if features.get("frontal_plane_knee_projection_angle", 0.0) > 10.0 else "Squat tracking is perfectly aligned."
        elif ex_id == "EX-005":
            return "Avoid excessive forward leaning." if features.get("trunk_flexion_angle", 0.0) > 35.0 else "Stand up evenly using both legs."
            
        return "Maintain current form pacing."