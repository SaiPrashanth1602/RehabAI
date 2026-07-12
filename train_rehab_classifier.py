"""
RehabAI V1 - High-Precision Squat Quality Assessment Engine
Author: Sai Prashanth Ramesh
Description: Trains a binary classifier to evaluate Deep Squat performance quality
             (Correct Form vs. Form Compensations) using UI-PRMD trajectory sequences.
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

def train_squat_quality_engine():
    print("🌲 Initializing RehabAI V1 Squat Quality Assessment Pipeline...")
    
    # Ingest the available CSV data matrices directly
    correct_path = "Data_Correct.csv"
    incorrect_path = "Data_Incorrect.csv"
    
    if not os.path.exists(correct_path) or not os.path.exists(incorrect_path):
        raise FileNotFoundError("🚨 Missing your root Data_Correct.csv or Data_Incorrect.csv files!")
        
    df_correct = pd.read_csv(correct_path, header=None)
    df_incorrect = pd.read_csv(incorrect_path, header=None)
    
    print(f"✅ Loaded Correct Squat Repetitions: {df_correct.shape}")
    print(f"❌ Loaded Incorrect Squat Repetitions: {df_incorrect.shape}")
    
    # Assign target labels (1 = Safe/Correct, 0 = Deficient/Incorrect)
    df_correct['label'] = 1
    df_incorrect['label'] = 0
    
    # Merge rows cleanly
    master_dataset = pd.concat([df_correct, df_incorrect], axis=0, ignore_index=True)
    
    X = master_dataset.drop(columns=['label'])
    y = master_dataset['label'].values
    
    # Stratified Train/Test split over the sequences
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Normalize our data
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Fit an optimized Random Forest Classifier
    print("🌲 Training Random Forest Classifier on sequence paths...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train_scaled, y_train)
    
    # Output evaluation results
    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n🎯 Training Completed! Form Assessment Accuracy: {acc * 100:.2f}%")
    print("\n📋 Performance Assessment Report:")
    print(classification_report(y_test, y_pred, target_names=["Incorrect/Compensated Form", "Correct/Perfect Form"]))
    
    # Save the absolute production weights files
    os.makedirs("ml/models", exist_ok=True)
    joblib.dump(model, "ml/models/squat_rf.pkl")
    joblib.dump(scaler, "ml/models/squat_scaler.joblib")
    
    print("💾 Successfully exported squat_rf.pkl and squat_scaler.joblib!")

if __name__ == "__main__":
    train_squat_quality_engine()