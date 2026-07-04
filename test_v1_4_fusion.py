# test_v1_4_fusion.py
"""
RehabAI v1.4.0 Decision Fusion Engine Validation Test Suite
"""

import pytest
from ai.fusion_engine import ClinicalFusionEngine

def test_hierarchical_safety_fusion_matrix():
    fusion_unit = ClinicalFusionEngine(confidence_threshold=0.75)

    # Test 1: Rule Engine Circuit Breaker Override
    res1 = fusion_unit.evaluate_fused_decision(rule_status="RED", ml_status="GREEN", ml_confidence=0.99)
    assert res1["status"] == "RED"
    assert res1["source"] == "rule_safety_override"

    # Test 2: High-Confidence Predictive Intelligence Escalation
    res2 = fusion_unit.evaluate_fused_decision(rule_status="GREEN", ml_status="YELLOW", ml_confidence=0.85)
    assert res2["status"] == "YELLOW"
    assert res2["source"] == "ml_predictive_intelligence"

    # Test 3: Low-Confidence ML Noise Suppression
    res3 = fusion_unit.evaluate_fused_decision(rule_status="GREEN", ml_status="YELLOW", ml_confidence=0.52)
    assert res3["status"] == "GREEN"
    assert res3["source"] == "low_confidence_ml_suppression"

    # Test 4: Conservative Risk Escalation
    res4 = fusion_unit.evaluate_fused_decision(rule_status="YELLOW", ml_status="RED", ml_confidence=0.90)
    assert res4["status"] == "RED"
    assert res4["source"] == "conservative_escalation"

    print("✅ All hierarchical decision fusion matrix boundaries verified perfectly!")

if __name__ == "__main__":
    import sys
    sys.exit(pytest.main(["-v", __file__]))