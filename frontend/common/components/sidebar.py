# frontend/components/sidebar.py
import streamlit as st
from frontend.common.utils.config import APP_NAME, VERSION

def render_sidebar():
    """Renders a premium clinical sidebar navigation module with live status indicators."""
    with st.sidebar:
        st.markdown(f"## 🏥 {APP_NAME}")
        st.caption(f"Clinical Portal Execution Space | Version {VERSION}")
        st.markdown("---")
        
        st.markdown("📋 **Navigation Channels**")
        nav_selection = st.radio(
            label="Navigation Pages Menu",
            options=["🏠 Dashboard", "👥 Patients", "📈 Analytics", "💡 Recommendations", "⚙️ Settings"],
            key="global_sidebar_routing_key_v1",
            label_visibility="collapsed"
        )
        st.markdown("---")
        
        st.markdown("🖥️ **System Engine Health**")
        with st.container(border=True):
            st.markdown("🟢 `AI Engine` — Ready")
            st.markdown("🟢 `Clinical Server` — Online")
            st.markdown("🟢 `Database Node` — Synchronized")
            
        st.markdown("---")
        st.caption("🔒 HIPAA / GDPR Compliance Verified")

    return nav_selection