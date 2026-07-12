"""
RehabAI - Patient Portal Central Dashboard Component
Author: Sai Prashanth Ramesh & Core Systems Architecture
Description: Renders the central patient overview board. Dynamically fetches profiles, 
             historical aggregates, and initializes active tracking queues straight from Firestore.
"""

import streamlit as st
import logging
import requests
from frontend.common.services.patient_service import PatientService
from frontend.common.services.exercise_service import ExerciseService

logger = logging.getLogger("RehabAI.PatientDashboardPage")


def render_patient_dashboard() -> None:
    """
    Executes the runtime validation lookups and mounts interface grids 
    driven entirely by remote database documents.
    """
    # 1. RESOLVE ACTIVE CONTEXT NODES
    if "patient_id" not in st.session_state:
        st.session_state.patient_id = "PAT_24MIS1033"
    if "plan_id" not in st.session_state:
        st.session_state.plan_id = "PLN_24MIS1033_PH1"
        
    current_patient_id = st.session_state.patient_id
    current_plan_id = st.session_state.plan_id

    # Instantiate transport endpoints managers
    patient_api = PatientService()
    exercise_api = ExerciseService()

    # 2. CONSUME NETWORK DATA PAYLOADS
    try:
        with st.spinner("Synchronizing clinical operational parameters..."):
            patient_profile = patient_api.get_patient(current_patient_id)
            # Fetch assignments directly out of Firestore plan_exercises
            assigned_queue = exercise_api.get_assigned_exercises(current_plan_id)
    except Exception as e:
        logger.error(f"Failed pulling remote configuration sets for dashboard: {e}")
        st.error("🚨 **Database Synchronization Failure**: Unable to update data layers with the Clinical Core server.")
        return

    if not patient_profile:
        st.warning("🔍 **Profile Untracked**: Failed to identify valid record profiles on the cloud node.")
        return

    # Extract database items cleanly
    first_name = patient_profile.get("first_name", "Patient")
    phase = patient_profile.get("current_phase", "Phase I")
    recovery_day = patient_profile.get("recovery_day", 1)
    doctor = patient_profile.get("doctor_name", "Attending Specialist")

    # 3. INTERFACE HEADER & STATS RENDER GRID
    with st.container():
        h_left, h_right = st.columns([2, 1])
        with h_left:
            st.title("🏠 Dashboard")
            st.markdown(f"### 👋 Welcome back, {first_name}")
            st.caption("Real-time telemetry overview of your clinical pathway constraints.")
        with h_right:
            with st.container(border=True):
                st.markdown(f"**🏥 Assigned Clinician**\n`{doctor}`")

    st.write("")
    st.subheader("📊 Dynamic Recovery Stats")
    
    # These fields now pull safely from separate database updates, falling back to 0.0 before analytics seed
    with st.container():
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            with st.container(border=True):
                st.metric(label="📈 Recovery Score", value=f"{patient_profile.get('recovery_score', 0.0)} / 100")
        with m2:
            with st.container(border=True):
                st.metric(label="🏁 Pathway Focus", value=phase)
        with m3:
            with st.container(border=True):
                st.metric(label="⏳ Post-Op Day", value=f"Day {recovery_day}")
        with m4:
            with st.container(border=True):
                st.metric(label="📐 Flexion ROM", value=f"{patient_profile.get('current_rom', 0.0)}°")

    st.write("")
    st.divider()

    # 4. SPLIT APPLICATION WORKSPACE
    left_workspace, right_workspace = st.columns([4, 3])

    # ===========================================================================
    # LEFT PANEL: DYNAMIC REHABILITATION EXERCISES FROM FIRESTORE
    # ===========================================================================
    with left_workspace:
        st.subheader("🏋️ Today's Therapy Regimen")
        
        if not assigned_queue:
            st.info("☀️ **Clear Therapy Queue**: No active tracking tasks are currently assigned to this plan.")
        else:
            for item in assigned_queue:
                ex_name = item.get("exercise_name", "Unknown Protocol")
                ex_code = item.get("exercise_code", "EX_UNK")
                ex_id = item.get("plan_exercise_id", ex_code)
                duration = item.get("duration", "5 Mins")
                difficulty = item.get("difficulty_rating", "Medium")
                
                # Streamlit UI isolated key hashing token to safely support parallel loop rendering
                widget_hash = f"dash_{ex_code.lower()}"

                with st.container(border=True):
                    ex_info, ex_actions = st.columns([3, 2])
                    with ex_info:
                        st.markdown(f"#### {ex_name}")
                        st.markdown(f"⏱️ **Duration:** `{duration}` | **Difficulty:** *{difficulty}*")
                        st.caption(f"Prescription Ref Trace: `{ex_id}`")
                    with ex_actions:
                        st.write("")  # Dynamic visual padding offsets
                        a1, a2 = st.columns(2)
                        with a1:
                            if st.button("Details", key=f"det_{widget_hash}", use_container_width=True):
                                st.session_state.exercise_id = ex_id
                                st.session_state.exercise_code = ex_code
                                st.session_state.exercise_name = ex_name
                                st.session_state.current_page = "📖 Exercise Detail"
                                st.rerun()
                        with a2:
                            if st.button("Start →", key=f"str_{widget_hash}", use_container_width=True, type="primary"):
                                # Assemble the formal clinical payload schema matching backend constraints
                                session_payload = {
                                    "plan_exercise_id": ex_id,
                                    "exercise_code": ex_code,
                                    "exercise_name": ex_name
                                }
                                
                                try:
                                    # Synchronously alert backend core cluster to allocate document registers
                                    backend_start_url = "http://127.0.0.1:8000/api/v1/sessions/start"
                                    response = requests.post(backend_start_url, json=session_payload, timeout=5.0)
                                    
                                    if response.status_code == 201:
                                        session_data = response.json()
                                        
                                        # Bind dynamic parameter contexts straight to core application scopes
                                        st.session_state["active_session_id"] = session_data["session_id"]
                                        st.session_state["current_exercise_name"] = ex_name
                                        st.session_state["current_exercise_code"] = ex_code
                                        
                                        # Clear view pane tracking thresholds matching patient.py exactly
                                        st.session_state.current_page = "🎥 Live Session"
                                        st.rerun()
                                    else:
                                        st.error(f"Clinical Service Failure: Server responded with status {response.status_code}")
                                except Exception as startup_err:
                                    logger.error(f"Exception triggered allocating session memory maps: {startup_err}")
                                    st.error("🚨 **Network Initialization Bottleneck**: Failed to spin up live assessment portal context.")

    # ===========================================================================
    # RIGHT PANEL: QUICK NAVIGATION LINK NODES
    # ===========================================================================
    with right_workspace:
        st.subheader("⚡ Quick Navigation Control")
        with st.container(border=True):
            st.markdown("Instantly adjust application context trees or monitor compliance tracking logs.")
            st.write("")
            
            if st.button("🦵 My Rehabilitation", use_container_width=True, type="primary"):
                st.session_state.current_page = "静 My Rehabilitation"
                st.rerun()
                
            if st.button("📈 View Progress Trends", use_container_width=True):
                st.session_state.current_page = "📊 Progress"
                st.rerun()
                
            if st.button("👤 Open Patient Profile", use_container_width=True):
                st.session_state.current_page = "👤 Profile"
                st.rerun()