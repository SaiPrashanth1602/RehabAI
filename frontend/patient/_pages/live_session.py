"""
RehabAI V1 - Patient Live Rehabilitation Tracking Portal
Author: Sai Prashanth Ramesh & Core Systems Architecture
"""
import streamlit as st
import cv2
import requests
import numpy as np
import time
import sys
import os
import pandas as pd
from datetime import datetime


import mediapipe as mp
mp_pose_mod = mp.solutions.pose
mp_drawing_mod = mp.solutions.drawing_utils
mp_drawing_styles_mod = mp.solutions.drawing_styles

from ai.movement_engine import RehabFeatureExtractor
from ml.inference import RehabInferenceEngine
from ml.feature_extractor import BiomechanicalExtractor
from frontend.common.utils.config import API_URL  # Unified endpoint utility

def render_live_session():
    # 1. RESOLVE RUNTIME LIFECYCLE ROUTING CONTEXT TOKENS
    # Read from 'session_id' — consistent key used by both exercise_detail.py and dashboard.py
    session_id = st.session_state.get("session_id")

    # Handle legacy dict format from older start_session responses
    if isinstance(session_id, dict):
        session_id = session_id.get("session_id") or session_id.get("id")

    patient_id = st.session_state.get("patient_id", "PAT_24MIS1033")
    exercise_name = st.session_state.get("exercise_name", "Sit-to-Stand")
    exercise_code = st.session_state.get("exercise_code", "m05")

    if not session_id:
        st.error("🚨 **Session Context Token Disconnected**: Please select an item inside your active Treatment Queue to initialize tracking.")
        if st.button("Return to Regimen"):
            # Use the correct page key that matches the router and sidebar
            st.session_state.current_page = "静 My Rehabilitation"
            st.rerun()
        return

    st.caption(f"Session Token: `{session_id}` | Patient ID: `{patient_id}` | Regimen: `{exercise_name}`")

    # 2. ALLOCATE CORE MEMORY BUFFERS AND HISTORY LISTS
    # Only reset state if this is a new session (prevents state loss on rerun)
    if "current_active_session_tracking" not in st.session_state or st.session_state.current_active_session_tracking != session_id:
        st.session_state.rehab_extractor = RehabFeatureExtractor(target_rom=130.0, flexion_threshold=120.0, extension_threshold=160.0)
        st.session_state.live_angle_history_buffer = []
        st.session_state.current_active_session_tracking = session_id

        st.session_state.correct_reps = 0
        st.session_state.incorrect_reps = 0
        st.session_state.total_reps = 0
        st.session_state.accumulated_confidences = []
        st.session_state.rom_values = []
        st.session_state.quality_scores = []
        st.session_state.duration_values = []

        st.session_state.rep_history_table_data = []
        st.session_state.console_logs = ["🤖 Telemetry active..."]
        st.session_state.last_latency = {"extract": 0.0, "resample": 0.0, "infer": 0.0, "total": 0.0}

        # Track session start time for accurate duration calculation
        st.session_state.session_start_time = time.time()

    if "ml_inference_engine" not in st.session_state:
        st.session_state.ml_inference_engine = RehabInferenceEngine()

    extractor = st.session_state.rehab_extractor
    ml_engine = st.session_state.ml_inference_engine

    try:
        requests.post(f"{API_URL}/sessions/camera/start", json={"session_id": str(session_id)}, timeout=3.0)
    except Exception:
        pass  # Non-critical — camera status flag only

    # =======================================================================
    # ⚡ LIGHTWEIGHT CORE HUD
    # =======================================================================
    top_stat_row = st.columns(4)
    with top_stat_row[0]:
        total_reps_metric = st.empty()
    with top_stat_row[1]:
        correct_reps_metric = st.empty()
    with top_stat_row[2]:
        incorrect_reps_metric = st.empty()
    with top_stat_row[3]:
        accuracy_metric = st.empty()

    left_feed_col, right_debug_col = st.columns([5, 4])

    with left_feed_col:
        frame_window = st.image([])
        stop_session = st.button("🛑 Stop & Save Session", type="primary", use_container_width=True)

    with right_debug_col:
        st.markdown("### 📊 Live Performance Tracking")
        metric_knee = st.empty()
        metric_rom = st.empty()
        st.markdown("---")

        st.markdown("**Pipeline Engine Diagnostics**")
        console_placeholder = st.empty()

        st.markdown("**Last Evaluated Rep Record**")
        last_rep_placeholder = st.empty()

    # 4. RUNTIME OPTICAL FEED PROCESSING FRAME LOOP
    cap = cv2.VideoCapture(0)
    pose_tracker = mp_pose_mod.Pose()
    last_processed_rep_count = 0

    while cap.isOpened() and not stop_session:
        ret, frame = cap.read()
        if not ret:
            break

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose_tracker.process(rgb_image)

        # Update metrics up top
        acc_calc = (st.session_state.correct_reps / st.session_state.total_reps * 100.0) if st.session_state.total_reps > 0 else 0.0
        total_reps_metric.metric("Total Reps", f"{st.session_state.total_reps}")
        correct_reps_metric.metric("✅ Correct", f"{st.session_state.correct_reps}")
        incorrect_reps_metric.metric("❌ Incorrect", f"{st.session_state.incorrect_reps}")
        accuracy_metric.metric("Form Accuracy", f"{acc_calc:.1f}%")

        if results.pose_landmarks:
            mp_drawing_mod.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose_mod.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles_mod.get_default_pose_landmarks_style()
            )
            landmarks = results.pose_landmarks.landmark
            joints = extractor.extract_joints(landmarks)

            if joints is not None:
                hip_v, knee_v, ankle_v = joints[0], joints[1], joints[2]
                sh_coord = [landmarks[12].x, landmarks[12].y, landmarks[12].z] if landmarks[12].visibility > 0.3 else None
                ft_coord = [landmarks[30].x, landmarks[30].y, landmarks[30].z] if landmarks[30].visibility > 0.3 else None

                t_extract_start = time.perf_counter()
                features = extractor.process_frame(hip_v, knee_v, ankle_v, shoulder=sh_coord, foot=ft_coord)
                t_extract_end = time.perf_counter()
                st.session_state.last_latency["extract"] = (t_extract_end - t_extract_start) * 1000.0

                # Track live kinematic points in background memory arrays
                st.session_state.live_angle_history_buffer.append([
                    float(features.get('hip_angle', 170.0)),
                    float(features.get('knee_angle', features['angle'])),
                    float(features.get('ankle_angle', 110.0))
                ])

                # Live scalar metric updates
                metric_knee.metric("Live Knee Angle", f"{features['angle']:.1f}°")
                metric_rom.metric("Session Max ROM", f"{features['rom']:.1f}°")

                # REPETITION TRANSITION CHECKPOINT
                if features['rep_count'] > last_processed_rep_count:
                    rep_matrix = np.array(st.session_state.live_angle_history_buffer, dtype=np.float64)

                    t_rescale_start = time.perf_counter()
                    resampled_matrix = ml_engine.resample_sequence(rep_matrix, target_frames=100)
                    t_rescale_end = time.perf_counter()
                    st.session_state.last_latency["resample"] = (t_rescale_end - t_rescale_start) * 1000.0

                    BiomechanicalExtractor.extract_features(resampled_matrix)

                    t_infer_start = time.perf_counter()
                    ml_result = ml_engine.evaluate_live_sequence(rep_matrix, exercise_name)
                    t_infer_end = time.perf_counter()
                    st.session_state.last_latency["infer"] = (t_infer_end - t_infer_start) * 1000.0

                    predicted_form = str(ml_result.get("form_status", "CORRECT"))
                    confidence_score = float(ml_result.get("confidence", 0.0))

                    st.session_state.total_reps += 1
                    if predicted_form == "CORRECT":
                        st.session_state.correct_reps += 1
                    else:
                        st.session_state.incorrect_reps += 1

                    st.session_state.accumulated_confidences.append(confidence_score)
                    st.session_state.rom_values.append(features['rom'])
                    st.session_state.quality_scores.append(features['movement_quality'])
                    st.session_state.duration_values.append(features.get('rep_duration', 3.2))

                    total_pipeline_time_calc = (
                        st.session_state.last_latency["extract"]
                        + st.session_state.last_latency["resample"]
                        + st.session_state.last_latency["infer"]
                    )
                    st.session_state.last_latency["total"] = total_pipeline_time_calc

                    log_str = f"Rep #{st.session_state.total_reps} -> {predicted_form} ({confidence_score:.1f}%) | Inference: {total_pipeline_time_calc:.1f}ms"
                    st.session_state.console_logs.append(log_str)
                    if len(st.session_state.console_logs) > 4:
                        st.session_state.console_logs.pop(0)

                    last_rep_placeholder.info(
                        f"**Repetition #{st.session_state.total_reps}**: `{predicted_form}`\n"
                        f"- Confidence: `{confidence_score:.1f}%` | Max ROM: `{features['rom']:.1f}°`"
                    )

                    st.session_state.live_angle_history_buffer = []
                    last_processed_rep_count = features['rep_count']

        # Draw console diagnostics
        console_placeholder.code("\n".join(st.session_state.console_logs), language="text")

        # Draw Camera Stream
        frame_window.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB")
        time.sleep(0.005)

    cap.release()
    cv2.destroyAllWindows()

    # 5. CLOSURE LIFECYCLE ROUTINES — called exactly once when stop_session is True
    if stop_session:
        final_total_reps = int(st.session_state.total_reps)
        final_correct_reps = int(st.session_state.correct_reps)

        final_accuracy = (final_correct_reps / final_total_reps * 100.0) if final_total_reps > 0 else 0.0

        # Use 0.0 fallback (not 90.0) — no reps = no confidence data
        avg_confidence_metric = float(np.mean(st.session_state.accumulated_confidences)) if st.session_state.accumulated_confidences else 0.0

        # Calculate average ROM from real per-rep measurements
        avg_rom = float(np.mean(st.session_state.rom_values)) if st.session_state.rom_values else 0.0

        # Calculate average movement quality from real per-rep measurements
        avg_movement_quality = float(np.mean(st.session_state.quality_scores)) if st.session_state.quality_scores else 0.0

        # Calculate real session duration from tracked start time
        session_start_time = st.session_state.get("session_start_time", time.time())
        duration_seconds = int(time.time() - session_start_time)

        trend_text = "IMPROVING" if final_accuracy >= 80.0 else "PLATEAUED" if final_accuracy >= 50.0 else "REGRESSING"
        rec_text = (
            "Maintain your current pace metrics."
            if trend_text == "IMPROVING"
            else "Focus on maintaining steady speeds."
        )

        # Recovery score is computed authoritatively by the backend route
        # We pass accuracy and avg_confidence — backend does: (accuracy*0.7) + (avg_confidence*0.3)
        end_session_payload = {
            "session_id": str(session_id),
            "patient_id": str(patient_id),
            "exercise_name": str(exercise_name),
            "total_reps": final_total_reps,
            "correct_count": final_correct_reps,
            "accuracy": round(final_accuracy, 1),
            "avg_confidence": round(avg_confidence_metric, 1),
            "recovery_score": round(final_accuracy, 1),   # Backend will recompute from accuracy+confidence
            "recovery_deviation": 0.0,
            "trend": trend_text,
            "recommendation": rec_text,
            "duration_seconds": duration_seconds,
            "avg_rom": round(avg_rom, 1),
            "avg_movement_quality": round(avg_movement_quality, 1)
        }

        try:
            with st.spinner("Saving session to Firestore..."):
                response = requests.post(f"{API_URL}/sessions/end", json=end_session_payload, timeout=10.0)
                response.raise_for_status()
            st.success("✅ Session saved successfully!")
            time.sleep(0.5)

            # Clear transient live-session state before navigating away
            st.session_state.live_angle_history_buffer = []
            st.session_state.pop("current_active_session_tracking", None)
            st.session_state.pop("session_start_time", None)
            st.session_state.current_page = "📋 Session Summary"
            st.rerun()
        except Exception as api_err:
            st.error(f"🛑 Network Serialization Error: {api_err}")