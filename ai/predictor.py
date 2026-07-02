from ai.movement_engine import RehabFeatureExtractor
from ai.recovery_engine import RecoveryIntelligenceEngine
from ai.deviation_engine import DeviationAnalysisEngine

class RehabPredictor:
    def __init__(self):
        self.ai = RehabFeatureExtractor()
        self.rec = RecoveryIntelligenceEngine()
        self.dev = DeviationAnalysisEngine()

    def get_analysis(self, landmarks):
        joints = self.ai.extract_joints(landmarks)
        
        if joints is None:
            return {
                "status": "WAITING_FOR_SETUP", "rep_count": 0, "rom": 0.0, "movement_quality": 0.0,
                "recovery_score": 0.0, "recovery_deviation": 0.0, "trend": "N/A",
                "recommendation": "Please stand back and ensure full leg is visible."
            }
            
        sh_coord = [landmarks[12].x, landmarks[12].y, landmarks[12].z]
        ft_coord = [landmarks[30].x, landmarks[30].y, landmarks[30].z]
        
        feat = self.ai.process_frame(joints[0], joints[1], joints[2], shoulder=sh_coord, foot=ft_coord)
        ris = self.rec.calculate_ris(feat['rom'], feat.get('movement_smoothness', 1.0), feat['rep_count'], 5, 3)
        analysis = self.dev.analyze_trajectory(ris, 65.0, 70.0)
        
        comp_pct = min(feat['rep_count'] / 5, 1.0) * 100
        total_attempts = feat['rep_count'] + feat.get('failed_reps', 0)
        succ_rate = f"{round((feat['rep_count'] / total_attempts) * 100, 1)}%" if total_attempts > 0 else "N/A"

        return {
            "status": self.ai.state,
            "recommendation": analysis['recommendation'],
            "recovery_score": ris,
            "recovery_deviation": analysis['deviation'],
            "trend": analysis['trend'],
            
            # --- downstream mapping properties expansion ---
            "knee_angle": feat.get('knee_angle', feat['angle']),
            "hip_angle": feat.get('hip_angle', 170.0),
            "ankle_angle": feat.get('ankle_angle', 110.0),
            "rom": feat['rom'],
            "peak_flexion": feat.get('peak_flexion', feat['angle']),
            "peak_extension": feat.get('peak_extension', feat['angle']),
            "angular_velocity": feat.get('angular_velocity', 0.0),
            "angular_acceleration": feat.get('angular_acceleration', 0.0),
            "peak_velocity": feat.get('peak_velocity', 0.0),
            "average_velocity": feat.get('average_velocity', 0.0),
            "rep_count": feat['rep_count'],
            "rep_duration": feat.get('rep_duration', 0.0),
            "hold_duration": feat.get('hold_duration', 0.0),
            "average_rep_time": feat.get('average_rep_time', 0.0),
            "exercise_time": feat.get('exercise_time', 0.0),
            "rest_time": feat.get('rest_time', 0.0),
            "time_under_tension": feat.get('time_under_tension', 0.0),
            "movement_quality": feat['movement_quality'],
            "movement_smoothness": feat.get('movement_smoothness', 1.0),
            "rom_consistency": feat.get('rom_consistency', 1.0),
            "exercise_completion": comp_pct,
            "success_rate": succ_rate,
            "failed_rep_count": feat.get('failed_reps', 0),
            "limb_symmetry_index": "NOT AVAILABLE (Requires Bilateral Leg Tracking)"
        }