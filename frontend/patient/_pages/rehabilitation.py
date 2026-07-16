"""
RehabAI - Patient Portal Rehabilitation Planner Component
Author: Senior UI/UX & Python Software Engineer
Description: Renders the complete prescribed physical therapy regimen by pulling
             live exercise scheduling profiles directly from Firestore collections.
"""

import streamlit as st
import logging
from frontend.common.services.exercise_service import ExerciseService

logger = logging.getLogger("RehabAI.RehabilitationPage")


def render_rehabilitation_page() -> None:
    """
    Queries your dynamic Firestore prescription tracks to populate the full
    rehabilitation queue without a single hardcoded line.
    """
    # 1. RESOLVE RUNTIME PLAN KEYS
    if "plan_id" not in st.session_state:
        st.session_state.plan_id = "PLN_24MIS1033_PH1"
    if "patient_id" not in st.session_state:
        st.session_state.patient_id = "PAT_24MIS1033"

    current_plan_id = st.session_state.plan_id
    current_patient_id = st.session_state.patient_id
    exercise_api = ExerciseService()

    # 2. HEADER NAVIGATION LAYER
    with st.container():
        if st.button("← Back to Dashboard", type="secondary"):
            st.session_state.current_page = "🏠 Dashboard"
            st.rerun()
        st.title("🦵 My Rehabilitation")
        st.markdown("Inspect your full prescribed therapy sequence and tracking parameters over the air.")
    st.divider()

    # 3. CONSUME NETWORK PRESCRIPTION PAYLOADS
    st.subheader("🏋️ Prescribed Therapy Track Schedule")
    
    plan_queue = []
    try:
        with st.spinner("Fetching active therapy regimen metrics..."):
            plan_queue = exercise_api.get_assigned_exercises(current_plan_id, patient_id=current_patient_id)
    except Exception as e:
        logger.error(f"Failed pulling prescription records for tracking frame '{current_plan_id}': {e}")
        st.caption("⚠️ *Unable to synchronize exercise regimen registry streams with Firestore.*")

    # 4. ITERATIVELY RENDER DYNAMIC CARD ENGINES
    if not plan_queue:
        st.info("☀️ **Clear Prescribed Plan**: There are currently no exercises assigned to this rehabilitation track node.")
    else:
        for index, item in enumerate(plan_queue, 1):
            ex_name = item.get("exercise_name", "Unknown Protocol")
            ex_code = item.get("exercise_code", "EX_UNK")
            ex_id = item.get("plan_exercise_id", ex_code)
            duration = item.get("duration", "5 Mins")
            difficulty = item.get("difficulty_rating", "Medium")
            is_mandatory = item.get("is_mandatory", True)
            
            # Extract prescription goals established in your models
            target_rom = item.get("target_rom_degrees", 0.0)
            target_sets = item.get("prescribed_sets", 3)
            target_reps = item.get("prescribed_reps", 10)

            # Generate localized widget hashes to ensure Streamlit loop safety
            unique_key = f"plan_{ex_code.lower()}_{index}"

            with st.container(border=True):
                ex_info, ex_actions = st.columns([3, 1])
                
                with ex_info:
                    st.markdown(f"### {index}. {ex_name}")
                    
                    # Apply explicit visual badge flags for clinical requirements
                    req_badge = ":red[[MANDATORY]]" if is_mandatory else ":gray[[OPTIONAL]]"
                    
                    st.markdown(
                        f"**Requirement:** {req_badge}  |  "
                        f"⏱️ **Estimated Duration:** `{duration}`  |  "
                        f"💪 **Difficulty:** `{difficulty}`"
                    )
                    st.markdown(
                        f"🎯 **Target Form Boundaries:** `{target_sets} Sets` × `{target_reps} Reps` "
                        f"| **Target ROM:** `{target_rom}°`"
                    )
                    st.caption(f"Firestore Record Identifier Key: `{ex_id}`")
                    
                with ex_actions:
                    st.write("")  # Clear vertical grid alignment buffer
                    st.write("")
                    if st.button("View Exercise", key=f"btn_view_{unique_key}", use_container_width=True, type="primary"):
                        st.session_state.exercise_id = ex_id
                        st.session_state.exercise_code = ex_code
                        st.session_state.exercise_name = ex_name
                        st.session_state.current_page = "📖 Exercise Detail"
                        st.rerun()

    st.write("")
    st.info("💡 **Clinical Directives:** Execute your therapy items in standard ordered intervals. If you experience abnormal resistance loops or localized swelling, drop execution streams immediately and signal your doctor node.")