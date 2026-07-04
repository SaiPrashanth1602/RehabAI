"""
RehabAI MediaPipe Acquisition Engine
Sprint 2 Component
"""

import cv2
import mediapipe as mp
from typing import Optional

class MediaPipeEngine:
    def __init__(self, static_image_mode: bool = False, model_complexity: int = 1, 
                 min_detection_confidence: float = 0.5, min_tracking_confidence: float = 0.5):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

    def process_frame(self, frame) -> Optional[any]:
        if frame is None:
            return None
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        if results.pose_landmarks:
            return results.pose_landmarks.landmark
        return None

    def close(self):
        self.pose.close()