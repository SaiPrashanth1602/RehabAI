"""
RehabAI Motion Mathematics Library
Sprint 5 - Core Mathematical Layer

Stateless utility functions handling deterministic vector geometry.
"""

import numpy as np
from typing import Tuple

class MotionMath:
    @staticmethod
    def calculate_3d_angle(p1: Tuple[float, float, float], 
                           p2: Tuple[float, float, float], 
                           p3: Tuple[float, float, float]) -> float:
        """Formula: theta = arccos( (v1 . v2) / (||v1|| * ||v2||) ) at vertex p2."""
        v1 = np.array(p1) - np.array(p2)
        v2 = np.array(p3) - np.array(p2)
        
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        
        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0
            
        cosine_angle = np.clip(dot_product / (norm_v1 * norm_v2), -1.0, 1.0)
        return float(np.degrees(np.arccos(cosine_angle)))

    @staticmethod
    def calculate_planar_slope(p1: Tuple[float, float, float], p2: Tuple[float, float, float]) -> float:
        """Calculates slope angle of a vector relative to horizontal axis using arctan2."""
        return float(np.abs(np.degrees(np.arctan2(p2[1] - p1[1], p2[0] - p1[0]))))

    @staticmethod
    def calculate_euclidean_distance(p1: Tuple[float, float, float], p2: Tuple[float, float, float]) -> float:
        """Calculates absolute spatial distance between two tracking coordinates."""
        return float(np.linalg.norm(np.array(p1) - np.array(p2)))