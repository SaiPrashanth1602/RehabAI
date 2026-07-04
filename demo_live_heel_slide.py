"""
RehabAI - Sprint 1 End-to-End Live Execution Demo
Day 7 Component

Orchestrates live system performance capturing frames directly from hardware 
and passing them dynamically through our unified clinical assessment pipeline.
"""

import cv2
import sys
from ai.utils import RehabAIOrchestrator

def run_live_rehab_session():
    print("=" * 60)
    print("Initializing RehabAI Live Engine Pipeline...")
    print("Exercise Target Profile: HEEL_SLIDE (Phase I Baseline)")
    print("Tracking Side Constraint: LEFT")
    print("=" * 60)
    
    # Initialize our central system coordination orchestrator block
    orchestrator = RehabAIOrchestrator(exercise_name="HEEL_SLIDE", tracking_side="left")
    
    # Establish connection handle to target hardware camera device index 0
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("🚨 Error: Could not establish a communication pipe to webcam index 0.")
        print("Please check hardware access permissions and retry execution.")
        sys.exit(1)
        
    print("\n🚀 Live stream active. Position your full body in side-profile view.")
    print("Press 'q' at any time inside the video window to safely conclude the session.\n")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("⚠️ Frame drop detected from video acquisition channel. Skipping loop iteration...")
                continue
                
            # Mirror the frame horizontally to present an intuitive mirror-like interface for the patient
            frame = cv2.flip(frame, 1)
            
            # Pipe frame through the complete end-to-end data processing layers
            ui_frame, session_metrics, active_feedback = orchestrator.process_frame_pipeline(frame)
            
            # Output live tracking values directly to terminal stdout stream for monitoring logs
            sys.stdout.write(
                f"\r[Telemetry] Flexion: {session_metrics.get('peak_range_of_motion', 0.0):<5.1f}° | "
                f"Compliance Score: {session_metrics.get('session_compliance_score', 100.0):<5.1f}% | "
                f"Trend: {session_metrics.get('performance_trend', 'STABLE'):<9}"
            )
            sys.stdout.flush()
            
            # Render the final interactive annotated GUI dashboard frame
            cv2.imshow("RehabAI Clinical Assessment Dashboard - Sprint 1", ui_frame)
            
            # Poll keyboard buffer to check if user registers escape sequence ('q' key)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\n\nExiting frame loop by explicit user request.")
                break
                
    except KeyboardInterrupt:
        print("\n\nSession broken via standard terminal keyboard interrupt event.")
        
    finally:
        # Gracefully release system physical resources and context handles
        print("Releasing video capture streams...")
        cap.release()
        cv2.destroyAllWindows()
        orchestrator.release_context()
        print("=" * 60)
        print("🏁 Session concluded successfully. All modules closed cleanly.")
        print("=" * 60)

if __name__ == "__main__":
    run_live_rehab_session()