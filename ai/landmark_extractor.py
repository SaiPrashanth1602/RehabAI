"""
RehabAI Landmark Filtering Extractor
Sprint 2 Component
"""

from typing import Dict, List, Optional
from ai.exercise_config import MEDIAPIPE_LANDMARK_MAP

class LandmarkExtractor:
    @staticmethod
    def extract_required_landmarks(raw_landmarks: Optional[list], required_joints: List[str]) -> Dict[str, Dict[str, tuple]]:
        extracted_data = {}
        if not raw_landmarks:
            return extracted_data

        for joint in required_joints:
            if joint not in MEDIAPIPE_LANDMARK_MAP:
                raise ValueError(f"Requested joint '{joint}' is not mapped in the core config system.")
                
            left_idx, right_idx = MEDIAPIPE_LANDMARK_MAP[joint]
            left_lm = raw_landmarks[left_idx]
            right_lm = raw_landmarks[right_idx]
            
            extracted_data[joint] = {
                "left": (left_lm.x, left_lm.y, left_lm.z, left_lm.visibility),
                "right": (right_lm.x, right_lm.y, right_lm.z, right_lm.visibility)
            }
        return extracted_data