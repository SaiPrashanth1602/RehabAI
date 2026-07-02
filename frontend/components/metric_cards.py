import streamlit as st
from utils.api import get_dashboard_overview


def render_metric_cards():

    stats = get_dashboard_overview()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "👥 Patients",
            stats["total_patients"]
        )

    with c2:
        st.metric(
            "📂 Sessions",
            stats["total_sessions"]
        )

    with c3:
        st.metric(
            "💚 Avg Recovery",
            f"{stats['average_recovery_score']:.1f}"
        )

    with c4:
        st.metric(
            "📐 Avg ROM",
            f"{stats['average_rom']:.1f}°"
        )