"""
RehabAI V1 - Core Training Engine
"""
import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from ml.config import DATASET_ROOT, MODEL_DIR, TARGET_MOVEMENTS, RF_PARAMS
from ml.dataset_loader import UIPRMDLoader
from ml.preprocessing import resample_sequence
from ml.feature_extractor import BiomechanicalExtractor

def train_v1_pipeline():
    print("🚀 Initializing RehabAI V1 Production Training Suite...")
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    loader = UIPRMDLoader(DATASET_ROOT)
    meta_df = loader.scan_and_parse()
    
    print(f"📊 Discovered matching exercise logs inside filesystem: {len(meta_df)} rows.")

    for m_code, name in TARGET_MOVEMENTS.items():
        print(f"\n🌲 Processing Exercise: {name} ({m_code})...")
        ex_df = meta_df[meta_df["exercise_id"] == m_code]
        
        if ex_df.empty:
            print(f"⚠️ Warning: Missing entries for {name}. Skipping compilation.")
            continue
            
        features_collector = []
        labels_collector = []
        subjects_collector = []
        
        for _, row in ex_df.iterrows():
            try:
                raw_matrix = loader.load_matrix(row["file_path"])
                aligned_matrix = resample_sequence(raw_matrix, target_frames=100)
                vector = BiomechanicalExtractor.extract_features(aligned_matrix)
                
                features_collector.append(vector)
                labels_collector.append(row["label"])
                subjects_collector.append(row["subject_id"])
            except Exception as e:
                print(f"❌ Failed processing sequence metadata slice at {row['file_path']}: {e}")

        X = np.array(features_collector)
        y = np.array(labels_collector)
        groups = np.array(subjects_collector)

        print(f"⚖️ Normalizing engineered feature matrices for {name}: {X.shape}")
        scaler = StandardScaler()
        X_scaled = final_features = scaler.fit_transform(X)

        print(f"🌲 Training independent model weights for {name}...")
        model = RandomForestClassifier(**RF_PARAMS)
        model.fit(X_scaled, y)

        # Meta package configuration structure
        payload = {
            "model": model,
            "scaler": scaler,
            "exercise_name": name,
            "exercise_code": m_code,
            "feature_names": name,
            "training_groups": np.unique(groups).tolist()
        }

        export_path = os.path.join(MODEL_DIR, f"{name}_RF.pkl")
        joblib.dump(payload, export_path)
        print(f"💾 Exported asset bundle cleanly to: {export_path}")

if __name__ == "__main__":
    train_v1_pipeline()