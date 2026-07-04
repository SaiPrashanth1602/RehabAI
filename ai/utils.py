"""
RehabAI Core Pipeline Orchestration Utility
Sprint 7 Component - v1.3.0 Integrated Analytics Orchestrator Core

Coordinates real-time data transformations across modules, filters noise,
and processes multi-frame session analytics upon pipeline shutdown loops.
"""

import cv2
import time
import uuid
import numpy as np
from typing import Dict, List, Any, Tuple

from ai.exercise_config import get_exercise_config
from ai.mediapipe_engine import MediaPipeEngine
from ai.landmark_extractor import LandmarkExtractor
from ai.feature_engineering import FeatureEngineering
from ai.feature_vector import FeatureVectorPipeline
from ai.predictor import RulePredictor
from ai.recommendation_engine import RecommendationEngine
from ai.analytics_engine import ClinicalAnalyticsEngine

class RehabAIOrchestrator:
    def __init__(self, exercise_name: str, tracking_side: str = "left", patient_phase: int = 1):
        """Initializes system modules bound to exercise targets, phases, and analytical aggregators."""
        self.config = get_exercise_config(exercise_name)
        self.side = tracking_side
        self.phase = patient_phase
        self.session_id = f"SESS-{uuid.uuid4().hex[:8].upper()}"
        
        self.engine = MediaPipeEngine()
        self.predictor = RulePredictor(self.config, patient_phase=self.phase)
        
        # Operational historical time-series memory frames
        self.status_history: List[str] = []
        self.metric_history: List[float] = []
        self.velocity_history: List[float] = []
        
        # Local structural cache parameters
        self.cached_reps = 0
        self.cached_speed = 0.0
        self.cached_compliance = 100.0
        self.cached_feedback = "Initializing tracking field vectors..."
        
        FeatureEngineering.reset_all_states()

    def process_frame_pipeline(self, frame: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any], str]:
        """Runs the complete data pipeline and handles live HUD text overlays."""
        h, w, _ = frame.shape
        ui_frame = frame.copy()
        current_timestamp = time.monotonic()
        
        raw_landmarks = self.engine.process_frame(frame)
        
        # Establish zeroed safe fallback defaults
        features = {}
        analytics = {"session_compliance_score": self.cached_compliance, "critical_violation_count": 0}
        status = "GREEN"
        visibility_passed = False
        
        ex_id = self.config["id"]

        if raw_landmarks:
            extracted = LandmarkExtractor.extract_required_landmarks(raw_landmarks, self.config["landmarks"])
            if extracted:
                # Landmark Visibility Verification Threshold Barrier Check
                visibility_passed = True
                for joint in self.config["landmarks"]:
                    left_vis = extracted[joint]["left"][3]
                    right_vis = extracted[joint]["right"][3]
                    target_vis = left_vis if self.side == "left" else right_vis
                    if target_vis < 0.60:
                        visibility_passed = False
                        break
                
                if not visibility_passed:
                    self.cached_feedback = "TRACKING WARNING: Step back. Ensure your full profile view is visible."
                else:
                    # Dynamic Exercise Routing Core
                    if ex_id == "EX-001":
                        features = FeatureEngineering.process_heel_slide_frame(extracted, self.side, current_timestamp)
                        metric_val = features["knee_flexion_angle"]
                    elif ex_id == "EX-002":
                        features = FeatureEngineering.process_straight_leg_raise_frame(extracted, self.side, current_timestamp)
                        metric_val = features["hip_flexion_angle"]
                    elif ex_id == "EX-003":
                        features = FeatureEngineering.process_long_arc_quad_frame(extracted, self.side, current_timestamp)
                        metric_val = features["knee_extension_angle"]
                    elif ex_id == "EX-004":
                        features = FeatureEngineering.process_mini_squat_frame(extracted, self.side, current_timestamp)
                        metric_val = features["knee_flexion_depth"]
                    elif ex_id == "EX-005":
                        features = FeatureEngineering.process_sit_to_stand_frame(extracted, self.side, current_timestamp)
                        metric_val = features["knee_flexion_angle"]

                    self.metric_history.append(metric_val)
                    self.cached_speed = features.get("angular_velocity", 0.0)
                    self.velocity_history.append(self.cached_speed)
                    
                    f_vector = FeatureVectorPipeline.serialize_features(features, self.config["features"])
                    status = self.predictor.predict(f_vector)
                    self.status_history.append(status)
                    
                    # Accumulate live caching definitions
                    if hasattr(FeatureEngineering, '_states') and ex_id in FeatureEngineering._states:
                        self.cached_reps = FeatureEngineering._states[ex_id].rep_count
                        
                    # Calculate live performance trends for display layers
                    green_count = self.status_history.count("GREEN")
                    self.cached_compliance = round((green_count / len(self.status_history)) * 100.0, 1)
                    self.cached_feedback = RecommendationEngine.generate_feedback(ex_id, features, {"critical_violation_count": self.status_history.count("RED"), "session_compliance_score": self.cached_compliance})

                try:
                    for joint in self.config["landmarks"]:
                        coords = extracted[joint][self.side]
                        pt = (int(coords[0] * w), int(coords[1] * h))
                        color = (0, 255, 255) if not visibility_passed else (0, 0, 255) if status == "RED" else (0, 255, 0)
                        cv2.circle(ui_frame, pt, 6, color, -1)
                except Exception:
                    pass

        # Text Layout Configuration Panel HUD Display Renders
        cv2.putText(ui_frame, f"REHAB-ANALYTICS v1.3.0 (Active Core)", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(ui_frame, f"Completed Reps: {int(self.cached_reps)}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(ui_frame, f"Velocity Rate:  {self.cached_speed} deg/s", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(ui_frame, f"Live Clean Score: {self.cached_compliance}%", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 255, 100), 2)
        
        cv2.rectangle(ui_frame, (10, h - 60), (w - 10, h - 10), (20, 20, 20), -1)
        cv2.putText(ui_frame, self.cached_feedback, (20, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
        
        analytics_map = {"session_compliance_score": self.cached_compliance, "peak_metric": max(self.metric_history) if self.metric_history else 0.0}
        return ui_frame, analytics_map, self.cached_feedback

    def release_context(self) -> Dict[str, Any]:
        """Triggers the clinical analytics compiler to output session statistical dashboards."""
        session_summary = ClinicalAnalyticsEngine.calculate_session_analytics(
            status_history=self.status_history,
            metric_history=self.metric_history,
            velocity_history=self.velocity_history,
            exercise_name=self.config["name"],
            exercise_id=self.config["id"],
            total_reps=self.cached_reps,
            feedback_instruction=self.cached_feedback
        )
        
        # Display the final summary dashboard onto terminal output lines
        ClinicalAnalyticsEngine.print_terminal_summary_hud(session_summary)
        
        self.engine.close()
        return session_summary