"""
RehabAI V1 - High-Density Multi-Scale Biomechanical Feature Extractor
Author: Sai Prashanth Ramesh & Core Systems Architecture
"""
import numpy as np

class BiomechanicalExtractor:
    @staticmethod
    def extract_features(angle_matrix, sample_rate=100.0):
        """
        Extracts identical 21-dimensional high-density signal representations
        designed to align perfectly with our production runtime contracts.
        """
        dt = 1.0 / sample_rate
        total_frames = len(angle_matrix)
        eps = 1e-6  # Protects against 0/0 divide warnings
        
        # Aligned UI-PRMD Channel Maps: Hip (3), Knee (6), Ankle (9)
        hip_idx = 3 if angle_matrix.shape[1] > 3 else 0
        knee_idx = 6 if angle_matrix.shape[1] > 6 else 1
        ankle_idx = 9 if angle_matrix.shape[1] > 9 else 2
        
        hip_series = angle_matrix[:, hip_idx]
        knee_series = angle_matrix[:, knee_idx]
        ankle_series = angle_matrix[:, ankle_idx]
        
        # 1-3. Core Angles (Terminal Values)
        knee_angle = knee_series[-1]
        hip_angle = hip_series[-1]
        ankle_angle = ankle_series[-1]
        
        # 4-6. Amplitude Signatures (Global Ranges)
        peak_flexion = np.max(knee_series)
        peak_extension = np.min(knee_series)
        rom = peak_flexion - peak_extension
        
        # 7-10. Kinematic Signal Derivatives
        velocity_profile = np.diff(knee_series) / dt
        acceleration_profile = np.diff(velocity_profile) / dt if len(velocity_profile) > 1 else np.array([0.0])
        
        angular_velocity = velocity_profile[-1] if len(velocity_profile) > 0 else 0.0
        angular_acceleration = acceleration_profile[-1] if len(acceleration_profile) > 0 else 0.0
        peak_velocity = np.max(np.abs(velocity_profile)) if len(velocity_profile) > 0 else 0.0
        average_velocity = np.mean(np.abs(velocity_profile)) if len(velocity_profile) > 0 else 0.0
        
        # 11-16. Advanced Temporal Phase Windows & Signal Deviations
        rep_duration = total_frames * dt
        hold_threshold = peak_flexion - (rom * 0.12) if rom > 0 else peak_flexion
        hold_duration = np.sum(knee_series >= hold_threshold) * dt
        
        # Chop the time-series cleanly into 4 sequential blocks
        quarters = np.array_split(knee_series, 4)
        q1_mean = np.mean(quarters[0]) if len(quarters[0]) > 0 else knee_angle
        q2_mean = np.mean(quarters[1]) if len(quarters[1]) > 0 else knee_angle
        q3_mean = np.mean(quarters[2]) if len(quarters[2]) > 0 else knee_angle
        q4_mean = np.mean(quarters[3]) if len(quarters[3]) > 0 else knee_angle
        
        # Extra micro-stability variance profiles safely protected from 0 values
        q1_std = np.std(quarters[0]) if len(quarters[0]) > 0 else 0.0
        q2_std = np.std(quarters[1]) if len(quarters[1]) > 0 else 0.0
        q3_std = np.std(quarters[2]) if len(quarters[2]) > 0 else 0.0
        q4_std = np.std(quarters[3]) if len(quarters[3]) > 0 else 0.0
        
        # Map our quarter means directly into our 21-D array footprint variables:
        average_rep_time = q1_mean
        exercise_time = q2_mean
        rest_time = q3_mean
        time_under_tension = q4_mean
        
        # 17-21. Quality Assessment Tracking Indexes
        # Safe cross-joint coordination tracking protected from runtime divide-by-zero warnings
        std_knee, std_hip = np.std(knee_series), np.std(hip_series)
        if std_knee > eps and std_hip > eps:
            joint_coordination = np.corrcoef(knee_series, hip_series)[0, 1]
            if np.isnan(joint_coordination):
                joint_coordination = 1.0
        else:
            joint_coordination = 1.0
            
        movement_quality = float(joint_coordination)
        movement_smoothness = float(np.std(acceleration_profile)) if len(acceleration_profile) > 0 else 0.0
        
        # Inject our quarter variances to help the trees identify shaky execution patterns:
        rom_consistency = float(q2_std + q3_std)   # Micro-tremor footprint across peak depth phase
        exercise_completion = float(q1_std + q4_std)  # Transition stability across boundary phases
        limb_symmetry_index = 100.0                   # Runtime placeholder marker
        
        return np.array([
            knee_angle, hip_angle, ankle_angle, rom, peak_flexion, peak_extension,
            angular_velocity, angular_acceleration, peak_velocity, average_velocity,
            rep_duration, hold_duration, average_rep_time, exercise_time, rest_time,
            time_under_tension, movement_quality, movement_smoothness, rom_consistency,
            exercise_completion, limb_symmetry_index
        ], dtype=float)