import cv2
import numpy as np
import sys
import time
from collections import deque

# -----------------------------------------------------------------
# 1. UPGRADED MODULAR BIOMECHANICS & KINEMATICS ENGINE
# -----------------------------------------------------------------
class KinematicsEngine:
    @staticmethod
    def calculate_angle(a, b, c):
        a, b, c = np.array(a), np.array(b), np.array(c)
        ba = a - b
        bc = c - b
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        return float(np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0))))

    @staticmethod
    def calculate_smoothness(velocity_buffer):
        if len(velocity_buffer) < 3: return 1.0
        accel_variance = np.var(np.diff(velocity_buffer))
        return float(np.clip(1.0 / (1.0 + (accel_variance / 100.0)), 0.0, 1.0))

class RehabFeatureExtractor:
    def __init__(self, target_rom=130.0, flexion_threshold=120.0, extension_threshold=160.0):
        self.target_rom = target_rom
        self.flexion_threshold = flexion_threshold
        self.extension_threshold = extension_threshold
        
        # State Management
        self.state = "EXTENSION"
        self.rep_count = 0
        self.failed_reps = 0
        
        # Angle Boundaries
        self.min_angle = 180.0
        self.max_angle = 0.0
        self.last_rom = 0.0
        self.peak_flexion = 180.0
        self.peak_extension = 0.0
        
        # Time Management
        self.start_time = time.time()
        self.last_time = time.time()
        self.last_rep_time = time.time()
        self.phase_start_time = time.time()
        
        # Temporal Metric Tracking Buffers
        self.rep_durations = []
        self.hold_duration = 0.0
        self.rise_duration = 0.0
        self.rest_time = 0.0
        self.time_under_tension = 0.0
        
        # Kinematic Tracking Buffers
        self.last_angle = None
        self.last_velocity = 0.0
        self.velocity_buffer = deque(maxlen=30)
        self.all_roms = []
        
        # Live Calculated Variables
        self.angular_velocity = 0.0
        self.angular_acceleration = 0.0
        self.peak_velocity = 0.0
        self.smoothness = 1.0

    def extract_joints(self, landmarks):
        # Tracking points: Shoulder(12), Hip(24), Knee(26), Ankle(28), Foot(30)
        indices = [12, 24, 26, 28, 30]
        threshold = 0.3 
        for i in indices:
            if landmarks[i].visibility < threshold:
                return None
        return [[landmarks[i].x, landmarks[i].y, landmarks[i].z] for i in indices]

    def process_frame(self, joints):
        shoulder, hip, knee, ankle, foot = joints
        current_time = time.time()
        dt = current_time - self.last_time
        if dt <= 0: dt = 0.001
        
        # 1. Biomechanical Multi-Joint Extraction
        current_knee_angle = KinematicsEngine.calculate_angle(hip, knee, ankle)
        current_hip_angle = KinematicsEngine.calculate_angle(shoulder, hip, knee)
        current_ankle_angle = KinematicsEngine.calculate_angle(knee, ankle, foot)
        
        # 2. Kinematics Derivatives (Velocity / Acceleration)
        if self.last_angle is not None:
            self.angular_velocity = (current_knee_angle - self.last_angle) / dt
            self.velocity_buffer.append(self.angular_velocity)
            self.angular_acceleration = (self.angular_velocity - self.last_velocity) / dt
            if abs(self.angular_velocity) > self.peak_velocity:
                self.peak_velocity = abs(self.angular_velocity)
        
        self.smoothness = KinematicsEngine.calculate_smoothness(list(self.velocity_buffer))
        
        # Update running history frames
        self.last_time = current_time
        self.last_angle = current_knee_angle
        self.last_velocity = self.angular_velocity

        if current_knee_angle < self.min_angle: self.min_angle = current_knee_angle
        if current_knee_angle > self.max_angle: self.max_angle = current_knee_angle

        # 3. State Machine & Temporal Event Loop
        if self.state == "EXTENSION" and current_knee_angle < self.flexion_threshold:
            # Shifted to Flexion Phase
            self.state = "FLEXION"
            self.rest_time = current_time - self.last_rep_time
            self.phase_start_time = current_time
            
        elif self.state == "FLEXION":
            # Track Time Under Tension active phase
            self.time_under_tension += dt
            if current_knee_angle < 90.0: 
                self.hold_duration += dt  # Accumulate peak depth hold time
                
            if current_knee_angle > self.extension_threshold:
                self.state = "EXTENSION"
                rep_dur = current_time - self.phase_start_time
                
                if rep_dur > 1.2:  # Valid Rep check
                    self.rep_count += 1
                    self.rep_durations.append(rep_dur)
                    self.last_rom = self.max_angle - self.min_angle
                    self.all_roms.append(self.last_rom)
                    
                    # Capture historical peaks
                    if self.min_angle < self.peak_flexion: self.peak_flexion = self.min_angle
                    if self.max_angle > self.peak_extension: self.peak_extension = self.max_angle
                    
                    self.rise_duration = rep_dur * 0.45  # Approximation of concentric phase
                    self.last_rep_time = current_time
                else:
                    self.failed_reps += 1
                
                # Reset local peak min/max trackers for next rep window
                self.min_angle, self.max_angle = 180.0, 0.0

        # Calculate Running Consistency Metrics
        consistency = 1.0 if len(self.all_roms) < 2 else float(1.0 - min(np.std(self.all_roms) / 100.0, 1.0))
        avg_vel = float(np.mean(np.abs(list(self.velocity_buffer)))) if self.velocity_buffer else 0.0
        avg_rep_t = float(np.mean(self.rep_durations)) if self.rep_durations else 0.0

        return {
            "knee_angle": round(current_knee_angle, 2),
            "hip_angle": round(current_hip_angle, 2),
            "ankle_angle": round(current_ankle_angle, 2),
            "rom": round(max((self.max_angle - self.min_angle), self.last_rom), 2),
            "peak_flexion": round(self.peak_flexion if self.peak_flexion != 180.0 else current_knee_angle, 2),
            "peak_extension": round(self.peak_extension if self.peak_extension != 0.0 else current_knee_angle, 2),
            "angular_velocity": round(self.angular_velocity, 2),
            "angular_acceleration": round(self.angular_acceleration, 2),
            "peak_velocity": round(self.peak_velocity, 2),
            "average_velocity": round(avg_vel, 2),
            "rep_count": self.rep_count,
            "rep_duration": round(self.rep_durations[-1] if self.rep_durations else 0.0, 2),
            "average_rep_time": round(avg_rep_t, 2),
            "hold_duration": round(self.hold_duration, 2),
            "rise_duration": round(self.rise_duration, 2),
            "exercise_time": round(current_time - self.start_time, 2),
            "rest_time": round(self.rest_time, 2),
            "time_under_tension": round(self.time_under_tension, 2),
            "movement_smoothness": round(self.smoothness, 2),
            "movement_consistency": round(consistency, 2),
            "failed_reps": self.failed_reps
        }

