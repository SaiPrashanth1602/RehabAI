# test_sprint1_day4.py
import pytest
import numpy as np
from ai.exercise_config import get_exercise_config
from ai.feature_vector import FeatureVectorPipeline
from ai.predictor import RulePredictor

def test_heel_slide_vector_and_prediction():
    config = get_exercise_config("HEEL_SLIDE")
    
    # Setup a mock frame dictionary containing a safe flexion angle
    mock_features = {
        "knee_flexion_angle": 75.0,
        "range_of_motion": 75.0,
        "angular_velocity": 5.0,
        "movement_quality_index": 1.0
    }
    
    # 1. Verify serialization order and type formatting
    vector = FeatureVectorPipeline.serialize_features(mock_features, config["features"])
    assert isinstance(vector, np.ndarray)
    assert vector[0] == 75.0  # First element must be knee_flexion_angle per config
    
    # 2. Test predictable rule bounds (Safe execution zone)
    predictor = RulePredictor(config)
    assert predictor.predict(vector) == "GREEN"

def test_heel_slide_red_zone_violation():
    config = get_exercise_config("HEEL_SLIDE")
    
    # Setup a mock frame dictionary exceeding early structural limits (110 degrees)
    mock_features = {
        "knee_flexion_angle": 110.0,
        "range_of_motion": 110.0,
        "angular_velocity": 2.0,
        "movement_quality_index": 1.0
    }
    
    vector = FeatureVectorPipeline.serialize_features(mock_features, config["features"])
    predictor = RulePredictor(config)
    
    # Must immediately trigger an automated safety alert flag
    assert predictor.predict(vector) == "RED"

if __name__ == "__main__":
    print("Run via terminal: pytest test_sprint1_day4.py")