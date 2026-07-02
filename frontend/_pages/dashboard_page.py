# frontend/pages/dashboard_page.py
import streamlit as st
import time
from components.metric_cards import render_metric_cards
from components.charts import render_charts
from components.tables import render_patient_table
from components.recommendations import render_recommendation
from components.session_history import render_session_history
from components.live_status import render_live_status_panel

def render_dashboard_page():
    st.markdown("# RehabAI Central Workspace")
    st.markdown("##### Clinical Operations Portal & Adaptive Patient Diagnostics Engine")
    st.markdown("---")

    with st.spinner("Synchronizing diagnostic workspace layers..."):
        time.sleep(0.2)
        render_live_status_panel()

    st.markdown("##")
    render_metric_cards()
    st.markdown("##")
    render_charts()
    st.markdown("##")
    
    split_col1, split_col2 = st.columns([3, 2])
    with split_col1:
        st.markdown("📋 **Active Patient Directory Overview**")
        render_patient_table()
    with split_col2:
        with split_col2:
            render_live_status_panel()
        
    st.markdown("---")
    st.markdown("📂 **Recent Rehabilitation Activity Logs**")
    render_session_history()