"""
RehabAI - Patient Portal Central Application Master Router
Author: Senior Full Stack Architect
Description: Coordinates global UI state frameworks, runs runtime session data lookups,
             and mounts view page scripts dynamically to build a stable multi-page application.
"""

import sys
import os

# --- PATH RESOLUTION BLOCK STAMP ---
# Finds the absolute path of the directory 2 levels up from this file (Project Root)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# -----------------------------------

import streamlit as st
import logging

# Import Core Transport Client Services
from frontend.common.services.patient_service import PatientService
from frontend.common.services.session_service import SessionService
from frontend.common.services.exercise_service import ExerciseService

# Import Modular Navigation Views
from frontend.common.components.patient_sidebar import render_patient_sidebar
from frontend.patient._pages.dashboard import render_patient_dashboard
from frontend.patient._pages.rehabilitation import render_rehabilitation_page
from frontend.patient._pages.exercise_detail import render_exercise_detail_page
from frontend.patient._pages.live_session import render_live_session
# FIXED: Updated function reference to explicitly match 'render_session_summary_page' implementation
from frontend.patient._pages.session_summary import render_session_summary_page
from frontend.patient._pages.progress import render_progress_page
from frontend.patient._pages.profile import render_profile_page

# Configure Application Subsystem Logger Layer
logger = logging.getLogger("RehabAI.PatientPortalMaster")

# Enforce broad layout presentation constraints across client viewplanes
st.set_page_config(
    page_title="RehabAI Patient Workspace",
    page_icon="🦵",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_global_session_contexts() -> None:
    """
    Sets up strict baseline structural keys within memory caches 
    to manage navigation states across dynamic component swaps.
    """
    # Change "ACL001" to the seeded production ID
    if "patient_id" not in st.session_state:
        st.session_state.patient_id = "PAT_24MIS1033"

    # Change "PLN-24MIS1033-PH1" to use underscores matching seed.py
    if "plan_id" not in st.session_state:
        st.session_state.plan_id = "PLN_24MIS1033_PH1"

    # Navigation master layout tracking boundary fallback
    if "current_page" not in st.session_state:
        st.session_state.current_page = "🏠 Dashboard"

    # Focused movement parameter trackers
    if "exercise_id" not in st.session_state:
        st.session_state.exercise_id = None
    if "exercise_name" not in st.session_state:
        st.session_state.exercise_name = None
        
    # Transaction tracking context keys
    if "session_id" not in st.session_state:
        st.session_state.session_id = None


def run_master_application_pipeline() -> None:
    """
    Pars active state tokens to dispatch structural render steps dynamically.
    Defines safe fallbacks to absorb layout exceptions.
    """
    # Step 1: Initialize global session framework matrices
    initialize_global_session_contexts()

    # Step 2: Render sidebar module and capture selected path updates
    selected_page_target = render_patient_sidebar()

    # Step 3: Dispatch components dynamically matching the master routing tree
    # Explicit mapping strings enforce complete synchronization with navbar actions
    current_view = st.session_state.current_page

    try:
        if current_view == "🏠 Dashboard":
            render_patient_dashboard()
            
        elif current_view == "静 My Rehabilitation":
            render_rehabilitation_page()
            
        elif current_view == "📖 Exercise Detail":
            render_exercise_detail_page()
            
        elif current_view == "🎥 Live Session":
            render_live_session()
            
        elif current_view == "📋 Session Summary":
            # FIXED: Routed cleanly to match your summary file architecture method
            render_session_summary_page()
            
        elif current_view == "📊 Progress":
            render_progress_page()
            
        elif current_view == "👤 Profile":
            render_profile_page()
            
        else:
            logger.error(f"Intercepted unmapped application routing vector state: {current_view}")
            st.error(f"💥 **Routing Engine Failure**: The view plane state '{current_view}' could not be resolved.")
            if st.button("🔄 Reset to Main Dashboard", type="primary"):
                st.session_state.current_page = "🏠 Dashboard"
                st.rerun()

    except Exception as route_fault:
        logger.critical(f"Fatal operational loop breakdown rendering layout frame inside '{current_view}': {route_fault}")
        st.error("💥 **Architectural Intercept Error**: An unhandled pipeline exception occurred during page mounting.")
        st.caption(f"Trace Metric Details: `{str(route_fault)}`")


if __name__ == "__main__":
    run_master_application_pipeline()