# -----------------------------------------------------------------
# 2. RECOVERY INTELLIGENCE & TRAJECTORY ENGINES
# -----------------------------------------------------------------
class RecoveryIntelligenceEngine:
    def calculate_ris(self, max_rom, movement_smoothness, completed_reps, target_reps, pain_rating):
        mobility = min(max_rom / 130.0, 1.0) * 0.4
        quality = np.clip(movement_smoothness, 0.0, 1.0) * 0.3
        consistency = np.clip(completed_reps / target_reps, 0.0, 1.0) * 0.2
        comfort = ((10 - np.clip(pain_rating, 0, 10)) / 10.0) * 0.1
        return float(round((mobility + quality + consistency + comfort) * 100.0, 1))

class DeviationAnalysisEngine:
    def analyze_trajectory(self, today_ris, yesterday_ris, expected_ris):
        dev = round(today_ris - expected_ris, 1)
        delta = round(today_ris - yesterday_ris, 1)
        trend = "IMPROVING" if delta > 1.5 else ("REGRESSING" if delta < -1.5 else "PLATEAUED")
        
        if dev <= -7.0:
            rec = "Significant deviation below expected recovery path. Reduce workload."
            status = "CRITICAL_LAG"
        elif -7.0 < dev < -2.0:
            rec = "Minor recovery lag identified. Maintain current training volume."
            status = "MODERATE_LAG"
        else:
            rec = "Progress is excellent and fully on track. Ready for load progression."
            status = "ON_TRACK"
            
        return {"deviation": dev, "trend": trend, "clinical_indicator": status, "recommendation": rec}

