# test_sprint1_day6.py
import pytest
import numpy as np
from ai.utils import RehabAIOrchestrator

def test_orchestrator_initialization_and_base_rendering():
    # 1. Initialize our orchestrator block target bound to the Heel Slide schema
    orchestrator = RehabAIOrchestrator(exercise_name="HEEL_SLIDE", tracking_side="left")
    
    # 2. Allocate a standard simulated blank canvas frame matrix array (480x640x3 BGR frame image)
    simulated_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # 3. Process the frame through the entire integrated pipeline
    ui_frame, analytics, feedback = orchestrator.process_frame_pipeline(simulated_frame)
    
    # 4. Run validation checks on structural outputs
    assert ui_frame.shape == (480, 640, 3)
    assert isinstance(analytics, dict)
    assert "session_compliance_score" in analytics
    assert isinstance(feedback, str)
    
    # Ensure standard zeroed fallback logic holds correctly when no tracking landmarks are detected
    assert analytics["session_compliance_score"] == 100.0
    assert "Positioning body" in feedback
    
    # Clean up native context processing allocation structures
    orchestrator.release_context()

if __name__ == "__main__":
    print("Run via terminal: pytest test_sprint1_day6.py")