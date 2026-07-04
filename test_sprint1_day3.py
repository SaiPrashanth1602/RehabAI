# test_sprint1_day3.py
import pytest
from ai.feature_engineering import FeatureEngineering

def test_perfect_right_angle_flexion():
    # Setup standard perpendicular coordinate plane mapping
    # Hip at origin (0,0,0), Knee extended forward horizontally (1,0,0), Ankle dropped down vertically (1,-1,0)
    # This forms a perfect 90 degree corner vector at the knee point vertex.
    mock_extracted = {
        "hip": {"left": (0.0, 0.0, 0.0, 0.99)},
        "knee": {"left": (1.0, 0.0, 0.0, 0.99)},
        "ankle": {"left": (1.0, -1.0, 0.0, 0.99)}
    }
    
    features = FeatureEngineering.process_heel_slide_frame(mock_extracted, side="left")
    
    # 180 - 90 degree internal angle = 90 degrees of pure anatomical flexion
    assert features["knee_flexion_angle"] == 90.0
    assert features["range_of_motion"] == 90.0

def test_empty_input_handling():
    features = FeatureEngineering.process_heel_slide_frame({}, side="left")
    assert features["knee_flexion_angle"] == 0.0

if __name__ == "__main__":
    print("Run via terminal: pytest test_sprint1_day3.py")