import cv2
import numpy as np
import sys
import json  # Added for the API payload export

# Import all custom modular layers of RehabAI
from movement_engine import RehabFeatureExtractor
from .recovery_engine import RecoveryIntelligenceEngine
from .deviation_engine import DeviationAnalysisEngine

try:
    import mediapipe as mp
    from mediapipe.solutions import pose as mp_pose_mod
    from mediapipe.solutions import drawing_utils as mp_drawing_mod

    mp_pose = mp_pose_mod.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    mp_drawing = mp_drawing_mod
except Exception as e:
    print(f"\n🛑 CRITICAL ERROR: {e}")
    sys.exit(1)

def main():
    cap = cv2.VideoCapture(0) 
    
    # Initialize the entire AI Stack
    ai_engine = RehabFeatureExtractor(target_rom=130.0, flexion_threshold=120.0, extension_threshold=160.0)
    recovery_engine = RecoveryIntelligenceEngine(target_rom=130.0)
    deviation_engine = DeviationAnalysisEngine()
    
    # Clinical Variables for MVP Demonstration
    TARGET_REPS = 5
    REPORTED_PAIN = 3
    YESTERDAY_SCORE = 65.0   # Mock historical baseline
    EXPECTED_SCORE = 70.0    # Mock targeted recovery checkpoint
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = mp_pose.process(image)
        
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        if results.pose_landmarks:
            try:
                landmarks = results.pose_landmarks.landmark
                
                # 1. Coordinate Extraction
                shoulder = ai_engine.extract_joints(landmarks)  # Pre-fetches the multi-landmark array
                hip = ai_engine.extract_from_mediapipe(landmarks, [mp_pose_mod.PoseLandmark.RIGHT_HIP.value])[0]
                knee = ai_engine.extract_from_mediapipe(landmarks, [mp_pose_mod.PoseLandmark.RIGHT_KNEE.value])[0]
                ankle = ai_engine.extract_from_mediapipe(landmarks, [mp_pose_mod.PoseLandmark.RIGHT_ANKLE.value])[0]
                
                # Extract optional tracking landmarks natively for the calculation layer
                sh_coord = [landmarks[12].x, landmarks[12].y, landmarks[12].z] if landmarks[12].visibility > 0.3 else None
                ft_coord = [landmarks[30].x, landmarks[30].y, landmarks[30].z] if landmarks[30].visibility > 0.3 else None

                # 2. Movement Calculations
                features = ai_engine.process_frame(hip, knee, ankle, shoulder=sh_coord, foot=ft_coord)
                
                # 3. Score Synthesis
                ris_score = recovery_engine.calculate_ris(
                    max_rom=features['rom'],
                    movement_quality=features['movement_quality'],
                    completed_reps=features['rep_count'],
                    target_reps=TARGET_REPS,
                    pain_rating=REPORTED_PAIN
                )
                
                # 4. Trajectory Deviation Analysis
                analysis = deviation_engine.analyze_trajectory(
                    today_ris=ris_score,
                    yesterday_ris=YESTERDAY_SCORE,
                    expected_ris=EXPECTED_SCORE
                )

                # 5. Construct the API Payload for Backend Consumption
                short_rec = analysis['recommendation'].split('.')[0] + "." # Grabs just the first sentence
                
                # Derived analytical metrics
                completion_pct = min(features['rep_count'] / TARGET_REPS, 1.0) * 100
                total_attempts = features['rep_count'] + features.get('failed_reps', 0)
                success_rate_str = f"{round((features['rep_count'] / total_attempts) * 100, 1)}%" if total_attempts > 0 else "N/A"
                
                # Placeholder LSI tracking setup
                # Placeholder metric. Requires Bilateral Leg Tracking cameras.
                lsi_display = "NOT AVAILABLE (Requires Bilateral Leg Tracking)"

                api_payload = {
                    "status": ai_engine.state,
                    "rep_count": features['rep_count'],
                    "rom": features['rom'],
                    "recovery_score": ris_score,
                    "recovery_deviation": analysis['deviation'],
                    "trend": analysis['trajectory_status'],
                    "recommendation": short_rec
                }
                
                # --- EXACT TERMINAL DIAGNOSTIC ORDER LAYOUT ---
                print("\n" * 40)  # Refresh feed
                print("=====================================")
                print("MEDIAPIPE LANDMARKS")
                print("=====================================\n")
                print(f"Shoulder   -> X: {landmarks[12].x:.2f}, Y: {landmarks[12].y:.2f}, Z: {landmarks[12].z:.2f}")
                print(f"Hip        -> X: {hip[0]:.2f}, Y: {hip[1]:.2f}, Z: {hip[2]:.2f}")
                print(f"Knee       -> X: {knee[0]:.2f}, Y: {knee[1]:.2f}, Z: {knee[2]:.2f}")
                print(f"Ankle      -> X: {ankle[0]:.2f}, Y: {ankle[1]:.2f}, Z: {ankle[2]:.2f}")

                print("\n=====================================")
                print("BIOMECHANICAL FEATURES")
                print("=====================================\n")
                print(f"Knee Angle:           {features.get('knee_angle', features['angle'])}°")
                print(f"Hip Angle:            {features.get('hip_angle', 170.0)}°")
                print(f"Ankle Angle:          {features.get('ankle_angle', 110.0)}°")
                print(f"ROM:                  {features['rom']}°")
                print(f"Peak Flexion:         {features.get('peak_flexion', features['angle'])}°")
                print(f"Peak Extension:       {features.get('peak_extension', features['angle'])}°")

                print("\n=====================================")
                print("KINEMATIC FEATURES")
                print("=====================================\n")
                print(f"Angular Velocity:     {features.get('angular_velocity', 0.0)} deg/sec")
                print(f"Angular Acceleration: {features.get('angular_acceleration', 0.0)} deg/sec²")
                print(f"Peak Velocity:        {features.get('peak_velocity', 0.0)} deg/sec")
                print(f"Average Velocity:     {features.get('average_velocity', 0.0)} deg/sec")

                print("\n=====================================")
                print("TEMPORAL FEATURES")
                print("=====================================\n")
                print(f"Rep Count:            {features['rep_count']}")
                print(f"Rep Duration:         {features.get('rep_duration', 0.0)} sec")
                print(f"Hold Duration:        {features.get('hold_duration', 0.0)} sec")
                print(f"Average Rep Time:     {features.get('average_rep_time', 0.0)} sec")
                print(f"Exercise Time:        {features.get('exercise_time', 0.0)} sec")
                print(f"Rest Time:            {features.get('rest_time', 0.0)} sec")
                print(f"Time Under Tension:   {features.get('time_under_tension', 0.0)} sec")

                print("\n=====================================")
                print("MOVEMENT QUALITY")
                print("=====================================\n")
                print(f"Movement Quality Score : {features['movement_quality']:.2f}%")
                print(f"Classification         : {'Optimal' if features.get('movement_smoothness', 1.0) > 0.7 else 'Compensated'}")
                print(f"Movement Smoothness   : {features.get('movement_smoothness', 1.0) * 100:.1f}%")
                print(f"ROM Consistency        : {features.get('rom_consistency', 1.0) * 100:.1f}%")

                print("\n=====================================")
                print("FUNCTIONAL FEATURES")
                print("=====================================\n")
                print(f"Exercise Completion:  {completion_pct:.1f}%")
                print(f"Success Rate:         {success_rate_str}")
                print(f"Failed Rep Count:     {features.get('failed_reps', 0)}")
                print(f"Limb Symmetry Index:  {lsi_display}")

                print("\n=====================================")
                print("FEATURE ENGINEERING")
                print("=====================================\n")
                print("Raw Landmarks\n        ↓\nBiomechanical Features\n        ↓\nKinematic Features\n        ↓\nTemporal Features\n        ↓\nMovement Quality Features\n        ↓\nFunctional Features\n        ↓\nFeature Vector")

                print("\n=====================================")
                print("FEATURE VECTOR")
                print("=====================================\n")
                print(f"Knee Angle            : {features.get('knee_angle', features['angle'])}°")
                print(f"Hip Angle             : {features.get('hip_angle', 170.0)}°")
                print(f"Ankle Angle           : {features.get('ankle_angle', 110.0)}°")
                print(f"ROM                   : {features['rom']}°")
                print(f"Peak Flexion          : {features.get('peak_flexion', features['angle'])}°")
                print(f"Peak Extension        : {features.get('peak_extension', features['angle'])}°")
                print(f"Angular Velocity      : {features.get('angular_velocity', 0.0)} deg/sec")
                print(f"Angular Acceleration  : {features.get('angular_acceleration', 0.0)} deg/sec²")
                print(f"Peak Velocity         : {features.get('peak_velocity', 0.0)} deg/sec")
                print(f"Average Velocity      : {features.get('average_velocity', 0.0)} deg/sec")
                print(f"Rep Duration          : {features.get('rep_duration', 0.0)} sec")
                print(f"Hold Duration         : {features.get('hold_duration', 0.0)} sec")
                print(f"Average Rep Time      : {features.get('average_rep_time', 0.0)} sec")
                print(f"Exercise Time         : {features.get('exercise_time', 0.0)} sec")
                print(f"Rest Time             : {features.get('rest_time', 0.0)} sec")
                print(f"Time Under Tension    : {features.get('time_under_tension', 0.0)} sec")
                print(f"Movement Quality Score: {features['movement_quality']:.2f}%")
                print(f"Movement Smoothness   : {features.get('movement_smoothness', 1.0) * 100:.1f}%")
                print(f"ROM Consistency       : {features.get('rom_consistency', 1.0) * 100:.1f}%")
                print(f"Exercise Completion   : {completion_pct:.1f}%")
                print(f"Success Rate          : {success_rate_str}")
                print(f"Limb Symmetry Index   : {lsi_display}\n")

                # Generate live structural float list for array print output
                f_vector = [
                    float(features.get('knee_angle', features['angle'])), float(features.get('hip_angle', 170.0)),
                    float(features.get('ankle_angle', 110.0)), float(features['rom']),
                    float(features.get('peak_flexion', features['angle'])), float(features.get('peak_extension', features['angle'])),
                    float(features.get('angular_velocity', 0.0)), float(features.get('angular_acceleration', 0.0)),
                    float(features.get('peak_velocity', 0.0)), float(features.get('average_velocity', 0.0)),
                    float(features.get('rep_duration', 0.0)), float(features.get('hold_duration', 0.0)),
                    float(features.get('average_rep_time', 0.0)), float(features.get('exercise_time', 0.0)),
                    float(features.get('rest_time', 0.0)), float(features.get('time_under_tension', 0.0)),
                    float(features['movement_quality']), float(features.get('movement_smoothness', 1.0)),
                    float(features.get('rom_consistency', 1.0)), float(completion_pct), 0.0
                ]
                print(f"Feature Vector Size : {len(f_vector)} Features\n")
                print(json.dumps([round(num, 2) for num in f_vector]))

                print("\n=====================================")
                print("RECOVERY INTELLIGENCE ENGINE")
                print("=====================================\n")
                print(f"Recovery Score:       {ris_score}/100")
                print(f"Recovery Trend:       {analysis['trend']}")

                print("\n=====================================")
                print("CLINICAL OUTPUT")
                print("=====================================\n")
                print(f"Recommendation:       {short_rec}\n")

                # --- GRAPHICAL HUD RENDERING ---
                knee_px = tuple(np.multiply(knee[:2], [640, 480]).astype(int))
                cv2.putText(image, f"{features['angle']} deg", knee_px, 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
                
                cv2.rectangle(image, (10, 10), (360, 260), (0, 0, 0), -1)
                cv2.putText(image, "RehabAI - Core Intelligent Loop", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(image, f"Status: {ai_engine.state}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)
                cv2.putText(image, f"Reps: {features['rep_count']} / {TARGET_REPS}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
                cv2.putText(image, f"Current ROM: {features['rom']} deg", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
                
                r_color = (0, 255, 0) if analysis['clinical_indicator'] == "ON_TRACK" else ((0, 255, 255) if analysis['clinical_indicator'] == "MODERATE_LAG" else (0, 0, 255))
                cv2.putText(image, f"Recovery Score: {ris_score}", (20, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.6, r_color, 2)
                cv2.putText(image, f"Recovery Deviation: {analysis['deviation']}", (20, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
                cv2.putText(image, f"Recovery Status: {analysis['trajectory_status']}", (20, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
                
                cv2.rectangle(image, (10, 440), (630, 475), (0, 0, 0), -1)
                cv2.putText(image, f"Rec: {short_rec}", (20, 462), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

            except Exception as e:
                pass 
            
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose_mod.POSE_CONNECTIONS)
        
        cv2.imshow('RehabAI - Movement Intelligence', image)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()