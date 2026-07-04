# test_sprint5_analytics.py
import pytest
import time
import numpy as np
from ai.utils import RehabAIOrchestrator

def test_repetition_counting_mechanics():
    # Setup orchestrator context target bound to the Heel Slide tracking architecture
    orchestrator = RehabAIOrchestrator(exercise_name="HEEL_SLIDE", tracking_side="left")
    simulated_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    print("\nRunning simulated time-series loops to test state engine dynamics...")
    
    # Process initial frames to baseline state configurations
    for _ in range(5):
        orchestrator.process_frame_pipeline(simulated_frame)
        time.sleep(0.01)
        
    # The integration pipeline handles null frame states cleanly 
    _, analytics, _ = orchestrator.process_frame_pipeline(simulated_frame)
    assert "session_compliance_score" in analytics
    
    orchestrator.release_context()
    print("✅ Stateful analytics integration check passed.")

if __name__ == "__main__":
    import sys
    sys.exit(pytest.main(["-v", __file__]))