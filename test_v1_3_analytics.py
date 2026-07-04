# test_v1_3_analytics.py
"""
RehabAI v1.3.0 Analytics Engine Validation Test Suite
"""

import pytest
from ai.analytics_engine import ClinicalAnalyticsEngine

def test_statistical_matrix_compilation():
    # Setup mock historical time-series logs
    mock_statuses = ["GREEN"] * 80 + ["YELLOW"] * 10 + ["RED"] * 10  # 100 frames total
    mock_angles = [30.0] * 50 + [60.0] * 50
    mock_speeds = [10.0] * 100
    
    summary = ClinicalAnalyticsEngine.calculate_session_analytics(
        status_history=mock_statuses,
        metric_history=mock_angles,
        velocity_history=mock_speeds,
        exercise_name="Mini Squat",
        exercise_id="EX-004",
        total_reps=5,
        feedback_instruction="Good control."
    )
    
    # Run assertions against research compliance thresholds
    assert summary["total_repetitions"] == 5
    assert summary["rom_stats"]["max"] == 60.0
    assert summary["rom_stats"]["mean"] == 45.0
    assert summary["zone_distribution"]["GREEN_PCT"] == 80.0
    assert summary["zone_distribution"]["RED_PCT"] == 10.0
    assert summary["session_compliance_score"] < 100.0
    
    print("✅ Analytics engine metric scaling confirmed.")

if __name__ == "__main__":
    import sys
    sys.exit(pytest.main(["-v", __file__]))