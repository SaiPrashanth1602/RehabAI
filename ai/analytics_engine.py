"""
RehabAI Comprehensive Clinical Analytics Engine
Sprint 7 - v1.3.0 Core Analytics Component

Processes stateless multi-frame telemetry lists to compute research-ready statistical 
metrics, hold intervals, velocity variations, and overall session compliance profiles.
"""

import numpy as np
from typing import Dict, Any, List, Tuple

class ClinicalAnalyticsEngine:
    @staticmethod
    def calculate_session_analytics(status_history: List[str], 
                                     metric_history: List[float], 
                                     velocity_history: List[float],
                                     exercise_name: str,
                                     exercise_id: str,
                                     total_reps: int,
                                     feedback_instruction: str) -> Dict[str, Any]:
        """
        Transforms raw frame arrays into an integrated summary matrix.
        Calculates means, medians, standard deviations, and time-in-zone density weights.
        """
        # Fallback initialization for empty sessions or failed tracking starts
        summary = {
            "exercise_name": exercise_name,
            "exercise_id": exercise_id,
            "session_duration_sec": 0.0,
            "total_repetitions": int(total_reps),
            "rom_stats": {"max": 0.0, "min": 0.0, "mean": 0.0, "median": 0.0, "std_dev": 0.0},
            "velocity_stats": {"peak": 0.0, "average": 0.0},
            "zone_distribution": {"GREEN_PCT": 0.0, "YELLOW_PCT": 0.0, "RED_PCT": 0.0},
            "session_compliance_score": 100.0,
            "clinical_recommendation": "Tracking incomplete. Ensure full body framing inside camera view bounds."
        }

        if not status_history or not metric_history:
            return summary

        total_frames = len(status_history)
        
        # 1. Calculate Session Time Boundaries (Assuming standard ~30 FPS camera timing offsets)
        summary["session_duration_sec"] = round(total_frames / 30.0, 1)

        # 2. Module 3: ROM Statistics Calculations
        rom_array = np.array(metric_history, dtype=np.float32)
        summary["rom_stats"] = {
            "max": round(float(np.max(rom_array)), 1),
            "min": round(float(np.min(rom_array)), 1),
            "mean": round(float(np.mean(rom_array)), 1),
            "median": round(float(np.median(rom_array)), 1),
            "std_dev": round(float(np.std(rom_array)), 2)
        }

        # 3. Module 4: Velocity Analysis Profiles
        if velocity_history:
            vel_array = np.array([abs(v) for v in velocity_history], dtype=np.float32)
            summary["velocity_stats"] = {
                "peak": round(float(np.max(vel_array)), 1),
                "average": round(float(np.mean(vel_array)), 1)
            }

        # 4. Module 5: Zone Analyzer Percentages
        green_count = status_history.count("GREEN")
        yellow_count = status_history.count("YELLOW")
        red_count = status_history.count("RED")

        summary["zone_distribution"] = {
            "GREEN_PCT": round((green_count / total_frames) * 100.0, 1),
            "YELLOW_PCT": round((yellow_count / total_frames) * 100.0, 1),
            "RED_PCT": round((red_count / total_frames) * 100.0, 1)
        }

        # 5. Composite Compliance Matrix Formulation
        # Deduct weight penalties dynamically based on risk-exposure durations
        penalty = (red_count * 5.0) + (yellow_count * 1.5)
        raw_compliance = max(0.0, 100.0 - (penalty / total_frames) * 10.0)
        summary["session_compliance_score"] = round(raw_compliance, 1)
        summary["clinical_recommendation"] = feedback_instruction

        return summary

    @staticmethod
    def print_terminal_summary_hud(summary: Dict[str, Any]):
        """Outputs an beautifully structured, clean text-based clinical dashboard summary report."""
        print("\n" + "="*60)
        print(f"📋 REHABAI CLINICAL SESSION SUMMARY REPORT - v1.3.0")
        print("="*60)
        print(f"Exercise Target:      {summary['exercise_name']} ({summary['exercise_id']})")
        print(f"Session Duration:     {summary['session_duration_sec']} seconds")
        print(f"Total Repetitions:    {summary['total_repetitions']} reps")
        print("-" * 60)
        print(f"Anatomical ROM Specs:")
        print(f"  » Peak Achieved:    {summary['rom_stats']['max']}°")
        print(f"  » Baseline Rest:    {summary['rom_stats']['min']}°")
        print(f"  » Average Flexion:  {summary['rom_stats']['mean']}°")
        print(f"  » Deviation (SD):   {summary['rom_stats']['std_dev']}°")
        print("-" * 60)
        print(f"Kinematic Velocity Specs:")
        print(f"  » Maximum Speed:    {summary['velocity_stats']['peak']} deg/s")
        print(f"  » Mean Pace Speed:  {summary['velocity_stats']['average']} deg/s")
        print("-" * 60)
        print(f"Safety Exposure Windows:")
        print(f"  » Time in GREEN:    {summary['zone_distribution']['GREEN_PCT']}%")
        print(f"  » Time in YELLOW:   {summary['zone_distribution']['YELLOW_PCT']}%")
        print(f"  » Time in RED:      {summary['zone_distribution']['RED_PCT']}%")
        print(f"⭐ Session Compliance Rating: {summary['session_compliance_score']}%")
        print("-" * 60)
        print(f"Feedback Guidance: {summary['clinical_recommendation']}")
        print("="*60 + "\n")