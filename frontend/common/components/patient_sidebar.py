"""
RehabAI - Patient Portal Sidebar Component (Minimal Navigation Version)
Author: Senior Python Software Engineer
Description: Renders an uncluttered, navigation-focused Streamlit sidebar interface.
"""

import streamlit as st

def render_patient_sidebar() -> str:
    """
    Renders the unified Streamlit sidebar for the Patient Portal workspace.
    
    Manages navigation mapping matrix and outputs the selected target view 
    for the master router.
    
    Returns:
        str: The currently active or newly selected target page title string.
    """
    # -----------------------------------------------------------------------
    # 1. NAVIGATION MAPPING MATRIX
    # -----------------------------------------------------------------------
    NAV_MAPPING = {
        "🏠 Dashboard": "🏠 Dashboard",
        "静 My Rehabilitation": "🦵 My Rehabilitation",
        "📊 Progress": "📈 Progress",
        "👤 Profile": "👤 Profile"
    }
    
    # Initialize page tracking safety fallback configuration
    if "current_page" not in st.session_state:
        st.session_state.current_page = "🏠 Dashboard"

    with st.sidebar:
        # -----------------------------------------------------------------------
        # 2. BRANDING AND HEADER CONTEXT
        # -----------------------------------------------------------------------
        st.title("🦵 RehabAI")
        st.caption("Patient Portal")
        st.divider()

        # -----------------------------------------------------------------------
        # 3. INTERACTIVE APPLICATION NAVIGATION LIST
        # -----------------------------------------------------------------------
        st.markdown("#### **Navigation**")
        
        # Iteratively render styled buttons matching internal state structures
        for internal_state, display_label in NAV_MAPPING.items():
            is_active = st.session_state.current_page == internal_state
            button_type = "primary" if is_active else "secondary"
            
            if st.button(
                label=display_label,
                key=f"nav_btn_{internal_state}",
                use_container_width=True,
                type=button_type
            ):
                if st.session_state.current_page != internal_state:
                    st.session_state.current_page = internal_state
                    st.rerun()

        st.divider()
        st.caption("RehabAI v1.0")

    return st.session_state.current_page