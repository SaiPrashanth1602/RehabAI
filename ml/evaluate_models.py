"""
RehabAI V1 - Cross-Subject Validation Engine
Author: Sai Prashanth Ramesh & Core Systems Architecture
Description: Validates classifier generalizability using strict cross-subject GroupKFold isolation, 
             computes aggregate statistical metrics, and generates publication-grade evaluation charts.
"""
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import GroupKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# Structural imports from your ml module
from ml.config import DATASET_ROOT, TARGET_MOVEMENTS, RF_PARAMS
from ml.dataset_loader import UIPRMDLoader
from ml.preprocessing import resample_sequence
from ml.feature_extractor import BiomechanicalExtractor

def generate_evaluation_visualizations(m_code, name, y_true, y_pred, fold_accuracies, feature_importances):
    """
    Constructs and exports evaluation plots for the presentation portfolio.
    """
    # Create an export directory for evaluation graphics if it doesn't exist
    export_dir = os.path.join("ml", "evaluation_plots")
    os.makedirs(export_dir, exist_ok=True)
    
    # Define a clean list of baseline feature labels matching your vector footprint layout
    feature_names = [
        "Knee Angle", "Hip Angle", "Ankle Angle", "ROM", "Peak Flexion", "Peak Extension",
        "Angular Velocity", "Angular Acceleration", "Peak Velocity", "Average Velocity",
        "Rep Duration", "Hold Duration", "Avg Rep Time", "Exercise Time", "Rest Time",
        "Time Under Tension", "Movement Quality", "Smoothness", "ROM Consistency",
        "Completion Pct", "Limb Symmetry Base"
    ]
    # Truncate or expand safely to handle variation adjustments in feature length dynamically
    if feature_importances.shape[0] != len(feature_names):
        feature_names = [f"Feature {i+1}" for i in range(feature_importances.shape[0])]

    # ---------------------------------------------------------------------------
    # CHART 1: CONFUSION MATRIX HEATMAP
    # ---------------------------------------------------------------------------
    plt.figure(figsize=(6, 5))
    cm = confusion_matrix(y_true, y_pred)
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False,
                xticklabels=["Incorrect Form", "Correct Form"],
                yticklabels=["Incorrect Form", "Correct Form"])
    plt.title(f"Confusion Matrix Heatmap\nExercise: {name}")
    plt.xlabel("Predicted Labels")
    plt.ylabel("Ground Truth Labels")
    plt.tight_layout()
    plt.savefig(os.path.join(export_dir, f"{m_code}_confusion_matrix.png"), dpi=300)
    plt.close()

    # ---------------------------------------------------------------------------
    # CHART 2: AGGREGATE FEATURE IMPORTANCE
    # ---------------------------------------------------------------------------
    plt.figure(figsize=(10, 6))
    sorted_indices = np.argsort(feature_importances)[::-1]
    sorted_features = [feature_names[i] for i in sorted_indices]
    sorted_weights = feature_importances[sorted_indices]
    
    sns.barplot(x=sorted_weights, y=sorted_features, palette="viridis")
    plt.title(f"Mean Gini Feature Importance Profile\nExercise: {name}")
    plt.xlabel("Relative Mean Importance Weight")
    plt.ylabel("Extracted Biomechanical Feature")
    plt.tight_layout()
    plt.savefig(os.path.join(export_dir, f"{m_code}_feature_importance.png"), dpi=300)
    plt.close()

    # ---------------------------------------------------------------------------
    # CHART 3: SPLIT ACCURACY PERFORMANCE LINE GRAPH
    # ---------------------------------------------------------------------------
    plt.figure(figsize=(7, 4))
    folds = [f"Fold {i+1}" for i in range(len(fold_accuracies))]
    plt.plot(folds, fold_accuracies, marker='o', linestyle='-', color='#1f77b4', linewidth=2, markersize=8)
    plt.axhline(y=np.mean(fold_accuracies), color='r', linestyle='--', label=f"Mean Acc ({np.mean(fold_accuracies)*100:.1f}%)")
    
    plt.title(f"Validation Split Accuracy Profile\nExercise: {name}")
    plt.xlabel("GroupKFold Evaluation Splits")
    plt.ylabel("Classification Accuracy Boundary")
    plt.ylim([0.0, 1.05])
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(os.path.join(export_dir, f"{m_code}_fold_accuracy.png"), dpi=300)
    plt.close()
    
    print(f"🎯 SUCCESS: Exported validation charts to '{export_dir}/' for {name} movement keys.")


def evaluate_v1_infrastructure():
    print("📋 Commencing Cross-Subject Generalizability Analysis...")
    loader = UIPRMDLoader(DATASET_ROOT)
    meta_df = loader.scan_and_parse()

    for m_code, name in TARGET_MOVEMENTS.items():
        print(f"\n==================== Evaluation Fold: {name} ====================")
        ex_df = meta_df[meta_df["exercise_id"] == m_code]
        if ex_df.empty:
            print(f"⚠️ Warning: Dataset has zero entries matching target: {m_code}")
            continue
            
        features_collector, labels_collector, subjects_collector = [], [], []
        for _, row in ex_df.iterrows():
            try:
                raw_matrix = loader.load_matrix(row["file_path"])
                aligned_matrix = resample_sequence(raw_matrix, target_frames=100)
                vector = BiomechanicalExtractor.extract_features(aligned_matrix)
                features_collector.append(vector)
                labels_collector.append(row["label"])
                subjects_collector.append(row["subject_id"])
            except Exception as _:
                continue

        if not features_collector:
            continue

        X = np.array(features_collector)
        y = np.array(labels_collector)
        groups = np.array(subjects_collector)

        # Enforce strict cross-subject isolation via GroupKFold
        n_splits = 5
        gkf = GroupKFold(n_splits=n_splits)
        oof_predictions = np.zeros(len(y))
        
        # Performance analytics metrics trackers
        fold_accuracies = []
        mean_feature_importances = np.zeros(X.shape[1])

        for train_idx, test_idx in gkf.split(X, y, groups=groups):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            fold_clf = RandomForestClassifier(**RF_PARAMS)
            fold_clf.fit(X_train_scaled, y_train)
            
            # Predict and collect split arrays
            predictions = fold_clf.predict(X_test_scaled)
            oof_predictions[test_idx] = predictions
            
            # Record individual metrics for tracking graph metrics charts
            fold_accuracies.append(accuracy_score(y_test, predictions))
            mean_feature_importances += fold_clf.feature_importances_ / n_splits

        # Print standard analytical outputs to terminal
        print("\n📋 Detailed Classification Performance Matrix Summary:")
        print(classification_report(y, oof_predictions, target_names=["Incorrect Form", "Correct Form"]))
        print("📊 Confusion Matrix Output:")
        print(confusion_matrix(y, oof_predictions))
        
        # Generate and save graphs directly to disc paths
        generate_evaluation_visualizations(
            m_code=m_code,
            name=name,
            y_true=y,
            y_pred=oof_predictions,
            fold_accuracies=fold_accuracies,
            feature_importances=mean_feature_importances
        )

if __name__ == "__main__":
    evaluate_v1_infrastructure()