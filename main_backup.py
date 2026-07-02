import sys
import subprocess
import importlib

def verify_environment():
    """Bypasses aggressive environment locks to prevent subprocess compilation crashes."""
    print("[*] Initializing RehabAI Pre-Flight Environment Checks...")
    try:
        import numpy as np
        import cv2
        import mediapipe as mp
        print(f"    [✓] NumPy version: {np.__version__}")
        print(f"    [✓] OpenCV version: {getattr(cv2, '__version__', 'Unknown')}")
        print("    [✓] Environment matrix loaded.")
    except ImportError as e:
        print(f"[!] Missing dependency: {e}. Please install it manually via pip.")
        sys.exit(1)

# Run the pre-flight check BEFORE importing your AI engine
verify_environment()

# Now it's safe to import your actual code components
import cv2
import mediapipe as mp
from ai.engine import RehabAIEngine

# ... rest of your main() function remains exactly the same ...

def main():
    # 1. Initialize AI Engine
    engine = RehabAIEngine(patient_id="P001", exercise="Knee_Flexion")
    
    # Setup Camera
    cap = cv2.VideoCapture(0)
    
    # Transparency factor
    alpha = 0.4 
    
    print("RehabAI Production Engine Active. Press 'q' to quit.")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        # 3. Analyze frame
        data = engine.analyze_frame(frame)
        
        # 4. Prepare UI variables
        is_waiting = (data['status'] == "WAITING_FOR_SETUP")
        
        # Colors: Amber (0, 215, 255) for setup, Green (0, 255, 0) for active
        status_color = (0, 215, 255) if is_waiting else (0, 255, 0)
        
        # Placeholders
        display_rom = "--" if is_waiting else f"{data['rom']} deg"
        display_reps = "--" if is_waiting else f"{data['rep_count']}"
        display_trend = data['trend'] if not is_waiting else "N/A"
        
        # 5. Draw Transparent UI Overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (550, 230), (0, 0, 0), -1) 
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        # 6. Draw Text
        # Line 1: Status
        cv2.putText(frame, f"STATUS: {data['status']}", (20, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2, cv2.LINE_AA)
        
        # Line 2: Exercise Name
        cv2.putText(frame, "Exercise: Knee Flexion", (20, 95), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        
        # Line 3: Metrics
        cv2.putText(frame, f"ROM: {display_rom} | Reps: {display_reps}", (20, 140), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        
        # Line 4: Recovery Trend
        cv2.putText(frame, f"Recovery Trend: {display_trend}", (20, 185), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2, cv2.LINE_AA)
        
        # Show feed
        cv2.imshow('RehabAI Production Engine', frame)
        
        if cv2.waitKey(1) == ord('q'): 
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()