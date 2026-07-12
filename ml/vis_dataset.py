"""
RehabAI V1 - Dataset Preprocessing & Normalization Inspector
"""
import gzip
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

def load_raw_gz_sequence(file_path):
    """Reads and parses a compressed text file containing joint angles."""
    try:
        with gzip.open(file_path, 'rt') as f:
            data = [line.strip().split() for l in f.readlines() if (line := l.strip())]
        matrix = np.array(data, dtype=float)
        return matrix
    except Exception as e:
        print(f"🚨 Failed reading file: {file_path}. Error: {e}")
        return None

def resample_sequence(matrix, target_frames=100):
    """Linear interpolation resampling to scale time-series sequences uniformly."""
    current_frames = matrix.shape[0]
    current_indices = np.linspace(0, current_frames - 1, num=current_frames)
    target_indices = np.linspace(0, current_frames - 1, num=target_frames)
    
    resampled_matrix = np.zeros((target_frames, matrix.shape[1]))
    for col in range(matrix.shape[1]):
        resampled_matrix[:, col] = np.interp(target_indices, current_indices, matrix[:, col])
    return resampled_matrix

def generate_normalization_screenshot_data():
    print("🔬 Accessing UI-PRMD clinical repository vectors...")
    
    # FIX: Paths adjusted to match your exact directory structure (Removed the empty /data segment)
    base_dir = "UI-PRMD-Analysis-master"
    correct_dir = os.path.join(base_dir, "Segmented Movements", "Kinect", "Angles")
    incorrect_dir = os.path.join(base_dir, "Incorrect Segmented Movements", "Kinect", "Angles")
    
    # Target exercise m05 (Sit-to-Stand) sample files
    good_sample_file = os.path.join(correct_dir, "m05_s01_e01_angles.txt.gz")
    bad_sample_file = os.path.join(incorrect_dir, "m05_s01_e01_angles_inc.txt.gz")
    
    # Double-check file availability before running processing tasks
    if not os.path.exists(good_sample_file):
        print(f"🚨 Path Error: Could not locate file at: {os.path.abspath(good_sample_file)}")
        return
        
    raw_good = load_raw_gz_sequence(good_sample_file)
    raw_bad = load_raw_gz_sequence(bad_sample_file)
    
    if raw_good is None or raw_bad is None:
        print("🚨 Error: Matrix collection was interrupted because files could not be loaded.")
        return
        
    # Resample vectors to exactly 100 timesteps
    norm_good = resample_sequence(raw_good, target_frames=100)
    norm_bad = resample_sequence(raw_bad, target_frames=100)
    
    # Apply standard normalization scaling boundaries [0, 1]
    min_val, max_val = norm_good.min(), norm_good.max()
    scaled_good = (norm_good - min_val) / (max_val - min_val + 1e-8)
    scaled_bad = (norm_bad - min_val) / (max_val - min_val + 1e-8)
    
    # Generate the plot
    os.makedirs("ml/evaluation_plots", exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Trace the first 3 primary tracking joint angles
    ax1.plot(scaled_good[:, :3]) 
    ax1.set_title("🟢 Normalized Correct Form (100 Timesteps)")
    ax1.set_xlabel("Normalized Paced Timestep Index")
    ax1.set_ylabel("Scaled Amplitude Bound [0 - 1]")
    ax1.grid(True, linestyle="--", alpha=0.5)
    
    ax2.plot(scaled_bad[:, :3])
    ax2.set_title("🔴 Normalized Compensation Form (100 Timesteps)")
    ax2.set_xlabel("Normalized Paced Timestep Index")
    ax2.grid(True, linestyle="--", alpha=0.5)
    
    plt.suptitle("RehabAI Preprocessing Pipeline - Dataset Normalization Blueprint Visualizer", fontsize=14, fontweight='bold')
    
    plot_out = "ml/evaluation_plots/dataset_normalization_screenshot.png"
    plt.savefig(plot_out, dpi=300, bbox_inches='tight')
    plt.close()
    
    print("\n=============================================================")
    print("✅ DATASET NORMALIZATION DIAGNOSTIC CHART GENERATED!")
    print(f"👉 Open Image File: {os.path.abspath(plot_out)}")
    print("=============================================================\n")

if __name__ == "__main__":
    generate_normalization_screenshot_data()