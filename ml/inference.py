"""
RehabAI V1 - Machine Learning Real-Time Engine Integration
"""
import numpy as np
import joblib
import os
from ml.feature_extractor import BiomechanicalExtractor
class RehabInferenceEngine:
    def __init__(self):
        self.models = {}

        model_files = {
            "lunge": "Lunge_RF.pkl",
            "sts": "STS_RF.pkl",
            "aslr": "ASLR_RF.pkl",
        }

        for exercise, filename in model_files.items():
            model_path = os.path.join("ml", "models", filename)

            if os.path.exists(model_path):
                payload = joblib.load(model_path)

                self.models[exercise] = {
                    "model": payload["model"],
                    "scaler": payload["scaler"]
                }

                print(f"✅ Loaded {filename}")

            else:
                print(f"❌ Missing model: {filename}")
                self.models[exercise] = None

    def resample_sequence(self, matrix, target_frames=100):
        """
        Resamples a sequence matrix of dynamic frame lengths (e.g. 74 or 120 rows)
        natively up or down to exactly target_frames (100 rows) using linear interpolation.
        """
        current_frames = matrix.shape[0]
        if current_frames == 0:
            return np.zeros((target_frames, matrix.shape[1]))
            
        current_indices = np.linspace(0, current_frames - 1, num=current_frames)
        target_indices = np.linspace(0, current_frames - 1, num=target_frames)
        
        resampled_matrix = np.zeros((target_frames, matrix.shape[1]))
        for col in range(matrix.shape[1]):
            resampled_matrix[:, col] = np.interp(target_indices, current_indices, matrix[:, col])
            
        return resampled_matrix

    def evaluate_live_sequence(self, raw_sequence_matrix, exercise_name):
        """
        Processes real-time inference checks on incoming rep frame blocks.
        """
        exercise_alias = {
            "lunge": "lunge",
            "inline lunge": "lunge",

            "sts": "sts",
            "sit-to-stand": "sts",
            "sit to stand": "sts",

            "aslr": "aslr",
            "standing active straight leg raise": "aslr",
            "straight leg raise": "aslr"
        }

        exercise_key = exercise_alias.get(
            exercise_name.lower().strip(),
            exercise_name.lower().strip()
        )
        
        # Edge boundary check
        if len(raw_sequence_matrix) < 10:
            return {"form_status": "COLLECTING_DATA", "confidence": 0.0}

        print(f"🧠 [ML INFERENCE] Processing live array sequence matrix through ML layer...")
        print(f"   -> Raw Matrix Dimensions received: {raw_sequence_matrix.shape}")

        try:
            # 1. RESAMPLE PIPELINE STEP: Transform raw frames (e.g., 85, 3) to exactly (100, 3)
            aligned_matrix = self.resample_sequence(
            raw_sequence_matrix,
            target_frames=100
            )

            feature_vector = BiomechanicalExtractor.extract_features(
                aligned_matrix
            )

            feature_vector = feature_vector.reshape(1,-1)
            print(f"   -> Extracted 21-dimensional biomechanical feature vector.")
            # 3. RUN MODEL CLASSIFIER WEIGHTS
            payload = self.models.get(exercise_key)

            if payload is None:
                print(f"❌ No model found for {exercise_key}")
                return {
                    "form_status": "MODEL_NOT_FOUND",
                    "confidence": 0.0
                }

            model = payload["model"]
            scaler = payload["scaler"]

            feature_vector = scaler.transform(feature_vector)

            print("=" * 60)
            print("Exercise:", exercise_key)
            print("Feature Shape:", feature_vector.shape)
            print("Features:")
            print(feature_vector)
            print("=" * 60)

            prediction = model.predict(feature_vector)[0]
            prob = model.predict_proba(feature_vector)[0]

            print("Prediction:", prediction)
            print("Probability:", prob)

            status = "CORRECT" if prediction == 1 else "COMPENSATION"
            confidence = round(float(np.max(prob) * 100), 2)

            print(f"🎯 Result: {status} ({confidence}%)")

            return {
                "form_status": status,
                "confidence": confidence
            }

        except Exception as eval_err:
            print(f"   🚨 Pipeline Math Crash during evaluation transformation: {str(eval_err)}")
            return {"form_status": "COMPENSATION", "confidence": 50.0}