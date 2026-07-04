# test_v1_core_release.py
"""
RehabAI Core v1.0.0 - Release Candidate Final Verification Suite
Tests integrated state tracking, visibility safety bypasses, and rule prediction.
"""

import pytest
import numpy as np
import time
from ai.utils import RehabAIOrchestrator
from ai.feature_engineering import FeatureEngineering

class MockLandmarkList:
    def __init__(self, x, y, z, visibility):
        self.x = x
        self.y = y
        self.z = z
        self.visibility = visibility

def generate_mock_pose(hip_xyz, knee_xyz, ankle_xyz, visibility=0.99):
    """Generates a complete mock MediaPipe landmark list array for pipeline routing."""
    mock_list = [MockLandmarkList(0.0, 0.0, 0.0, 0.0)] * 33
    # Map index constraints matching exercise_config.py
    mock_list[23] = MockLandmarkList(hip_xyz[0], hip_xyz[1], hip_xyz[2], visibility)     # Left Hip
    mock_list[24] = MockLandmarkList(hip_xyz[0], hip_xyz[1], hip_xyz[2], visibility)     # Right Hip
    mock_list[25] = MockLandmarkList(knee_xyz[0], knee_xyz[1], knee_xyz[2], visibility)   # Left Knee
    mock_list[26] = MockLandmarkList(knee_xyz[0], knee_xyz[1], knee_xyz[2], visibility)   # Right Knee
    mock_list[27] = MockLandmarkList(ankle_xyz[0], ankle_xyz[1], ankle_xyz[2], visibility) # Left Ankle
    mock_list[28] = MockLandmarkList(ankle_xyz[0], ankle_xyz[1], ankle_xyz[2], visibility) # Right Ankle
    return mock_list

def test_v1_release_mini_squat_safety_guardrails(monkeypatch):
    """Verifies that a dangerous dynamic valgus knee collapse triggers a RED status alert."""
    orchestrator = RehabAIOrchestrator(exercise_name="MINI_SQUAT", tracking_side="left")
    simulated_image = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Pre-load a mock pose frame displaying clear dynamic valgus alignment collapse
    mock_pose = generate_mock_pose(
        hip_xyz=(0.5, 0.2, 0.0),
        knee_xyz=(0.7, 0.5, 0.0), # Extreme lateral knee shift creating a massive slope angle
        ankle_xyz=(0.5, 0.8, 0.0)
    )
    
    # Intercept raw MediaPipe processing engine output
    monkeypatch.setattr(orchestrator.engine, "process_frame", lambda f: mock_pose)
    
    ui_frame, analytics, feedback = orchestrator.process_frame_pipeline(simulated_image)
    
    # Assert system catches the tracking failure and triggers a safety override
    assert "Watch knee positioning" in feedback or "Halt session" in feedback
    orchestrator.release_context()

def test_v1_release_low_visibility_bypass(monkeypatch):
    """Verifies that low-visibility tracking frames safely bypass calculations without crashing."""
    orchestrator = RehabAIOrchestrator(exercise_name="HEEL_SLIDE", tracking_side="left")
    simulated_image = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Generate mock data with low visibility tracking (0.30 confidence score)
    poor_pose = generate_mock_pose((0.5, 0.2, 0.0), (0.5, 0.5, 0.0), (0.5, 0.8, 0.0), visibility=0.30)
    monkeypatch.setattr(orchestrator.engine, "process_frame", lambda f: poor_pose)
    
    ui_frame, analytics, feedback = orchestrator.process_frame_pipeline(simulated_image)
    
    # Compliance score must remain safe and clear instruction text must flag user positioning
    assert analytics["session_compliance_score"] == 100.0
    assert "TRACKING WARNING" in feedback
    orchestrator.release_context()

if __name__ == "__main__":
    import sys
    sys.exit(pytest.main(["-v", __file__]))