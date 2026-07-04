"""
RehabAI Feature Engineering Engine
Sprint 6 Component - State-Driven Kinematic Analytics Engine

Processes multi-frame transformations to extract repetitions, holds, and velocity metrics.
Includes velocity tracking filters to eliminate low-confidence tracking noise.
"""

import time
from typing import Dict, Any, List
from ai.motion_math import MotionMath

class ExerciseStateTracker:
    def __init__(self):
        """Maintains mutable state tracking across continuous time-series frame processing."""
        self.rep_count = 0
        self.current_direction = "START"  # START -> CONCENTRIC -> HOLD -> ECCENTRIC
        self.hold_start_time = None
        self.last_angle = None
        self.last_time = None
        self.peak_rom = 0.0

class FeatureEngineering:
    # Persistent state storage instances mapped by exercise identifier keys
    _states: Dict[str, ExerciseStateTracker] = {}

    @classmethod
    def _get_state(cls, ex_id: str) -> ExerciseStateTracker:
        if ex_id not in cls._states:
            cls._states[ex_id] = ExerciseStateTracker()
        return cls._states[ex_id]

    @classmethod
    def reset_all_states(cls):
        """Resets all internal exercise state histories to baseline clean tracking loops."""
        cls._states.clear()

    @classmethod
    def process_heel_slide_frame(cls, landmarks: Dict[str, Dict[str, tuple]], side: str, timestamp: float) -> Dict[str, Any]:
        state = cls._get_state("EX-001")
        if not landmarks or "hip" not in landmarks or "knee" not in landmarks or "ankle" not in landmarks:
            return {"knee_flexion_angle": 0.0, "range_of_motion": state.peak_rom, "repetition_count": state.rep_count, "angular_velocity": 0.0}

        hip = landmarks["hip"][side][:3]
        knee = landmarks["knee"][side][:3]
        ankle = landmarks["ankle"][side][:3]
        
        flexion = 180.0 - MotionMath.calculate_3d_angle(hip, knee, ankle)
        
        velocity = 0.0
        if state.last_angle is not None and state.last_time is not None:
            dt = timestamp - state.last_time
            if dt > 0:
                raw_velocity = (flexion - state.last_angle) / dt
                # Noise spike filter: ignore non-physiological velocity values (> 500 deg/s)
                velocity = raw_velocity if abs(raw_velocity) < 500.0 else 0.0
                
        if flexion > state.peak_rom:
            state.peak_rom = round(flexion, 2)

        # Repetition State Transitions
        if state.current_direction == "START" and flexion > 45.0:
            state.current_direction = "CONCENTRIC"
        elif state.current_direction == "CONCENTRIC" and velocity < -5.0:
            state.rep_count += 1
            state.current_direction = "ECCENTRIC"
        elif state.current_direction == "ECCENTRIC" and flexion < 15.0:
            state.current_direction = "START"

        state.last_angle = flexion
        state.last_time = timestamp

        return {
            "knee_flexion_angle": round(flexion, 2),
            "range_of_motion": state.peak_rom,
            "repetition_count": float(state.rep_count),
            "angular_velocity": round(abs(velocity), 2)
        }

    @classmethod
    def process_straight_leg_raise_frame(cls, landmarks: Dict[str, Dict[str, tuple]], side: str, timestamp: float) -> Dict[str, Any]:
        state = cls._get_state("EX-002")
        if not landmarks or "hip" not in landmarks or "knee" not in landmarks or "ankle" not in landmarks:
            return {"hip_flexion_angle": 0.0, "extensor_lag_angle": 0.0, "repetition_count": state.rep_count, "angular_velocity": 0.0}

        hip = landmarks["hip"][side][:3]
        knee = landmarks["knee"][side][:3]
        ankle = landmarks["ankle"][side][:3]
        
        lag = max(0.0, 180.0 - MotionMath.calculate_3d_angle(hip, knee, ankle))
        hip_flex = MotionMath.calculate_planar_slope(hip, knee)
        
        velocity = 0.0
        if state.last_angle is not None and state.last_time is not None:
            dt = timestamp - state.last_time
            if dt > 0:
                raw_velocity = (hip_flex - state.last_angle) / dt
                velocity = raw_velocity if abs(raw_velocity) < 500.0 else 0.0

        if state.current_direction == "START" and hip_flex > 30.0:
            state.current_direction = "CONCENTRIC"
        elif state.current_direction == "CONCENTRIC" and velocity < -3.0:
            state.rep_count += 1
            state.current_direction = "ECCENTRIC"
        elif state.current_direction == "ECCENTRIC" and hip_flex < 10.0:
            state.current_direction = "START"

        state.last_angle = hip_flex
        state.last_time = timestamp

        return {
            "hip_flexion_angle": round(hip_flex, 2),
            "extensor_lag_angle": round(lag, 2),
            "repetition_count": float(state.rep_count),
            "angular_velocity": round(abs(velocity), 2)
        }

    @classmethod
    def process_long_arc_quad_frame(cls, landmarks: Dict[str, Dict[str, tuple]], side: str, timestamp: float) -> Dict[str, Any]:
        state = cls._get_state("EX-003")
        if not landmarks or "hip" not in landmarks or "knee" not in landmarks or "ankle" not in landmarks:
            return {"knee_extension_angle": 0.0, "terminal_extension_deviation": 0.0, "repetition_count": state.rep_count, "angular_velocity": 0.0}

        hip = landmarks["hip"][side][:3]
        knee = landmarks["knee"][side][:3]
        ankle = landmarks["ankle"][side][:3]
        
        ext_angle = MotionMath.calculate_3d_angle(hip, knee, ankle)
        deviation = max(0.0, 180.0 - ext_angle)
        
        velocity = 0.0
        if state.last_angle is not None and state.last_time is not None:
            dt = timestamp - state.last_time
            if dt > 0:
                raw_velocity = (ext_angle - state.last_angle) / dt
                velocity = raw_velocity if abs(raw_velocity) < 500.0 else 0.0

        if state.current_direction == "START" and ext_angle > 140.0:
            state.current_direction = "CONCENTRIC"
        elif state.current_direction == "CONCENTRIC" and velocity < -4.0:
            state.rep_count += 1
            state.current_direction = "ECCENTRIC"
        elif state.current_direction == "ECCENTRIC" and ext_angle < 100.0:
            state.current_direction = "START"

        state.last_angle = ext_angle
        state.last_time = timestamp

        return {
            "knee_extension_angle": round(ext_angle, 2),
            "terminal_extension_deviation": round(deviation, 2),
            "repetition_count": float(state.rep_count),
            "angular_velocity": round(abs(velocity), 2)
        }

    @classmethod
    def process_mini_squat_frame(cls, landmarks: Dict[str, Dict[str, tuple]], side: str, timestamp: float) -> Dict[str, Any]:
        state = cls._get_state("EX-004")
        if not landmarks or "hip" not in landmarks or "knee" not in landmarks or "ankle" not in landmarks:
            return {"knee_flexion_depth": 0.0, "frontal_plane_knee_projection_angle": 0.0, "repetition_count": state.rep_count, "angular_velocity": 0.0}

        hip = landmarks["hip"][side][:3]
        knee = landmarks["knee"][side][:3]
        ankle = landmarks["ankle"][side][:3]
        
        depth = 180.0 - MotionMath.calculate_3d_angle(hip, knee, ankle)
        valgus = MotionMath.calculate_planar_slope(hip, knee)
        
        velocity = 0.0
        if state.last_angle is not None and state.last_time is not None:
            dt = timestamp - state.last_time
            if dt > 0:
                raw_velocity = (depth - state.last_angle) / dt
                velocity = raw_velocity if abs(raw_velocity) < 500.0 else 0.0

        if state.current_direction == "START" and depth > 25.0:
            state.current_direction = "CONCENTRIC"
        elif state.current_direction == "CONCENTRIC" and velocity < -4.0:
            state.rep_count += 1
            state.current_direction = "ECCENTRIC"
        elif state.current_direction == "ECCENTRIC" and depth < 10.0:
            state.current_direction = "START"

        state.last_angle = depth
        state.last_time = timestamp

        return {
            "knee_flexion_depth": round(depth, 2),
            "frontal_plane_knee_projection_angle": round(valgus, 2),
            "repetition_count": float(state.rep_count),
            "angular_velocity": round(abs(velocity), 2)
        }

    @classmethod
    def process_sit_to_stand_frame(cls, landmarks: Dict[str, Dict[str, tuple]], side: str, timestamp: float) -> Dict[str, Any]:
        state = cls._get_state("EX-005")
        if not landmarks or "shoulder" not in landmarks or "hip" not in landmarks or "knee" not in landmarks or "ankle" not in landmarks:
            return {"knee_flexion_angle": 0.0, "trunk_flexion_angle": 0.0, "repetition_count": state.rep_count, "angular_velocity": 0.0}

        shldr = landmarks["shoulder"][side][:3]
        hip = landmarks["hip"][side][:3]
        knee = landmarks["knee"][side][:3]
        ankle = landmarks["ankle"][side][:3]
        
        flexion = 180.0 - MotionMath.calculate_3d_angle(hip, knee, ankle)
        trunk = MotionMath.calculate_planar_slope(shldr, hip)
        
        velocity = 0.0
        if state.last_angle is not None and state.last_time is not None:
            dt = timestamp - state.last_time
            if dt > 0:
                raw_velocity = (flexion - state.last_angle) / dt
                velocity = raw_velocity if abs(raw_velocity) < 500.0 else 0.0

        if state.current_direction == "START" and flexion < 40.0:
            state.current_direction = "CONCENTRIC"
        elif state.current_direction == "CONCENTRIC" and velocity > 5.0:
            state.rep_count += 1
            state.current_direction = "ECCENTRIC"
        elif state.current_direction == "ECCENTRIC" and flexion > 70.0:
            state.current_direction = "START"

        state.last_angle = flexion
        state.last_time = timestamp

        return {
            "knee_flexion_angle": round(flexion, 2),
            "trunk_flexion_angle": round(trunk, 2),
            "repetition_count": float(state.rep_count),
            "angular_velocity": round(abs(velocity), 2)
        }