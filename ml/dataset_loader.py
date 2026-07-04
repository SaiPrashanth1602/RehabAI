"""
RehabAI ML Dataset Loader Core
Sprint RF-01 - v1.4.0 ML Data Pipeline Component

Aggregates multiple session telemetry logs, transforms long-format frame records 
into wide feature vectors, and prepares raw inputs for preprocessing steps.
"""

import os
import glob
import pandas as pd
from typing import List, Tuple

class MLDatasetLoader:
    def __init__(self, raw_dir: str = os.path.join("ml", "datasets", "raw")):
        """Initializes loader context path targeting raw CSV deposit maps."""
        self.raw_dir = raw_dir

    def get_all_csv_paths(self) -> List[str]:
        """Scans the targeted raw data directory for session CSV logs."""
        return glob.glob(os.path.join(self.raw_dir, "telemetry_*.csv"))

    def load_and_pivot_session(self, file_path: str) -> pd.DataFrame:
        """
        Transforms long-format frame streams into structured wide-format machine learning feature maps.
        Pivots metrics out into dedicated attribute columns indexed by runtime offsets.
        """
        df = pd.read_csv(file_path)
        if df.empty:
            return pd.DataFrame()

        # Step 1: Pivot the categorical Kinematic_Metric column values into distinct column fields
        pivoted_features = df.pivot_table(
            index="Timestamp_Offset",
            columns="Kinematic_Metric",
            values="Calculated_Value",
            aggfunc="first"
        ).reset_index()

        # Step 2: Extract corresponding ground truth safety classifications mapped by timestamp offsets
        labels_map = df.groupby("Timestamp_Offset")["Safety_Classification"].first().reset_index()
        
        # Merge tracking components into a unified feature vector frame row context
        session_matrix = pd.merge(pivoted_features, labels_map, on="Timestamp_Offset")
        
        # Inject source session tag identifier tracking fields
        session_id = os.path.basename(file_path).replace("telemetry_", "").replace(".csv", "")
        session_matrix.insert(0, "Session_ID", session_id)
        
        return session_matrix

    def compile_global_dataset(self) -> pd.DataFrame:
        """Iterates over all discovered session traces to construct a global dense master dataset matrix."""
        csv_files = self.get_all_csv_paths()
        if not csv_files:
            print(f"⚠️ Dataset Loader Warning: No raw session files detected inside '{self.raw_dir}'.")
            return pd.DataFrame()

        compiled_frames = []
        print(f"🔄 Scanning and aggregating {len(csv_files)} tracking telemetry files...")
        
        for file in csv_files:
            try:
                session_df = self.load_and_pivot_session(file)
                if not session_df.empty:
                    compiled_frames.append(session_df)
            except Exception as e:
                print(f"❌ Failed to parse data slice file '{file}': {str(e)}")

        if not compiled_frames:
            return pd.DataFrame()

        # Stack all parsed dataframes vertically to form a single master dataset
        master_dataset = pd.concat(compiled_frames, ignore_index=True)
        print(f"✅ Global aggregation complete. Final Shape Matrix: {master_dataset.shape}")
        return master_dataset

if __name__ == "__main__":
    # Internal component smoke test runner verification module loop execution line
    loader = MLDatasetLoader()
    dataset = loader.compile_global_dataset()
    if not dataset.empty:
        print("\n--- Feature Matrix Quick Preview ---")
        print(dataset.head(5))