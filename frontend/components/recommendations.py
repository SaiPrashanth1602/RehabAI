import streamlit as st

from utils.api import get_dashboard


def render_recommendation(patient_id):

    dashboard = get_dashboard(patient_id)

    if not dashboard:

        st.info("No recommendation available.")

        return

    with st.container(border=True):

        st.markdown("### 🧠 AI Rehabilitation Recommendation")

        st.caption(
            f"Exercise : {dashboard['exercise']}"
        )

        st.markdown("---")

        c1, c2 = st.columns(2)

        with c1:

            st.metric(
                "Recovery Trend",
                dashboard["trend"]
            )

        with c2:

            st.metric(
                "Recovery Score",
                f"{dashboard['recovery_score']:.1f}"
            )

        st.markdown("---")

        st.markdown("#### Recommendation")

        st.success(
            dashboard["recommendation"]
        )

        st.markdown("---")

        a, b = st.columns(2)

        with a:

            st.metric(
                "Movement Quality",
                f"{dashboard['movement_quality']:.1f}%"
            )

        with b:

            st.metric(
                "ROM",
                f"{dashboard['rom']:.1f}°"
            )