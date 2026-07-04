"""
RehabAI Feature Vector Serialization Component
Sprint 2 Component
"""

import numpy as np
from typing import Dict, List, Any

class FeatureVectorPipeline:
    @staticmethod
    def serialize_features(features_dict: Dict[str, Any], required_features: List[str]) -> np.ndarray:
        vector_output = []
        for feature in required_features:
            vector_output.append(float(features_dict.get(feature, 0.0)))
        return np.array(vector_output, dtype=np.float32)