# -----------------------------------------------------------------
# 3. CORE APPLICATION FRAMEWORK PIPELINE
# -----------------------------------------------------------------
try:
    import mediapipe as mp
    mp_pose_mod = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp_pose_mod.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
except Exception as e:
    print(f"\n🛑 CRITICAL ERROR INITIALIZING MEDIAPIPE: {e}")
    sys.exit(1)

def main():
    cap = cv2.VideoCapture(0)
    
    # Initialize Engine Stack Components
    ai_engine = RehabFeatureExtractor(target_rom=130.0, flexion_threshold=120.0, extension_threshold=160.0)
    recovery_engine = RecoveryIntelligenceEngine()
    deviation_engine = DeviationAnalysisEngine()
    
    TARGET_REPS = 5
    REPORTED_PAIN = 3
    YESTERDAY_SCORE = 65.0   
    EXPECTED_SCORE = 70.0    
    
    print("RehabAI Diagnostics Matrix active. Step back into frame. Press 'q' to quit.")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
            
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = mp_pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            joints = ai_engine.extract_joints(landmarks)
            
            if joints is not None:
                # Process active frame metrics from MediaPipe stream
                f = ai_engine.process_frame(joints)
                
                # Compute composite performance models
                ris_score = recovery_engine.calculate_ris(f['rom'], f['movement_smoothness'], f['rep_count'], TARGET_REPS, REPORTED_PAIN)
                analysis = deviation_engine.analyze_trajectory(ris_score, YESTERDAY_SCORE, EXPECTED_SCORE)
                
                # Derive target variables dynamically
                completion_pct = round((f['rep_count'] / TARGET_REPS) * 100.0, 1)
                success_rate = round((f['rep_count'] / (f['rep_count'] + f['failed_reps']) * 100.0), 1) if (f['rep_count'] + f['failed_reps']) > 0 else 100.0
                lsi_index = 95.0 # Mock fallback (Requires second tracking camera loop for contralateral symmetry analysis)
                
                # Compile Complete Unified Multi-Dimension Feature Vector Array
                feature_vector = [
                    f['knee_angle'], f['hip_angle'], f['ankle_angle'], f['rom'], f['peak_flexion'], f['peak_extension'],
                    f['angular_velocity'], f['angular_acceleration'], f['peak_velocity'], f['average_velocity'],
                    f['rep_duration'], f['average_rep_time'], f['hold_duration'], f['rise_duration'], f['rest_time'], f['time_under_tension'],
                    f['movement_smoothness'], f['movement_consistency'], completion_pct, success_rate, lsi_index
                ]
                
                # Clear Terminal Terminal Buffer Interface Output
                #print("\n" * 40)
                
                # print("==============================")
                # print("MEDIAPIPE")
                # print("==============================\n")
                # print(f"Shoulder   -> X: {joints[0][0]:.2f}, Y: {joints[0][1]:.2f}, Z: {joints[0][2]:.2f}")
                # print(f"Hip        -> X: {joints[1][0]:.2f}, Y: {joints[1][1]:.2f}, Z: {joints[1][2]:.2f}")
                # print(f"Knee       -> X: {joints[2][0]:.2f}, Y: {joints[2][1]:.2f}, Z: {joints[2][2]:.2f}")
                # print(f"Ankle      -> X: {joints[3][0]:.2f}, Y: {joints[3][1]:.2f}, Z: {joints[3][2]:.2f}")
                                
                print("\n==============================")
                print("BIOMECHANICAL FEATURES")
                print("==============================\n")
                print(f"Knee Angle:           {f['knee_angle']}°")
                print(f"Hip Angle:            {f['hip_angle']}°")
                print(f"Ankle Angle:          {f['ankle_angle']}°")
                print(f"ROM:                  {f['rom']}°")
                print(f"Peak Flexion:         {f['peak_flexion']}°")
                print(f"Peak Extension:       {f['peak_extension']}°")

                # print("\n==============================")
                # print("KINEMATIC FEATURES")
                # print("==============================\n")
                # print(f"Angular Velocity:     {f['angular_velocity']} deg/sec")
                # print(f"Angular Acceleration: {f['angular_acceleration']} deg/sec²")
                # print(f"Peak Velocity:        {f['peak_velocity']} deg/sec")
                # print(f"Average Velocity:     {f['average_velocity']} deg/sec")

                # print("\n==============================")
                # print("TEMPORAL FEATURES")
                # print("==============================\n")
                # print(f"Rep Count:            {f['rep_count']}")
                # print(f"Rep Duration:         {f['rep_duration']} sec")
                # print(f"Average Rep Time:     {f['average_rep_time']} sec")
                # print(f"Hold Duration:        {f['hold_duration']} sec")
                # print(f"Rise Duration:        {f['rise_duration']} sec")
                # print(f"Exercise Time:        {f['exercise_time']} sec")
                # print(f"Rest Time:            {f['rest_time']} sec")
                # print(f"Time Under Tension:   {f['time_under_tension']} sec")

                # print("\n==============================")
                # print("MOVEMENT QUALITY")
                # print("==============================\n")
                # print(f"Movement Quality:     {'Optimal' if f['movement_smoothness'] > 0.7 else 'Compensated'}")
                # print(f"Movement Smoothness:  {f['movement_smoothness'] * 100:.1f}%")
                # print(f"Movement Consistency: {f['movement_consistency'] * 100:.1f}%")

                # print("\n==============================")
                # print("FUNCTIONAL FEATURES")
                # print("==============================\n")
                # print(f"Exercise Completion:  {completion_pct}%")
                # print(f"Success Rate:         {success_rate}%")
                # print(f"Failed Reps:          {f['failed_reps']}")
                # print(f"Limb Symmetry Index:  {lsi_index}%")

                # print("\n==============================")
                # print("FEATURE VECTOR")
                # print("==============================\n")
                # print("[")
                # for i in range(0, len(feature_vector), 4):
                #     chunk = feature_vector[i:i+4]
                #     formatted_chunk = ", ".join([f"{val:.2f}" for val in chunk])
                #     print(f"  {formatted_chunk}" + ("," if i+4 < len(feature_vector) else ""))
                # print("]")

                # print("\n==============================")
                # print("RANDOM FOREST")
                # print("==============================\n")
                # print(f"Recovery Score:       {ris_score}/100")
                # print(f"Recovery Trend:       {analysis['trend']}")

                # print("\n==============================")
                # print("CLINICAL OUTPUT")
                # print("==============================\n")
                # print(f"Recommendation:       {analysis['recommendation']}\n")

                # UI Window HUD Draw Overlay
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose_mod.POSE_CONNECTIONS)
                cv2.rectangle(image, (10, 10), (280, 80), (0, 0, 0), -1)
                cv2.putText(image, f"Reps: {f['rep_count']}  | ROM: {f['rom']} deg", (20, 45), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)

        cv2.imshow('RehabAI - Live Analytics Loop', image)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()