# test_sprint7_phase_rules.py
"""
RehabAI Multi-Phase Rule Verification Suite
Sprint 7.1 Component - Boundary Shift Logic Testing
"""

import pytest
import numpy as np
from ai.exercise_config import get_exercise_config
from ai.feature_vector import FeatureVectorPipeline
from ai.predictor import RulePredictor

def test_phase_dependent_slr_threshold_shifting():
    config = get_exercise_config("STRAIGHT_LEG_RAISE")
    
    # --- Test Case 1: Extreme 65.0° Hip Flexion ---
    mock_features_high = {
        "hip_flexion_angle": 65.0,
        "extensor_lag_angle": 0.0,
        "angular_velocity": 0.0
    }
    vector_high = FeatureVectorPipeline.serialize_features(mock_features_high, config["features"])
    
    # Phase 1: 65° exceeds the absolute limit (Max 55°), must be RED
    phase1_predictor = RulePredictor(config, 1)
    assert phase1_predictor.predict(vector_high) == "RED"
    
    # Phase 2: 65° is acceptable but falls into the warning zone (60° - 75°), must be YELLOW
    phase2_predictor = RulePredictor(config, 2)
    assert phase2_predictor.predict(vector_high) == "YELLOW"
    
    # --- Test Case 2: Moderate 50.0° Hip Flexion ---
    mock_features_optimal = {
        "hip_flexion_angle": 50.0,
        "extensor_lag_angle": 0.0,
        "angular_velocity": 0.0
    }
    vector_optimal = FeatureVectorPipeline.serialize_features(mock_features_optimal, config["features"])
    
    # Phase 2: 50° is well below the 60° warning line, must return GREEN
    assert phase2_predictor.predict(vector_optimal) == "GREEN"
    
    print("✅ Multi-phase dynamic boundary shifts and warning bands confirmed!")

if __name__ == "__main__":
    import sys
    sys.exit(pytest.main(["-v", __file__]))