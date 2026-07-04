"""
RehabAI Random Forest Evaluation Module
Sprint RF-03 Component - v1.4.0 ML Pipeline Core

Loads the trained model binary and evaluates performance metrics against 
the validation test partition to generate a classification matrix report.
"""

import os
import joblib
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
from ml.dataset_loader import MLDatasetLoader
from ml.preprocess import MLDataPreprocessor

def evaluate_trained_model():
    print("=" * 70)
    print("📊 Executing RehabAI Random Forest Statistical Evaluation...")
    print("=" * 70)

    # 1. Load the model artifact payload
    model_path = os.path.join("ml", "models", "rehab_squat_rf.joblib")
    if not os.path.exists(model_path):
        print(f"❌ Evaluation Error: Trained model payload not found at '{model_path}'")
        return

    payload = joblib.load(model_path)
    model = payload["model"]
    feature_names = payload["features"]
    label_mapping = payload["label_mapping"]
    inverse_mapping = {v: k for k, v in label_mapping.items()}

    # 2. Reload the raw data to get clean test partitions
    loader = MLDatasetLoader()
    raw_df = loader.compile_global_dataset()
    
    processor = MLDataPreprocessor()
    X, y, _ = processor.transform_dataset(raw_df)
    _, X_test, _, y_test = processor.generate_train_test_splits(X, y)

    print(f"🔎 Evaluating model against {len(X_test)} unseen validation frames...")

    # 3. Generate predictions
    y_pred = model.predict(X_test)

    # 4. Compute Classification Metrics
    target_names = [inverse_mapping[i] for i in sorted(np.unique(y_test))]
    report = classification_report(y_test, y_pred, target_names=target_names)
    
    print("\n📈 Classification Performance Matrix:")
    print("-" * 70)
    print(report)
    print("-" * 70)

    # 5. Compute the Confusion Matrix
    print("🧱 Raw Confusion Matrix Array:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    
    print("\n💡 Interpretation Guide:")
    print("  Row indices = True Class Label | Column indices = Model Prediction")
    print("=" * 70)

if __name__ == "__main__":
    evaluate_trained_model()