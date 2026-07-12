# frontend/pages/analytics_page.py
import streamlit as st
import plotly.graph_objects as go
from frontend.common.utils.mock_data import TRENDS_MOCK

def render_analytics_page():
    st.title("📈 Advanced Clinical Analytics Matrix")
    st.markdown("#### Longitudinal Telemetry Evaluation & Treatment Program Compliance")
    st.markdown("---")

    stat_c1, stat_c2 = st.columns(2)
    stat_c1.metric(label="⏱️ Total Session Duration", value="420 mins")
    stat_c2.metric(label="✅ Program Compliance Metric", value="94.2%")

    st.markdown("##")
    chart_theme_defaults = dict(
        margin=dict(l=40, r=20, t=20, b=40), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=240
    )
    st.markdown("📈 **Recovery Track Progression Spline**")
    f1 = go.Figure(go.Scatter(x=TRENDS_MOCK["sessions"], y=TRENDS_MOCK["recovery_series"], mode='lines+markers', line=dict(color='#0F766E', width=3)))
    f1.update_layout(**chart_theme_defaults)
    st.plotly_chart(f1, use_container_width=True)