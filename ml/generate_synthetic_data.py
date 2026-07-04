"""
RehabAI Synthetic Data Generator
Sprint RF-01 Component - v1.4.0 ML Pipeline

Generates balanced, randomized synthetic biomechanical feature frames 
for EX-004 (Mini Squat) to seed the Random Forest classifier.
"""

import os
import numpy as np
import pandas as pd

def generate_mini_squat_dataset(num_samples_per_class: int = 500, output_dir: str = os.path.join("ml", "datasets", "raw")):
    """Generates thousands of randomized, balanced kinematic feature arrays for training."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    np.random.seed(42) # Lock seed for reproducible training iterations
    rows = []

    # 1. Generate Class 0: GREEN (Optimal safe performance limits)
    # Depth: 0 to 60 deg, Valgus: 0 to 10 deg
    for i in range(num_samples_per_class):
        offset = 1000.0 + (i * 0.03)
        depth = np.random.uniform(5.0, 59.9)
        valgus = np.random.uniform(0.0, 9.9)
        
        # Log depth metric frame row
        rows.append([offset, "knee_flexion_depth", round(depth, 2), "GREEN"])
        # Log valgus metric frame row
        rows.append([offset, "frontal_plane_knee_projection_angle", round(valgus, 2), "GREEN"])

    # 2. Generate Class 1: YELLOW (Warning buffer limits)
    # Occurs if depth is 60-75 deg OR valgus is 10-15 deg
    for i in range(num_samples_per_class):
        offset = 2000.0 + (i * 0.03)
        # Mix scenarios: some high depth, some high valgus
        if i % 2 == 0:
            depth = np.random.uniform(60.0, 74.9)
            valgus = np.random.uniform(0.0, 9.9)
        else:
            depth = np.random.uniform(5.0, 59.9)
            valgus = np.random.uniform(10.0, 14.9)
            
        rows.append([offset, "knee_flexion_depth", round(depth, 2), "YELLOW"])
        rows.append([offset, "frontal_plane_knee_projection_angle", round(valgus, 2), "YELLOW"])

    # 3. Generate Class 2: RED (Hazardous threshold breaches)
    # Occurs if depth > 75 deg OR valgus > 15 deg
    for i in range(num_samples_per_class):
        offset = 3000.0 + (i * 0.03)
        if i % 2 == 0:
            depth = np.random.uniform(75.1, 120.0)
            valgus = np.random.uniform(0.0, 14.9)
        else:
            depth = np.random.uniform(5.0, 74.9)
            valgus = np.random.uniform(15.1, 30.0)
            
        rows.append([offset, "knee_flexion_depth", round(depth, 2), "RED"])
        rows.append([offset, "frontal_plane_knee_projection_angle", round(valgus, 2), "RED"])

    # Build DataFrame container and write directly to the raw directory
    df = pd.DataFrame(rows, columns=["Timestamp_Offset", "Kinematic_Metric", "Calculated_Value", "Safety_Classification"])
    output_path = os.path.join(output_dir, "telemetry_SYNTHETIC_SQUAT_1500.csv")
    df.to_csv(output_path, index=False)
    print(f"🔥 Successfully synthesized {num_samples_per_class * 3} balanced telemetry frames!")
    print(f"📂 Extracted down to: {output_path}")

if __name__ == "__main__":
    generate_mini_squat_dataset()