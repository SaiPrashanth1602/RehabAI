"""
RehabAI Dynamic Rule-Based Decision Module
Sprint 7.1 Component - Universal Multi-Phase Clinical Boundary Evaluator

Parses serialized real-time kinematics vectors against dynamic thresholds
loaded straight out of config registries based on patient recovery timelines.
"""

import numpy as np
from typing import Dict, Any, List

class RulePredictor:
    def __init__(self, exercise_config: Dict[str, Any], patient_phase: int = 1):
        """Initializes boundary structures bound to configuration matrices and target phase profiles."""
        self.config = exercise_config
        self.feature_order: List[str] = exercise_config["features"]
        self.ex_id = self.config.get("id", "")
        
        # Clamp patient phase boundaries to valid structural domains [1, 2, 3]
        self.phase = max(1, min(3, int(patient_phase)))
        self.thresholds = self.config.get("phase_thresholds", {}).get(self.phase, {})

    def predict(self, feature_vector: np.ndarray) -> str:
        """
        Parses dense float feature matrices against dynamic phase boundaries.
        Returns: 'GREEN', 'YELLOW', or 'RED' safety status metrics.
        """
        if feature_vector is None or len(feature_vector) == 0:
            return "RED"
            
        f_map = dict(zip(self.feature_order, feature_vector.tolist()))

        # 1️⃣ EX-001: HEEL_SLIDE Routing Logic
        if self.ex_id == "EX-001":
            val = f_map.get("knee_flexion_angle", 0.0)
            limits = self.thresholds.get("knee_flexion_angle", [90.0, 100.0])
            return "RED" if val > limits[1] else "YELLOW" if val > limits[0] else "GREEN"
            
        # 2️⃣ EX-002: STRAIGHT_LEG_RAISE Routing Logic
        elif self.ex_id == "EX-002":
            lag = f_map.get("extensor_lag_angle", 0.0)
            hip = f_map.get("hip_flexion_angle", 0.0)
            
            lag_limits = self.thresholds.get("extensor_lag_angle", [1.5, 3.0])
            hip_limits = self.thresholds.get("hip_flexion_angle", [45.0, 55.0])
            
            if lag > lag_limits[1] or hip > hip_limits[1]:
                return "RED"
            elif lag > lag_limits[0] or hip > hip_limits[0]:
                return "YELLOW"
            return "GREEN"
            
        # 3️⃣ EX-003: LONG_ARC_QUAD Routing Logic
        elif self.ex_id == "EX-003":
            dev = f_map.get("terminal_extension_deviation", 0.0)
            limits = self.thresholds.get("terminal_extension_deviation", [5.0, 15.0])
            return "RED" if dev > limits[1] else "YELLOW" if dev > limits[0] else "GREEN"
            
        # 4️⃣ EX-004: MINI_SQUAT Routing Logic
        elif self.ex_id == "EX-004":
            dep = f_map.get("knee_flexion_depth", 0.0)
            vlg = f_map.get("frontal_plane_knee_projection_angle", 0.0)
            
            dep_limits = self.thresholds.get("knee_flexion_depth", [60.0, 75.0])
            vlg_limits = self.thresholds.get("frontal_plane_knee_projection_angle", [10.0, 15.0])
            
            if dep > dep_limits[1] or vlg > vlg_limits[1]:
                return "RED"
            elif dep > dep_limits[0] or vlg > vlg_limits[0]:
                return "YELLOW"
            return "GREEN"
            
        # 5️⃣ EX-005: SIT_TO_STAND Routing Logic
        elif self.ex_id == "EX-005":
            trunk = f_map.get("trunk_flexion_angle", 0.0)
            limits = self.thresholds.get("trunk_flexion_angle", [35.0, 45.0])
            return "RED" if trunk > limits[1] else "YELLOW" if trunk > limits[0] else "GREEN"

        return "GREEN"