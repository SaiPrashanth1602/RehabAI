"""
RehabAI V1 - Kinematic Preprocessing Pipelines
"""
import numpy as np

def resample_sequence(matrix, target_frames=100):
    """Aligns timelines using 1D signal interpolation."""
    total_frames, channels = matrix.shape
    if total_frames == target_frames:
        return matrix
        
    source_indices = np.linspace(0, total_frames - 1, num=total_frames)
    target_indices = np.linspace(0, total_frames - 1, num=target_frames)
    
    aligned_matrix = np.zeros((target_frames, channels))
    for c in range(channels):
        aligned_matrix[:, c] = np.interp(target_indices, source_indices, matrix[:, c])
        
    return aligned_matrix