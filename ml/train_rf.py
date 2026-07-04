"""
RehabAI Random Forest Training Module
Sprint RF-02 Component - v1.4.0 ML Pipeline Core

Loads the processed multi-variable matrix, trains an ensemble decision tree classifier,
and serializes model binaries down to the models storage directory.
"""

import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from ml.dataset_loader import MLDatasetLoader
from ml.preprocess import MLDataPreprocessor

def execute_model_training_pipeline():
    print("=" * 70)
    print("🌲 Initializing RehabAI Random Forest Training Routine...")
    print("=" * 70)

    # 1. Pipeline Execution: Aggregate raw multi-session tables
    loader = MLDatasetLoader()
    raw_df = loader.compile_global_dataset()
    
    if raw_df.empty:
        print("❌ Training Aborted: No valid dataset matrices compiled.")
        return

    # 2. Pipeline Execution: Run transformations and test/train splits
    processor = MLDataPreprocessor()
    X, y, feature_names = processor.transform_dataset(raw_df)
    X_train, X_test, y_train, y_test = processor.generate_train_test_splits(X, y)

    print(f"📦 Features Targeted for Node Splitting: {feature_names}")
    print(f"🏋️ Training Dataset Shape Matrix:        {X_train.shape}")
    
    # 3. Initialize Random Forest Classifier Model
    # Setting n_estimators=100 creates an ensemble of 100 independent decision trees
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1 # Utilize all available CPU cores for parallel tree compilation
    )

    print("\n🔄 Fitting ensemble trees against training space patterns...")
    model.fit(X_train, y_train)
    print("✅ Model training iteration completed successfully.")

    # 4. Calculate Internal Feature Importance Weights
    print("\n📊 Biomechanical Feature Importance Map Metrics:")
    importances = model.feature_importances_
    for name, weight in zip(feature_names, importances):
        print(f"  » {name:<40}: {weight:.4f}")

    # 5. Serialize Model Weights Binary to Disk
    model_dir = os.path.join("ml", "models")
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
        
    model_output_path = os.path.join(model_dir, "rehab_squat_rf.joblib")
    
    # Bundle both the trained model and the feature definitions together
    payload = {
        "model": model,
        "features": feature_names,
        "label_mapping": processor.label_mapping
    }
    
    joblib.dump(payload, model_output_path)
    print("-" * 70)
    print(f"💾 Serialized Model Binary successfully written to:\n  {model_output_path}")
    print("=" * 70)

if __name__ == "__main__":
    execute_model_training_pipeline()