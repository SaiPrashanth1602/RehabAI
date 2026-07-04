# test_sprint1_day2.py
import pytest
from collections import namedtuple
from ai.landmark_extractor import LandmarkExtractor
from ai.exercise_config import get_exercise_config

# Mock landmark object matching MediaPipe landmark field signature
MockLandmark = namedtuple('MockLandmark', ['x', 'y', 'z', 'visibility'])

@pytest.fixture
def dummy_mediapipe_output():
    # Generate 33 sequential dummy coordinates
    return [MockLandmark(x=float(i), y=float(i*2), z=float(i*3), visibility=0.99) for i in range(33)]

def test_landmark_extractor_filtering(dummy_mediapipe_output):
    # Fetch configurations for a Heel Slide exercise
    config = get_exercise_config("HEEL_SLIDE")
    required_joints = config["landmarks"] # ['hip', 'knee', 'ankle']
    
    extracted = LandmarkExtractor.extract_required_landmarks(dummy_mediapipe_output, required_joints)
    
    # Assert structural keys map correctly
    assert "hip" in extracted
    assert "knee" in extracted
    assert "ankle" in extracted
    assert "shoulder" not in extracted # Leak validation
    
    # Verify accurate index alignment (Hip left index is 23)
    assert extracted["hip"]["left"][0] == 23.0
    assert extracted["hip"]["left"][1] == 46.0

def test_empty_landmark_handling():
    extracted = LandmarkExtractor.extract_required_landmarks(None, ["hip"])
    assert extracted == {}

if __name__ == "__main__":
    print("Run via terminal: pytest test_sprint1_day2.py")