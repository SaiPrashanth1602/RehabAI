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

# ===========================================================================
# 🛡️ BULLETPROOF WINDOWS VIRTUAL ENVIRONMENT PATH RESOLUTION
# ===========================================================================
try:
    current_file_path = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(current_file_path, "..", "..", ".."))
    candidate_paths = [
        os.path.join(root_dir, ".venv311", "Lib", "site-packages"),
        os.path.join(root_dir, ".venv", "Lib", "site-packages"),
    ]
    for path in candidate_paths:
        if os.path.exists(path) and path not in sys.path:
            sys.path.insert(0, path)
except Exception:
    pass

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
    raw_session_state = st.session_state.get("session_id")
    session_id = None

    if isinstance(raw_session_state, dict):
        session_id = raw_session_state.get("session_id") or raw_session_state.get("id")
    elif isinstance(raw_session_state, str):
        session_id = raw_session_state

    patient_id = st.session_state.get("patient_id", "PAT_24MIS1033")
    exercise_name = st.session_state.get("exercise_name", "Sit-to-Stand")
    exercise_code = st.session_state.get("exercise_code", "m05")
    exercise_key = exercise_name.lower().strip()

    if not session_id:
        st.error("🚨 **Session Context Token Disconnected**: Please select an item inside your active Treatment Queue to initialize tracking.")
        if st.button("Return to Regimen"):
            st.session_state.current_page = "📋 My Rehabilitation"
            st.rerun()
        return

    st.caption(f"Session Token: `{session_id}` | Patient ID: `{patient_id}` | Regimen: `{exercise_name}`")

    # 2. ALLOCATE CORE MEMORY BUFFERS AND HISTORY LISTS
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

    if "ml_inference_engine" not in st.session_state:
        st.session_state.ml_inference_engine = RehabInferenceEngine()
        
    extractor = st.session_state.rehab_extractor
    ml_engine = st.session_state.ml_inference_engine

    try:
        requests.post(f"{API_URL}/sessions/camera/start", json={"session_id": str(session_id)})
    except Exception:
        pass

    # =======================================================================
    # ⚡ LIGHTWEIGHT CORE HUD (No expanding heavy matrices/telemetry nodes)
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
        
        # Super simple code snippet for system tracking output instead of heavy nested widgets
        st.markdown("**Pipeline Engine Diagnostics**")
        console_placeholder = st.empty()
        
        st.markdown("**Last Evaluated Rep Record**")
        last_rep_placeholder = st.empty()

    feature_names_lookup = [
        "mean_hip", "mean_knee", "mean_ankle", "std_hip", "std_knee", "std_ankle",
        "min_hip", "min_knee", "min_ankle", "max_hip", "max_knee", "max_ankle",
        "range_hip", "range_knee", "range_ankle", "velocity_hip", "velocity_knee", "velocity_ankle",
        "acceleration_hip", "acceleration_knee", "acceleration_ankle"
    ]

    model_payload = ml_engine.models.get(exercise_key)

    # 4. RUNTIME OPTICAL FEED PROCESSING FRAME LOOP (CRIPPLED RE-RENDERING FAT)
    cap = cv2.VideoCapture(0)
    pose_tracker = mp_pose_mod.Pose()
    last_processed_rep_count = 0

    while cap.isOpened() and not stop_session:
        ret, frame = cap.read()
        if not ret: break

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose_tracker.process(rgb_image)
        
        # Update metrics up top with zero layout layout dependencies
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

                # Track live kinematic points purely in background memory arrays
                st.session_state.live_angle_history_buffer.append([
                    float(features.get('hip_angle', 170.0)),
                    float(features.get('knee_angle', features['angle'])),
                    float(features.get('ankle_angle', 110.0))
                ])

                # Light scalar values text updates (Instant UI draw time)
                metric_knee.metric("Live Knee Angle", f"{features['angle']:.1f}°")
                metric_rom.metric("Session Max ROM", f"{features['rom']:.1f}°")

                # REPETITION TRANSITION CHECKPOINT
                if features['rep_count'] > last_processed_rep_count:
                    rep_matrix = np.array(st.session_state.live_angle_history_buffer, dtype=np.float64)
                    
                    t_rescale_start = time.perf_counter()
                    resampled_matrix = ml_engine.resample_sequence(rep_matrix, target_frames=100)
                    t_rescale_end = time.perf_counter()
                    st.session_state.last_latency["resample"] = (t_rescale_end - t_rescale_start) * 1000.0
                    
                    extracted_vector_row = BiomechanicalExtractor.extract_features(resampled_matrix)
                    
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

                    total_pipeline_time_calc = st.session_state.last_latency["extract"] + st.session_state.last_latency["resample"] + st.session_state.last_latency["infer"]
                    st.session_state.last_latency["total"] = total_pipeline_time_calc

                    # Track lightweight console lines
                    log_str = f"Rep #{st.session_state.total_reps} -> {predicted_form} ({confidence_score:.1f}%) | Inference: {total_pipeline_time_calc:.1f}ms"
                    st.session_state.console_logs.append(log_str)
                    if len(st.session_state.console_logs) > 4:
                        st.session_state.console_logs.pop(0)

                    # Update last repetition snippet placeholder
                    last_rep_placeholder.info(
                        f"**Repetition #{st.session_state.total_reps}**: `{predicted_form}`\n"
                        f"- Confidence: `{confidence_score:.1f}%` | Max ROM: `{features['rom']:.1f}°`"
                    )

                    st.session_state.live_angle_history_buffer = []
                    last_processed_rep_count = features['rep_count']

        # 12. DRAW SIMPLIFIED TELEMETRY STRING CONSOLES ONLY
        console_placeholder.code("\n".join(st.session_state.console_logs), language="text")

        # Draw Camera Stream
        frame_window.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB")
        time.sleep(0.005) # Dropped delay floor to crank up pipeline processing overhead room

    cap.release()
    cv2.destroyAllWindows()

    # 5. CLOSURE LIFECYCLE ROUTINES
    # =======================================================================
    # 5. CLOSURE LIFECYCLE ROUTINES
    # =======================================================================
    if stop_session:
        final_total_reps = int(st.session_state.total_reps)
        final_correct_reps = int(st.session_state.correct_reps)
        
        # Calculate locally using session state to prevent UnboundLocalError
        final_accuracy = (final_correct_reps / final_total_reps * 100.0) if final_total_reps > 0 else 0.0
        avg_confidence_metric = float(np.mean(st.session_state.accumulated_confidences)) if st.session_state.accumulated_confidences else 90.0

        trend_text = "IMPROVING" if final_accuracy >= 80.0 else "PLATEAUED" if final_accuracy >= 50.0 else "REGRESSING"
        rec_text = "Maintain your current pace metrics." if trend_text == "IMPROVING" else "Focus on maintaining steady speeds."

        end_session_payload = {
            "session_id": str(session_id),
            "patient_id": str(patient_id),
            "exercise_name": str(exercise_name),
            "total_reps": final_total_reps,
            "correct_count": final_correct_reps,
            "accuracy": round(final_accuracy, 1),
            "avg_confidence": round(avg_confidence_metric, 1),
            "recovery_score": round(final_accuracy, 1),
            "recovery_deviation": 0.0,
            "trend": trend_text,
            "recommendation": rec_text
        }

        try:
            with st.spinner("Uploading logs..."):
                response = requests.post(f"{API_URL}/sessions/end", json=end_session_payload)
                response.raise_for_status()
            st.success("Session saved successfully!")
            time.sleep(0.5)
            
            # Clear layout states variables memory spaces before leaving workspace
            st.session_state.live_angle_history_buffer = []
            st.session_state.current_page = "📋 Session Summary"
            st.rerun()
        except Exception as api_err:
            st.error(f"🛑 Network Serialization Error: {api_err}")

        try:
            with st.spinner("Uploading logs..."):
                response = requests.post(f"{API_URL}/sessions/end", json=end_session_payload)
                response.raise_for_status()
            st.success("Session saved!")
            time.sleep(0.5)
            
            st.session_state.live_angle_history_buffer = []
            st.session_state.current_page = "📋 Session Summary"
            st.rerun()
        except Exception as api_err:
            st.error(f"🛑 Error: {api_err}")