"""
RehabAI - Universal Live Multi-Exercise Analytics Pipeline
Sprint 7 Component - v1.3.0 Live Analytics CLI Runner

Usage: python demo_live_universal.py [EXERCISE_NAME] [PATIENT_PHASE (1|2|3)]
Example: python demo_live_universal.py HEEL_SLIDE 1
"""

import cv2
import sys
from ai.utils import RehabAIOrchestrator
from ai.exercise_config import EXERCISE_REGISTRY

def run_universal_live_session():
    available_exercises = list(EXERCISE_REGISTRY.keys())
    
    if len(sys.argv) < 2 or sys.argv[1].upper() not in available_exercises:
        print("=" * 70)
        print("🚨 Error: Missing or invalid exercise parameter selection.")
        print("Options: HEEL_SLIDE, STRAIGHT_LEG_RAISE, LONG_ARC_QUAD, MINI_SQUAT, SIT_TO_STAND")
        print("\nExample: python demo_live_universal.py HEEL_SLIDE 1")
        print("=" * 70)
        sys.exit(1)
        
    selected_exercise = sys.argv[1].upper()
    
    selected_phase = 1
    if len(sys.argv) >= 3:
        try:
            phase_arg = int(sys.argv[2])
            if phase_arg in [1, 2, 3]:
                selected_phase = phase_arg
        except ValueError:
            pass
    
    print("=" * 70)
    print(f"Initializing RehabAI Production Engine Suite v1.3.0...")
    print(f"Targeting Active Context Profile: {selected_exercise}")
    print(f"Configuring Patient Rehab Phase: Phase {selected_phase}")
    print("=" * 70)
    
    orchestrator = RehabAIOrchestrator(exercise_name=selected_exercise, tracking_side="left", patient_phase=selected_phase)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("🚨 Hardware Error: Link failed to webcam device context.")
        sys.exit(1)
        
    print("\n🚀 Camera pipeline online. Adjust setup location into clear field of view.")
    print("Press 'q' inside the display window to cleanly conclude your session.\n")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
                
            frame = cv2.flip(frame, 1)
            ui_frame, metrics, feedback_string = orchestrator.process_frame_pipeline(frame)
            
            sys.stdout.write(
                f"\r[Streaming Frame Telemetry] Live Compliance Rate: {metrics.get('session_compliance_score', 100.0):>5.1f}% | "
                f"Peak Height: {metrics.get('peak_metric', 0.0):>5.1f}"
            )
            sys.stdout.flush()
            
            cv2.imshow(f"RehabAI Functional Dashboard - Active: {selected_exercise}", ui_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\n\nSession broken by direct target escape sequence.")
                break
                
    except KeyboardInterrupt:
        print("\n\nSession interrupted via shell execution command.")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        # Conclude context thread run and fetch final compiled summary dictionary logs
        final_analytics = orchestrator.release_context()
        print("🏁 Operational shutdown complete.")

if __name__ == "__main__":
    run_universal_live_session()