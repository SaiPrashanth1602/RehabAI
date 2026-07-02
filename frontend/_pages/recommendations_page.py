import streamlit as st

from utils.api import get_patients, get_dashboard


def render_recommendations_page():

    st.title("💡 AI Rehabilitation Recommendations")
    st.markdown("#### Personalized treatment recommendations generated from the latest rehabilitation session")
    st.markdown("---")

    patients = get_patients()

    if len(patients) == 0:
        st.info("No patients available.")
        return

    for patient in patients:

        dashboard = get_dashboard(patient["id"])

        with st.container(border=True):

            st.markdown(f"### 👤 {patient['name']}")

            c1, c2 = st.columns(2)

            with c1:
                st.metric(
                    "Recovery Score",
                    f"{dashboard['recovery_score']:.1f}"
                )

            with c2:
                st.metric(
                    "Trend",
                    dashboard["trend"]
                )

            st.markdown(f"**Exercise:** {dashboard['exercise']}")

            st.markdown(f"**Status:** {dashboard['status']}")

            st.success(dashboard["recommendation"])

            st.divider()