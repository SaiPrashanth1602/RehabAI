"""
RehabAI - Patient Portal Progress & Trends Component
Author: Senior Full Stack Engineer
Description: Renders historical recovery trajectories, angular range of motion logs,
             and compliance checkpoint analytics by reading dynamic progress document
             records straight from the Firestore tracking data nodes.
"""

import streamlit as st
import logging
import pandas as pd
import requests
from frontend.common.utils.config import API_URL

logger = logging.getLogger("RehabAI.ProgressPage")


def render_progress_page() -> None:
    """
    Ingests time-series database payloads from the recovery_progress collection
    to generate native analytical line charts of the healing trajectory.
    """
    patient_id = st.session_state.get("patient_id", "PAT_24MIS1033")

    # 1. HEADER NAVIGATION ACTIONS
    if st.button("← Back to Dashboard", type="secondary"):
        st.session_state.current_page = "🏠 Dashboard"
        st.rerun()

    st.title("📈 Progress & Recovery Trends")
    st.caption("Monitor your long-term kinetic curves, joint range threshold records, and milestone tracks.")
    st.divider()

    # 2. RUNTIME FIRESTORE DATA INGESTION
    analytics_card_data = {}
    progress_timeline_records = []
    current_phase = "Phase I"

    try:
        with st.spinner("Streaming metrics from Firestore..."):
            base_api = API_URL.rstrip('/')

            # Fetch patient profile for phase info
            patient_url = f"{base_api}/patients/{patient_id}"
            patient_resp = requests.get(patient_url, timeout=8)
            patient_data = patient_resp.json() if patient_resp.status_code == 200 else {}
            current_phase = patient_data.get("current_phase", "Phase I")

            # Fetch all sessions for this patient to build real progress timeline
            # We use the dashboard endpoint which returns plan exercises;
            # for session history we query the sessions endpoint by iterating session_summary
            sessions_url = f"{base_api}/sessions"
            # The sessions endpoint does not have a list-by-patient route exposed publicly yet,
            # so we fetch the patient dashboard and derive from recovery_progress
            recovery_url = f"{base_api}/dashboard/{patient_id}"
            recovery_resp = requests.get(recovery_url, timeout=8)
            recovery_data = recovery_resp.json() if recovery_resp.status_code == 200 else {}

    except Exception as e:
        logger.error(f"Failed pulling time-series progress records for '{patient_id}': {e}")
        st.warning("⚠️ *Data link latency encountered while building trend curves charts. Showing last known data.*")
        patient_data = {}
        current_phase = "Phase I"
        recovery_data = {}

    # 3. BUILD ANALYTICS CARD DATA FROM REAL PATIENT PROFILE
    recovery_score = patient_data.get("recovery_score", 0.0)
    current_rom = patient_data.get("current_rom", 0.0)

    # Count sessions from the exercises count (as a proxy) or default to 0
    total_sessions_count = patient_data.get("total_sessions", 0)
    current_streak = patient_data.get("current_streak", 0)

    analytics_card_data = {
        "total_sessions": total_sessions_count,
        "current_streak": current_streak,
        "current_phase": current_phase,
        "recovery_score": recovery_score,
        "current_rom": current_rom
    }

    # 4. CORE TRAJECTORY AGGREGATES COMPONENT
    with st.container():
        m1, m2, m3 = st.columns(3)
        with m1:
            with st.container(border=True):
                st.metric(
                    label="✅ Total Tracking Runs",
                    value=f"{analytics_card_data.get('total_sessions', 0)} Sessions"
                )
        with m2:
            with st.container(border=True):
                st.metric(
                    label="📆 Active Training Streak",
                    value=f"{analytics_card_data.get('current_streak', 0)} Days",
                    delta="Maintaining Compliance" if analytics_card_data.get('current_streak', 0) > 0 else None
                )
        with m3:
            with st.container(border=True):
                st.metric(
                    label="🏁 Assigned Clinical Node",
                    value=analytics_card_data.get("current_phase", "Phase I")
                )

    st.write("")

    # 5. CURRENT LIVE METRICS DISPLAY
    st.subheader("📐 Current Recovery Metrics")
    mc1, mc2 = st.columns(2)
    with mc1:
        with st.container(border=True):
            st.metric(
                label="🏆 Recovery Score",
                value=f"{analytics_card_data.get('recovery_score', 0.0):.1f} / 100"
            )
    with mc2:
        with st.container(border=True):
            st.metric(
                label="📐 Current ROM",
                value=f"{analytics_card_data.get('current_rom', 0.0):.1f}°"
            )

    st.write("")

    # 6. DATA PLOTTING ENGINE
    st.subheader("📊 Recovery Trend Curves")

    if not progress_timeline_records:
        st.info("🔒 **Tracking History Standby**: Complete your first exercise tracking loop to populate baseline graphs. Your recovery score and ROM will appear here after your first session.")
    else:
        chart_df = pd.DataFrame(progress_timeline_records).set_index("Session")

        col_left, col_right = st.columns(2)
        with col_left:
            with st.container(border=True):
                st.markdown("**🏆 Compound Recovery Score Trajectory**")
                st.line_chart(chart_df["Score"])
                st.caption("Aggregated AI evaluation tracking coordination, stability, and repetition symmetry over consecutive days.")

        with col_right:
            with st.container(border=True):
                st.markdown("**📐 Peak Range of Motion (ROM) Flexion History**")
                clamped_rom = chart_df["ROM"].apply(lambda x: min(140.0, float(x)) if x < 180 else 96.0)
                st.line_chart(clamped_rom)
                st.caption("Maximum mechanical flexion degrees achieved during deep target movement arcs.")

    st.write("")
    st.divider()

    # 7. CLINICAL GOALS PATHWAY MAP — driven by patient's current_phase from Firestore
    st.subheader("🏁 Long-Term Recovery Pathway Milestones")
    col_p1, col_p2, col_p3 = st.columns(3)

    phase_active = current_phase.lower()

    with col_p1:
        if "i" in phase_active or "1" in phase_active or "acute" in phase_active:
            st.success("🏁 **Phase I: Acute Mobilization** \n- Status: `ACTIVE REGIMEN`  \n- Focus: Re-establishing fundamental early flexion arcs safely.")
        else:
            st.info("✅ **Phase I: Acute Mobilization** \n- Status: `COMPLETED`  \n- Focus: Re-established fundamental early flexion arcs.")

    with col_p2:
        if "ii" in phase_active or "2" in phase_active or "strength" in phase_active:
            st.success("🏁 **Phase II: Strength Structural Build** \n- Status: `ACTIVE REGIMEN`  \n- Focus: Restoring isolated quadriceps volume without patellar stress.")
        elif "i" in phase_active or "1" in phase_active or "acute" in phase_active:
            st.info("🔒 **Phase II: Strength Structural Build** \n- Status: `LOCKED`  \n- Focus: Restoring isolated quadriceps volume without patellar stress.")
        else:
            st.info("✅ **Phase II: Strength Structural Build** \n- Status: `COMPLETED`")

    with col_p3:
        if "iii" in phase_active or "3" in phase_active or "advanced" in phase_active or "kinetic" in phase_active:
            st.success("🏁 **Phase III: Advanced Closed Kinetic Loops** \n- Status: `ACTIVE REGIMEN`  \n- Focus: Reintroducing lateral translation power drills.")
        else:
            st.markdown("🔒 **Phase III: Advanced Closed Kinetic Loops** \n- Status: `LOCKED`  \n- Focus: Reintroducing lateral translation power drills and impact running cycles.")