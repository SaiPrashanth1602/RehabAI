"""
RehabAI Real-Time Machine Learning Inference Engine
Sprint RF-04 Component - v1.4.0 ML Pipeline Core

Loads the serialized Random Forest binary and computes real-time predictive 
classifications and confidence probabilities from incoming feature vectors.
"""

import os
import joblib
import numpy as np
from typing import Dict, Any, List, Union

class RehabMLInferenceEngine:
    def __init__(self, model_filename: str = "rehab_squat_rf.joblib"):
        """Initializes the inference engine context and lazy-loads the model binary."""
        self.model_path = os.path.join("ml", "models", model_filename)
        self.model = None
        self.expected_features: List[str] = []
        self.inverse_mapping: Dict[int, str] = {}
        self._load_model_payload()

    def _load_model_payload(self):
        """Loads the serialized dictionary payload from storage."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"❌ Inference Initialization Error: Model file not found at '{self.model_path}'. "
                f"Please ensure you run 'python -m ml.train_rf' first to generate the binary."
            )
        
        payload = joblib.load(self.model_path)
        self.model = payload["model"]
        self.expected_features = payload["features"]
        
        # Invert the label mapping (e.g., 0 -> "GREEN", 1 -> "YELLOW", 2 -> "RED")
        label_mapping = payload["label_mapping"]
        self.inverse_mapping = {v: k for k, v in label_mapping.items()}

    def predict_safety_status(self, feature_vector: Union[List[float], np.ndarray]) -> Dict[str, Any]:
        """
        Ingests a raw ordered feature array and calculates predictive confidence scores.
        Returns a structured dictionary with the top prediction and class probabilities.
        """
        # Ensure input array matches the exact dimension shape the trees were trained on
        X = np.array(feature_vector, dtype=np.float32).reshape(1, -1)
        
        if X.shape[1] != len(self.expected_features):
            raise ValueError(
                f"❌ Shape Mismatch: Expected {len(self.expected_features)} features {self.expected_features}, "
                f"but received input vector of length {X.shape[1]}."
            )

        # 1. Compute deterministic hard class prediction
        class_idx = int(self.model.predict(X)[0])
        prediction_label = self.inverse_mapping[class_idx]

        # 2. Compute full ensemble probability distribution array
        probabilities = self.model.predict_proba(X)[0]

        # 3. Compile structured confidence summary profile
        confidence_distribution = {}
        for idx, prob in enumerate(probabilities):
            class_name = self.inverse_mapping[idx]
            confidence_distribution[f"{class_name}_PROB"] = round(float(prob), 4)

        return {
            "prediction": prediction_label,
            "confidence": round(float(probabilities[class_idx]), 4),
            "probabilities": confidence_distribution,
            "metadata": {"features_evaluated": self.expected_features}
        }

if __name__ == "__main__":
    # Smoke test execution routine to verify inference parsing logic
    print("🔄 Initializing inference engine check...")
    try:
        engine = RehabMLInferenceEngine()
        
        # Simulate an optimal safe frame feature vector: Depth = 30.0°, Valgus = 4.5°
        mock_safe_vector = [30.0, 4.5]
        result_safe = engine.predict_safety_status(mock_safe_vector)
        
        print("\n🟢 Mock Safe Frame Evaluation:")
        print(f"  » Feature Inputs: {dict(zip(engine.expected_features, mock_safe_vector))}")
        print(f"  » Top Prediction: {result_safe['prediction']} (Confidence: {result_safe['confidence'] * 100:.1f}%)")
        print(f"  » Complete Distribution Breakdown: {result_safe['probabilities']}")

        # Simulate a severe collapse frame feature vector: Depth = 82.0°, Valgus = 18.5°
        mock_hazard_vector = [82.0, 18.5]
        result_hazard = engine.predict_safety_status(mock_hazard_vector)
        
        print("\n🔴 Mock Hazard Frame Evaluation:")
        print(f"  » Feature Inputs: {dict(zip(engine.expected_features, mock_hazard_vector))}")
        print(f"  » Top Prediction: {result_hazard['prediction']} (Confidence: {result_hazard['confidence'] * 100:.1f}%)")
        print(f"  » Complete Distribution Breakdown: {result_hazard['probabilities']}")
        
        print("\n✅ Inference interface verified completely.")
    except Exception as e:
        print(f"\n❌ Inference verification run failed: {str(e)}")