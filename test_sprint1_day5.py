# test_sprint1_day5.py
import pytest
from ai.recovery_engine import RecoveryEngine
from ai.recommendation_engine import RecommendationEngine

def test_analytics_and_feedback_integration():
    # 1. Simulate a session with minor control issues (mostly green with some yellow warnings)
    mock_status_history = ["GREEN"] * 40 + ["YELLOW"] * 10
    mock_angles = [60.0 + (i * 0.5) for i in range(50)] # Gradually increasing range
    
    analytics = RecoveryEngine.evaluate_session_performance(mock_status_history, mock_angles)
    
    assert analytics["session_compliance_score"] == 85.0  # 100 - (10 * 1.5)
    assert analytics["peak_range_of_motion"] == 84.5
    assert analytics["performance_trend"] == "IMPROVING"
    
    # 2. Verify that feedback systems provide guidance under good form conditions
    mock_current_features = {"knee_flexion_angle": 80.0}
    feedback = RecommendationEngine.generate_feedback(mock_current_features, analytics)
    assert "form" in feedback or "control" in feedback

def test_critical_safety_feedback_trigger():
    # Simulate a high-risk session with severe early over-flexion (multiple red flags)
    mock_status_history = ["GREEN"] * 10 + ["RED"] * 8
    mock_angles = [70.0] * 10 + [105.0] * 8
    
    analytics = RecoveryEngine.evaluate_session_performance(mock_status_history, mock_angles)
    
    # Verify that a high volume of red flags correctly drops the compliance score
    assert analytics["session_compliance_score"] < 70.0
    
    mock_current_features = {"knee_flexion_angle": 105.0}
    feedback = RecommendationEngine.generate_feedback(mock_current_features, analytics)
    
    # The system must immediately output an explicit stop instruction
    assert "Halt session" in feedback

if __name__ == "__main__":
    print("Run via terminal: pytest test_sprint1_day5.py")