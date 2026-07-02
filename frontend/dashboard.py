# frontend/dashboard.py
import os
import sys

# 1. Compute explicit absolute paths to avoid system import mismatches
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

# 2. Inject paths safely into system environment pool
for path in [PROJECT_ROOT, CURRENT_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

import streamlit as st

# 3. Dynamic imports resolved cleanly by workspace path injectors
from _pages.dashboard_page import render_dashboard_page
from _pages.patients_page import render_patients_page
from _pages.analytics_page import render_analytics_page
from _pages.recommendations_page import render_recommendations_page
from _pages.patient_profile import render_patient_profile_page
from _pages.settings import render_settings_page
from components.sidebar import render_sidebar


def main():
    st.set_page_config(
        page_title="RehabAI | Clinical Workspace",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Core Navigation State Initialization Rules
    if "current_page" not in st.session_state:
        st.session_state.current_page = "🏠 Dashboard"
    if "selected_patient_id" not in st.session_state:
        st.session_state.selected_patient_id = None

    sidebar_routing = render_sidebar()

    # Route state interception filters
    if sidebar_routing and sidebar_routing != st.session_state.current_page:
        st.session_state.current_page = sidebar_routing
        st.session_state.selected_patient_id = None
        st.rerun()

    # Layout Execution Pipeline Switches
    if st.session_state.selected_patient_id is not None:
        render_patient_profile_page()
    elif "Dashboard" in st.session_state.current_page:
        render_dashboard_page()
    elif "Patients" in st.session_state.current_page:
        render_patients_page()
    elif "Analytics" in st.session_state.current_page:
        render_analytics_page()
    elif "Recommendations" in st.session_state.current_page:
        render_recommendations_page()
    elif "Settings" in st.session_state.current_page:
        render_settings_page()

if __name__ == "__main__":
    main()