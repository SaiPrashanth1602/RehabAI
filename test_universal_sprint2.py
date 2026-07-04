# test_universal_sprint2.py
import pytest
import numpy as np
from ai.utils import RehabAIOrchestrator
from ai.exercise_config import EXERCISE_REGISTRY

def test_all_five_exercises_pipeline():
    simulated_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    for exercise_key in EXERCISE_REGISTRY.keys():
        print(f"Verifying system loop orchestration pipeline for: {exercise_key}")
        orchestrator = RehabAIOrchestrator(exercise_name=exercise_key, tracking_side="left")
        
        ui_frame, analytics, feedback = orchestrator.process_frame_pipeline(simulated_frame)
        
        assert ui_frame.shape == (480, 640, 3)
        assert "session_compliance_score" in analytics
        assert isinstance(feedback, str)
        
        orchestrator.release_context()

if __name__ == "__main__":
    print("Run via terminal command: pytest test_universal_sprint2.py")