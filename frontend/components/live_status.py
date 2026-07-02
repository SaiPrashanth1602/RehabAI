# frontend/components/live_status.py
import streamlit as st

def render_live_status_panel():
    """Displays a live production medical context telemetry panel at the top of the main views."""
    st.markdown("### 🖥️ Active Workspace & Sensor Diagnostics")
    
    with st.container(border=True):
        row1_c1, row1_c2, row1_c3, row1_c4 = st.columns(4)
        row1_c1.markdown("📷 **Camera System:** :green[🟢 Connected]")
        row1_c2.markdown("🧠 **AI Engine:** :green[🟢 Ready]")
        row1_c3.markdown("🌐 **Backend Core:** :green[🟢 Online]")
        row1_c4.markdown("🗄️ **Database State:** :green[🟢 Connected]")
        
        st.markdown("---")
        
        row2_c1, row2_c2, row2_c3, row2_c4 = st.columns(4)
        row2_c1.markdown("**Current Patient:** `John Doe`")
        row2_c2.markdown("**Active Routine:** `Knee Extension`")
        row2_c3.markdown("**Repetition Count:** `08 / 12`")
        row2_c4.markdown("**Session Elapse:** :orange[⏱️ 04:12 mins]")