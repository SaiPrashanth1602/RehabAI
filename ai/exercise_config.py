"""
RehabAI Exercise Configuration Registry
Sprint 7.1 Component - Multi-Phase Dynamic Schema Configuration

Defines landmark mappings and variable phase-dependent threshold matrices.
"""

from typing import Dict, Any, List

MEDIAPIPE_LANDMARK_MAP: Dict[str, List[int]] = {
    "shoulder": [11, 12],
    "hip": [23, 24],
    "knee": [25, 26],
    "ankle": [27, 28]
}

EXERCISE_REGISTRY: Dict[str, Dict[str, Any]] = {
    "HEEL_SLIDE": {
        "id": "EX-001",
        "name": "Heel Slide",
        "landmarks": ["hip", "knee", "ankle"],
        "features": ["knee_flexion_angle", "range_of_motion", "angular_velocity"],
        "predictor_type": "rule_based",
        # Phase-dependent safety limits mapping [Yellow_Threshold, Red_Threshold]
        "phase_thresholds": {
            1: {"knee_flexion_angle": [90.0, 100.0]},   # Phase I: Max 100 deg to protect early graft
            2: {"knee_flexion_angle": [110.0, 120.0]}, # Phase II: Increased mobility goals
            3: {"knee_flexion_angle": [125.0, 140.0]}  # Phase III: Full structural return
        }
    },
    "STRAIGHT_LEG_RAISE": {
        "id": "EX-002",
        "name": "Straight Leg Raise",
        "landmarks": ["hip", "knee", "ankle"],
        "features": ["hip_flexion_angle", "extensor_lag_angle", "angular_velocity"],
        "predictor_type": "rule_based",
        "phase_thresholds": {
            1: {"extensor_lag_angle": [1.5, 3.0], "hip_flexion_angle": [45.0, 55.0]},  # Phase I Limits
            2: {"extensor_lag_angle": [1.0, 2.0], "hip_flexion_angle": [60.0, 75.0]},  # Phase II Limits
            3: {"extensor_lag_angle": [0.5, 1.0], "hip_flexion_angle": [80.0, 95.0]}   # Phase III Limits
        }
    },
    "LONG_ARC_QUAD": {
        "id": "EX-003",
        "name": "Long Arc Quad",
        "landmarks": ["hip", "knee", "ankle"],
        "features": ["knee_extension_angle", "terminal_extension_deviation", "angular_velocity"],
        "predictor_type": "rule_based",
        "phase_thresholds": {
            1: {"terminal_extension_deviation": [5.0, 15.0]},
            2: {"terminal_extension_deviation": [3.0, 10.0]},
            3: {"terminal_extension_deviation": [1.0, 5.0]}
        }
    },
    "MINI_SQUAT": {
        "id": "EX-004",
        "name": "Mini Squat",
        "landmarks": ["hip", "knee", "ankle"],
        "features": ["knee_flexion_depth", "frontal_plane_knee_projection_angle", "angular_velocity"],
        "predictor_type": "rule_based",
        "phase_thresholds": {
            1: {"knee_flexion_depth": [60.0, 75.0], "frontal_plane_knee_projection_angle": [10.0, 15.0]},
            2: {"knee_flexion_depth": [75.0, 90.0], "frontal_plane_knee_projection_angle": [8.0, 12.0]},
            3: {"knee_flexion_depth": [90.0, 110.0], "frontal_plane_knee_projection_angle": [5.0, 8.0]}
        }
    },
    "SIT_TO_STAND": {
        "id": "EX-005",
        "name": "Sit to Stand",
        "landmarks": ["shoulder", "hip", "knee", "ankle"],
        "features": ["knee_flexion_angle", "trunk_flexion_angle", "angular_velocity"],
        "predictor_type": "rule_based",
        "phase_thresholds": {
            1: {"trunk_flexion_angle": [35.0, 45.0]},
            2: {"trunk_flexion_angle": [30.0, 40.0]},
            3: {"trunk_flexion_angle": [25.0, 35.0]}
        }
    }
}

def get_exercise_config(exercise_name: str) -> Dict[str, Any]:
    upper_key = exercise_name.upper()
    if upper_key not in EXERCISE_REGISTRY:
        raise KeyError(f"Exercise '{exercise_name}' is not registered in RehabAI core config.")
    return EXERCISE_REGISTRY[upper_key]