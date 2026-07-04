"""
RehabAI Telemetry Preprocessing Pipeline
Sprint RF-01 - v1.4.0 ML Data Pipeline Component

Handles row normalization, drops uninformative timeline features, encodes string targets,
and separates matrices cleanly into validation train/test partitions.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from typing import Tuple, Dict

class MLDataPreprocessor:
    def __init__(self):
        # Explicit label serialization mapping structure
        self.label_mapping: Dict[str, int] = {
            "GREEN": 0,
            "YELLOW": 1,
            "RED": 2
        }
        self.inverse_mapping: Dict[int, str] = {v: k for k, v in self.label_mapping.items()}

    def transform_dataset(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, list]:
        """
        Processes a raw pivoted dataset frame into split numeric array partitions.
        Drops identifier meta columns and encodes target strings into class arrays.
        """
        if df.empty:
            raise ValueError("Preprocessing error: Target input dataset matrix is empty.")

        # Step 1: Map target string classifications down to sequential integer nodes
        if "Safety_Classification" not in df.columns:
            raise KeyError("Critical target column 'Safety_Classification' missing from input matrix data data.")
            
        df = df.copy()
        df["target_label"] = df["Safety_Classification"].map(self.label_mapping)
        
        # Drop rows where labels are untracked or misaligned
        df = df.dropna(subset=["target_label"])

        # Step 2: Separate structural feature arrays from absolute tracking keys
        columns_to_drop = ["Session_ID", "Timestamp_Offset", "Safety_Classification", "target_label"]
        feature_columns = [col for col in df.columns if col not in columns_to_drop]

        # Step 3: Isolate X matrices and y vectors
        X = df[feature_columns].values
        y = df["target_label"].values

        # Handle structural missing value imputations natively if any gaps are detected
        if np.isnan(X).any():
            from sklearn.impute import SimpleImputer
            imputer = SimpleImputer(strategy="mean")
            X = imputer.fit_transform(X)

        return X, y, feature_columns

    def generate_train_test_splits(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2, random_state: int = 42) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Splits numeric array collections cleanly into standard evaluation test sets."""
        return train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y if len(np.unique(y)) > 1 else None)

if __name__ == "__main__":
    # Integration smoke test check with our active loader pipeline architecture module 
    from ml.dataset_loader import MLDatasetLoader
    
    loader = MLDatasetLoader()
    raw_df = loader.compile_global_dataset()
    
    if not raw_df.empty:
        processor = MLDataPreprocessor()
        X, y, selected_features = processor.transform_dataset(raw_df)
        X_train, X_test, y_train, y_test = processor.generate_train_test_splits(X, y)
        
        print("\n--- Preprocessing Pipeline Operational ---")
        print(f"Target Feature Vector Set: {selected_features}")
        print(f"Training Array Size (X_train):  {X_train.shape}")
        print(f"Testing Array Size (X_test):    {X_test.shape}")
        print(f"Target Distribution Class Map:  {np.bincount(y)}")