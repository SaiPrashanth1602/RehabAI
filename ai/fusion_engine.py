"""
RehabAI Clinical Decision Fusion Engine
Sprint RF-05 Component - v1.4.0 Unified Intelligence Core

Amalgamates deterministic clinical rule compliance metrics with probabilistic 
Random Forest inferences to output an explainable, safety-first execution status.
"""

from typing import Dict, Any

class ClinicalFusionEngine:
    def __init__(self, confidence_threshold: float = 0.75):
        """Initializes the fusion engine with a configurable confidence barrier."""
        self.confidence_threshold = confidence_threshold

    def evaluate_fused_decision(self, rule_status: str, ml_status: str, ml_confidence: float) -> Dict[str, Any]:
        """
        Executes hierarchical safety fusion over upstream prediction vectors.
        Enforces a clinical circuit-breaker to prioritize hardcoded rules during safety violations.
        """
        # Formulate base trace payload structure for absolute explainability
        response = {
            "status": "GREEN",
            "source": "unanimous_agreement",
            "rule_engine_status": rule_status,
            "ml_engine_status": ml_status,
            "ml_confidence": round(float(ml_confidence), 4),
            "reason": "Both analytical layers confirm a safe, compliant movement matrix."
        }

        # --- RULE 1: CLINICAL CIRCUIT BREAKER (Rule Engine outputs RED) ---
        if rule_status == "RED":
            response["status"] = "RED"
            response["source"] = "rule_safety_override"
            response["reason"] = "Hard clinical safety threshold violation detected. Machine learning overrides suspended."
            return response

        # --- RULE 2: CONSERVATIVE RISK ESCALATION (Either layer detects critical failure) ---
        if rule_status == "YELLOW" and ml_status == "RED":
            response["status"] = "RED"
            response["source"] = "conservative_escalation"
            response["reason"] = "Rule warning combined with high-risk ML failure detection. Escalated to RED."
            return response

        # --- RULE 3: PRESERVE CLINICAL WARNINGS ---
        if rule_status == "YELLOW" and ml_status == "GREEN":
            response["status"] = "YELLOW"
            response["source"] = "rule_warning_preservation"
            response["reason"] = "Rule engine boundary warning active. Retaining conservative buffer."
            return response

        # --- RULE 4: PREDICTIVE INTELLIGENCE ESCALATION (Rule is GREEN, ML flags an anomaly) ---
        if rule_status == "GREEN" and ml_status in ["YELLOW", "RED"]:
            # Evaluate if the model's confidence crosses our strict research gate check threshold
            if ml_confidence >= self.confidence_threshold:
                response["status"] = ml_status
                response["source"] = "ml_predictive_intelligence"
                response["reason"] = f"ML model detected a complex joint compensation pattern ({ml_status}) with high confidence."
            else:
                response["status"] = "GREEN"
                response["source"] = "low_confidence_ml_suppression"
                response["reason"] = f"ML flagged a borderline anomaly ({ml_status}), but score fell below {self.confidence_threshold * 100}%. Suppressed."
            return response

        # --- RULE 5: STANDARD UNANIMOUS AGGREGATIONS ---
        if rule_status == "YELLOW" and ml_status == "YELLOW":
            response["status"] = "YELLOW"
            response["source"] = "unanimous_warning"
            response["reason"] = "Both rule boundaries and ML trees confirm a borderline movement profile."
            return response

        return response