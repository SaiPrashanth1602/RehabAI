"""
RehabAI - Patient Portal Exercise Detail Component
Author: Senior Full Stack Engineer
Description: Renders clinical instructions, target biomechanical metrics, common errors, 
             and device camera alignment specifications by pulling asset files dynamically 
             from the global Firestore exercise library collection.
"""

import streamlit as st
import logging
from frontend.common.services.exercise_service import ExerciseService
from frontend.common.services.session_service import SessionService

logger = logging.getLogger("RehabAI.ExerciseDetailPage")


def render_exercise_detail_page() -> None:
    """
    Renders the clinical instruction workspace framework by combining specific 
    prescription targets with master library assets over the air.
    """
    # 1. CONTEXT RAILS RESOLUTION
    patient_id = st.session_state.get("patient_id", "PAT_24MIS1033")
    plan_id = st.session_state.get("plan_id", "PLN_24MIS1033_PH1")
    exercise_id = st.session_state.get("exercise_id")
    exercise_code = st.session_state.get("exercise_code")
    exercise_name = st.session_state.get("exercise_name")

    # Early exit boundary check if page context sequence drops references
    if not exercise_code or not exercise_name:
        st.warning("🔍 **Exercise context reference unlinked.**")
        if st.button("⬅ Return to Plan", type="primary"):
            st.session_state.current_page = "静 My Rehabilitation"
            st.rerun()
        return

    exercise_api = ExerciseService()

    # 2. RUNTIME DATABASE INGESTION
    library_data = {}
    plan_exercise_data = {}
    
    try:
        with st.spinner("Synchronizing movement specifications from Firestore..."):
            # Fetch global template specs (muscles, description, media URLs)
            library_data = exercise_api.get_exercise_details(exercise_code)
            
            # Fetch user-specific plan targets (sets, reps, custom clinical notes)
            assigned_queue = exercise_api.get_assigned_exercises(plan_id)
            for item in assigned_queue:
                if item.get("exercise_code") == exercise_code:
                    plan_exercise_data = item
                    break
    except Exception as e:
        logger.error(f"Failed pulling asset schemas targeting '{exercise_code}' over transport: {e}")
        st.error("🚨 **Network Connection Error**: Dropped data link layer sync loops with master repository files.")

    # Parse structural properties natively from the database models
    description = library_data.get("description", "Prescribed rehabilitation movement matrix.")
    target_muscles = library_data.get("target_muscles", ["Quadriceps", "Hamstrings"])
    animation_url = library_data.get("animation_url", "")
    
    # Merge prescription specifications with baseline models
    prescribed_sets = plan_exercise_data.get("prescribed_sets", library_data.get("default_target_sets", 3))
    prescribed_reps = plan_exercise_data.get("prescribed_reps", library_data.get("default_target_reps", 10))
    target_rom = plan_exercise_data.get("target_rom_degrees", library_data.get("default_target_rom", 90.0))
    hold_sec = plan_exercise_data.get("hold_duration_seconds", library_data.get("default_target_hold", 5))
    clinical_notes = plan_exercise_data.get("clinical_notes", "Maintain safe, slow alignment tracking extensions.")

    # 3. INTERFACE RENDERING ENGINE
    if st.button("⬅ Back to Plan", type="secondary"):
        st.session_state.current_page = "静 My Rehabilitation"
        st.rerun()

    st.title(f"📖 {exercise_name}")
    st.caption(f"Global Reference Signature: `{exercise_code}` | Prescription Key: `{exercise_id}`")
    st.write("")

    # Split workspace layout: Left for documentation descriptions, Right for media assets
    col_text, col_media = st.columns([5, 4])

    with col_text:
        st.markdown("### 📋 Clinical Description")
        st.write(description)
        
        st.markdown("### ✨ Targeted Muscle Complexes")
        st.write(", ".join(target_muscles))

        st.markdown("### 🎯 Prescribed Session Target Boundaries")
        with st.container(border=True):
            t1, t2, t3 = st.columns(3)
            with t1:
                st.metric(label="Prescribed Volume", value=f"{prescribed_sets} Sets")
            with t2:
                st.metric(label="Target Reps", value=f"{prescribed_reps} / Set")
            with t3:
                st.metric(label="Target ROM", value=f"{target_rom}°")

    with col_media:
        st.markdown("### 🖼️ Kinematic Reference Guidance Loop")
        with st.container(border=True):
            if animation_url:
                # Displays the dynamic GIF or reference illustration coming straight out of Firestore URL references
                st.image(animation_url, caption=f"Correct baseline cadence tracking template for {exercise_name}.")
            else:
                st.write("")
                st.info("🔍 Media streaming hook standby. Check cloud storage asset deployment pipelines.")
                st.write("")

    st.divider()

    # Clinical Directives and Tracking Alignment Sections
    st.markdown("### 🩺 Attending Specialist Directives")
    st.info(f"\" {clinical_notes} \"")

    st.write("")
    with st.container(border=True):
        st.markdown("### 🎥 Edge Computer Vision Device Configuration")
        st.markdown(
            f"To guarantee precise evaluation limits from your **Random Forest classification models**, place your device camera "
            f"completely perpendicular to your injured side at a distance of approximately 5 feet. Verify that the system tracking lenses "
            f"have a completely unobstructed view of these tracked key-vectors: `{', '.join(library_data.get('biomechanical_features', ['Joint Coordinates']))}`."
        )

    st.divider()

    # 4. TRANSACTIONS POOL SYSTEM TRIGGER (INITIALIZE SESSIONS)
    left_pad, center_node, right_pad = st.columns([1, 2, 1])
    with center_node:
        if st.button("▶ Initialize Active Run Session", use_container_width=True, type="primary"):
            try:
                session_broker = SessionService()
                with st.spinner("Spawning running transactional session block on Firestore..."):
                    # Complete full field mappings required by backend SessionCreate schema model
                    session_record = session_broker.start_session(
                        patient_id=patient_id,
                        plan_id=plan_id,
                        plan_exercise_id=exercise_id or f"PEX_{plan_id}_{exercise_code}",
                        exercise_code=exercise_code,
                        exercise_name=exercise_name
                    )
                
                if session_record and "session_id" in session_record:
                    st.session_state.session_id = session_record["session_id"]
                    st.success("✅ **Active Tracking Run Allocated Successfully**")
                    st.session_state.current_page = "🎥 Live Session"
                    st.rerun()
                    
            except Exception as transaction_fault:
                logger.critical(f"Failed to securely spin up session on database pipeline: {transaction_fault}")
                st.error("🚨 **Clinical Service Failure**: Unable to open an evaluation tracking context block inside Firestore collections.")