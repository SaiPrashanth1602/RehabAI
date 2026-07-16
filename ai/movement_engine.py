import numpy as np
import time
from collections import deque

class KinematicsEngine:
    @staticmethod
    def calculate_angle(a, b, c):
        a, b, c = np.array(a), np.array(b), np.array(c)
        ba = a - b
        bc = c - b
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        return np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))

    @staticmethod
    def calculate_smoothness(velocity_buffer):
        if len(velocity_buffer) < 3: return 1.0
        accel_variance = np.var(np.diff(velocity_buffer))
        # Smoothness metric derived via acceleration variance
        return float(np.clip(1.0 / (1.0 + (accel_variance / 100.0)), 0.0, 1.0))

class RehabFeatureExtractor:
    def __init__(self, target_rom=130.0, flexion_threshold=120.0, extension_threshold=160.0):
        self.target_rom = target_rom
        self.flexion_threshold = flexion_threshold
        self.extension_threshold = extension_threshold
        self.state = "EXTENSION"
        self.rep_count = 0
        self.failed_reps = 0  # Added tracking for failed/short reps
        
        # Biomechanical boundaries
        self.min_angle = 180.0
        self.max_angle = 0.0
        self.last_rom = 0.0
        self.peak_flexion = 180.0
        self.peak_extension = 0.0
        
        # Temporal engine tracking markers
        self.start_time = time.time()
        self.last_time = time.time()
        self.last_angle = None
        self.last_rep_time = time.time()
        self.phase_start_time = time.time()
        
        # Kinematic / Performance buffers
        self.velocity_buffer = deque(maxlen=30)  # Expanded window for cleaner derivative estimation
        self.last_velocity = 0.0
        self.peak_velocity = 0.0
        self.rep_durations = []
        self.all_roms = []
        
        # Running temporal aggregators
        self.hold_duration = 0.0
        self.rise_duration = 0.0
        self.rest_time = 0.0
        self.time_under_tension = 0.0
        self.smoothness = 1.0

    def extract_joints(self, landmarks):
        # Base architecture tracks Hip(24), Knee(26), Ankle(28)
        indices = [24, 26, 28] 
        
        # Relaxed threshold for easier testing
        threshold = 0.3 
        
        for i in indices:
            if landmarks[i].visibility < threshold:
                return None
        return [[landmarks[i].x, landmarks[i].y, landmarks[i].z] for i in indices]

    def _compute_quality_score(self, current_rom):
        if current_rom == 0: return 0.0
        return round((min(current_rom / self.target_rom, 1.0) * 70.0) + (self.smoothness * 30.0), 2)

    def process_frame(self, hip, knee, ankle, shoulder=None, foot=None):
        current_time = time.time()
        dt = current_time - self.last_time
        if dt <= 0: dt = 0.001
        
        # 1. Core Biomechanical Angular Extraction
        current_angle = KinematicsEngine.calculate_angle(hip, knee, ankle)
        
        # Gracefully handle optional landmarks for secondary kinematic chains if available
        current_hip_angle = KinematicsEngine.calculate_angle(shoulder, hip, knee) if shoulder is not None else 170.0
        current_ankle_angle = KinematicsEngine.calculate_angle(knee, ankle, foot) if foot is not None else 110.0
        
        # 2. Kinematics Derivatives (Velocity / Acceleration calculations)
        angular_velocity = 0.0
        angular_acceleration = 0.0
        
        if self.last_angle is not None and dt > 0.01:
            # Calculate raw velocity
            raw_velocity = (current_angle - self.last_angle) / dt
            
            # Apply low-pass filter using previous velocity to eliminate sub-pixel jitter
            angular_velocity = (0.2 * raw_velocity) + (0.8 * self.last_velocity)
            self.velocity_buffer.append(angular_velocity)
            
            # Filter acceleration as well to prevent extreme variance spikes
            raw_acceleration = (angular_velocity - self.last_velocity) / dt
            angular_acceleration = (0.2 * raw_acceleration) + (0.8 * self.angular_acceleration)
            
            if abs(angular_velocity) > self.peak_velocity:
                self.peak_velocity = abs(angular_velocity)
        
        # Placeholder metric.
        # Replace with SPARC-based smoothness in future versions.
        self.smoothness = KinematicsEngine.calculate_smoothness(list(self.velocity_buffer))
        
        # Save structural steps for the subsequent frame processing loop
        self.last_time = current_time
        self.last_angle = current_angle
        self.last_velocity = angular_velocity
        self.angular_acceleration = angular_acceleration  # Save state for filter

        if current_angle < self.min_angle: self.min_angle = current_angle
        if current_angle > self.max_angle: self.max_angle = current_angle

        # 3. State Machine & Temporal Metric Accumulations
        if self.state == "EXTENSION" and current_angle < self.flexion_threshold:
            self.state = "FLEXION"
            self.rest_time = current_time - self.last_rep_time
            self.phase_start_time = current_time
        elif self.state == "FLEXION":
            self.time_under_tension += dt
            if current_angle < 90.0:
                self.hold_duration += dt
                
            if current_angle > self.extension_threshold:
                self.state = "EXTENSION"
                rep_dur = current_time - self.phase_start_time
                
                if rep_dur > 1.2:  # Validation filter window for real repetitions
                    self.rep_count += 1
                    self.rep_durations.append(rep_dur)
                    self.last_rom = self.max_angle - self.min_angle
                    self.all_roms.append(self.last_rom)
                    
                    if self.min_angle < self.peak_flexion: self.peak_flexion = self.min_angle
                    if self.max_angle > self.peak_extension: self.peak_extension = self.max_angle
                    
                    self.rise_duration = rep_dur * 0.45  # Estimated concentric phase window
                    self.last_rep_time = current_time
                else:
                    self.failed_reps += 1
                
                self.min_angle, self.max_angle = 180.0, 0.0

        # Calculate session consistency parameters
        rom_consistency = 1.0 if len(self.all_roms) < 2 else float(1.0 - min(np.std(self.all_roms) / 100.0, 1.0))
        avg_velocity = float(np.mean(np.abs(list(self.velocity_buffer)))) if self.velocity_buffer else 0.0
        avg_rep_time = float(np.mean(self.rep_durations)) if self.rep_durations else 0.0

        return {
            "angle": float(round(current_angle, 2)),
            "knee_angle": float(round(current_angle, 2)),
            "hip_angle": float(round(current_hip_angle, 2)),
            "ankle_angle": float(round(current_ankle_angle, 2)),
            "rom": float(round(max((self.max_angle - self.min_angle), self.last_rom), 2)),
            "peak_flexion": float(round(self.peak_flexion if self.peak_flexion != 180.0 else current_angle, 2)),
            "peak_extension": float(round(self.peak_extension if self.peak_extension != 0.0 else current_angle, 2)),
            "angular_velocity": float(round(angular_velocity, 2)),
            "angular_acceleration": float(round(angular_acceleration, 2)),
            "peak_velocity": float(round(self.peak_velocity, 2)),
            "average_velocity": float(round(avg_velocity, 2)),
            "rep_count": int(self.rep_count),
            "failed_reps": int(self.failed_reps),
            "rep_duration": float(round(self.rep_durations[-1] if self.rep_durations else 0.0, 2)),
            "average_rep_time": float(round(avg_rep_time, 2)),
            "hold_duration": float(round(self.hold_duration, 2)),
            "rise_duration": float(round(self.rise_duration, 2)),
            "exercise_time": float(round(current_time - self.start_time, 2)),
            "rest_time": float(round(self.rest_time, 2)),
            "time_under_tension": float(round(self.time_under_tension, 2)),
            "movement_quality": float(self._compute_quality_score(self.last_rom)),
            "movement_smoothness": float(round(self.smoothness, 2)),
            "rom_consistency": float(round(rom_consistency, 2))
        }