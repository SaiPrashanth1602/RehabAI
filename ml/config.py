"""
RehabAI V1 - Global Configuration Settings
Author: Sai Prashanth Ramesh & Core Systems Architecture
"""
import os

CORE_PROJECT_ROOT = "."

PATH_CANDIDATES = [
    os.path.join(CORE_PROJECT_ROOT, "UI-PRMD-Analysis-master", "data"),
    os.path.join(CORE_PROJECT_ROOT, "UI-PRMD-Analysis-master"),
    os.path.join(CORE_PROJECT_ROOT, "data"),
    os.path.join(CORE_PROJECT_ROOT, "UI-PRMD"),
]

DATASET_ROOT = None
for candidate in PATH_CANDIDATES:
    if os.path.exists(candidate) and os.path.isdir(candidate):
        DATASET_ROOT = candidate
        break

if DATASET_ROOT is None:
    DATASET_ROOT = os.path.join(CORE_PROJECT_ROOT, "UI-PRMD-Analysis-master", "data")

MODEL_DIR = os.path.join(CORE_PROJECT_ROOT, "ml", "models")

TARGET_MOVEMENTS = {
    "m03": "Lunge",
    "m05": "STS",
    "m06": "ASLR"
}

# UPGRADED: Optimized Ensemble constraints to extract maximum time-series boundary details
RF_PARAMS = {
    "n_estimators": 350,          # Increased tree count for highly stable vote counts
    "max_depth": None,            # Allow trees to grow fully to isolate fine joint patterns
    "min_samples_split": 2,       # Fine-grained splitting
    "min_samples_leaf": 1,        # Precise terminal leaf nodes
    "max_features": "sqrt",       # Traditional feature square-root subset matching
    "class_weight": "balanced",   # Balanced penalty parameters across form faults
    "random_state": 42
}