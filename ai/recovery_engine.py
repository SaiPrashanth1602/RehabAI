"""
RehabAI Session Recovery Analytics Engine
Sprint 2 Component
"""

from typing import List, Dict, Any
import numpy as np

class RecoveryEngine:
    @staticmethod
    def evaluate_session_performance(status_history: List[str], metric_history: List[float]) -> Dict[str, Any]:
        analytics = {"session_compliance_score": 100.0, "peak_metric": 0.0, "performance_trend": "STABLE", "critical_violation_count": 0}
        if not status_history:
            return analytics
            
        red = status_history.count("RED")
        yellow = status_history.count("YELLOW")
        analytics["critical_violation_count"] = red
        
        compliance = max(0.0, 100.0 - ((red * 5.0) + (yellow * 1.5)))
        analytics["session_compliance_score"] = round(compliance, 1)
        
        if metric_history:
            analytics["peak_metric"] = float(np.max(metric_history))
        return analytics