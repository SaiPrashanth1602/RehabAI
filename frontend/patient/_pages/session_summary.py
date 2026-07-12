"""
RehabAI - Patient Portal Post-Session Evaluation Summary
Author: Senior UI/UX Engineer
Description: Renders interactive, analytical performance insights and recovery metric 
             milestones immediately following the completion of an active rehabilitation session.
"""

import streamlit as st
import logging
from frontend.common.services.session_service import SessionService

logger = logging.getLogger("RehabAI.SessionSummaryPage")


def render_session_summary_page() -> None:
    """
    Renders the post-exercise breakdown by polling session details and summary markers 
    calculated natively by the backend database execution layer.
    """
    session_id = st.session_state.get("session_id")
    exercise_name = st.session_state.get("exercise_name", "Prescribed Exercise")
    
    if not session_id:
        st.warning("🔍 **No recent session metrics found in the current state buffer.**")
        if st.button("Return to Dashboard", type="primary"):
            st.session_state.current_page = "🏠 Dashboard"
            st.rerun()
        return

    session_broker = SessionService()
    
    try:
        with st.spinner("Fetching performance calculations..."):
            session_data = session_broker.get_session(session_id)
    except Exception as e:
        logger.error(f"Failed pulling summary fields for token {session_id}: {e}")
        st.error("🚨 **Data Synchronization Error**: Unable to safely retrieve calculation summaries from the server.")
        return

    st.title("🏆 Workout Summary")
    st.markdown(f"Great job! You have successfully completed your prescribed tracking session for **{exercise_name}**.")
    st.caption(f"Archived Session Reference: `{session_id}`")
    st.divider()

    # ===========================================================================
    # 1. CORE PERFORMANCE BIOMARKER METRICS
    # ===========================================================================
    st.subheader("📊 Session Performance Scorecard")
    
    status_flag = session_data.get("status", "Completed")
    duration_seconds = session_data.get("duration_seconds", 0)
    
    total_reps = session_data.get("total_reps_completed", 0)
    correct_reps = session_data.get("correct_reps", 0)
    incorrect_reps = session_data.get("incorrect_reps", 0)
    accuracy_val = float(session_data.get("session_accuracy_percentage", 0.0))
    confidence_val = float(session_data.get("average_model_confidence", 0.0))
    
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric(
            label="⏱️ Total Workout Duration", 
            value=f"{duration_seconds // 60:02d}:{duration_seconds % 60:02d}",
            help="Total time elapsed with active webcam pipeline streaming frames."
        )
    with m2:
        st.metric(
            label="🏁 Lifecycle Status", 
            value=str(status_flag).upper()
        )
    with m3:
        st.metric(
            label="🏋️ Total Reps Detected", 
            value=f"{total_reps} reps"
        )

    st.write("")
    
    # Secondary breakdowns row
    r1, r2 = st.columns(2)
    with r1:
        st.metric(label="🟢 Correct Repetitions", value=f"{correct_reps} reps")
    with r2:
        st.metric(label="🔴 Incorrect Repetitions", value=f"{incorrect_reps} reps")

    st.write("")
    
    # ===========================================================================
    # 2. RANDOM FOREST ML CLASSIFICATION HUD
    # ===========================================================================
    st.subheader("🧠 Machine Learning Biomechanical Audit")
    
    with st.container(border=True):
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("#### 🦾 Form Accuracy Rating")
            st.progress(min(max(accuracy_val / 100.0, 0.0), 100.0))
            st.markdown(f"**Overall Accuracy:** `{accuracy_val:.1f}%` of movements matched proper execution trajectories.")
            
        with col_right:
            st.markdown("#### 🎯 Mean Classifier Confidence")
            st.progress(min(max(confidence_val / 100.0, 0.0), 100.0))
            st.markdown(f"**Random Forest Confidence:** `{confidence_val:.1f}%` structural template compatibility.")

    st.write("")

    # ===========================================================================
    # 3. CLINICAL DIRECTIVES & SYSTEM DISPATCH NAVIGATION
    # ===========================================================================
    st.markdown("### 🩺 Post-Exercise Assessment Advice")
    
    if accuracy_val >= 90:
        st.success("💡 **Clinical Indicator:** Excellent form control limits! Your kinetic smoothness values remain high. Maintain your current pace metrics.")
    elif accuracy_val >= 75:
        st.success("💡 **Clinical Indicator:** Good movement quality overall. Maintain spatial alignment consistency in future repetitions.")
    elif accuracy_val >= 60:
        st.warning("💡 **Clinical Indicator:** Minor compensations detected by the ML classifier. Focus on stabilizing your posture through the core ranges.")
    else:
        st.error("🚨 **Clinical Indicator:** Significant movement deviations detected. Ensure your device tracking camera stands completely unclouded, perpendicular, and review standard exercise guidance specs.")

    st.write("")
    st.divider()

    # System Navigation Buttons Group
    left_btn, right_btn = st.columns(2)
    with left_btn:
        if st.button("🔄 Start New Exercise Run", use_container_width=True, type="secondary"):
            if "rep_frame_buffer" in st.session_state:
                st.session_state.rep_frame_buffer = []
            st.session_state.current_page = "📋 My Rehabilitation"
            st.rerun()
            
    with right_btn:
        if st.button("🏠 Return to Main Dashboard", use_container_width=True, type="primary"):
            if "rep_frame_buffer" in st.session_state:
                st.session_state.rep_frame_buffer = []
            st.session_state.pop("session_id", None)
            st.session_state.current_page = "🏠 Dashboard"
            st.rerun()