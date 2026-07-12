import streamlit as st
import pandas as pd

from frontend.common.utils.api import get_sessions


def render_session_history():

    sessions = get_sessions()

    if len(sessions) == 0:

        st.info("No rehabilitation sessions available.")

        return

    df = pd.DataFrame([

        {

            "Patient": s["patient_id"],

            "Exercise": s["exercise"],

            "Status": s["status"],

            "ROM": s["rom"],

            "Recovery": s["recovery_score"],

            "Movement Quality": s["movement_quality"],

            "Trend": s["trend"],

            "Timestamp": s["timestamp"]

        }

        for s in sessions

    ])

    st.dataframe(

        df,

        use_container_width=True,

        hide_index=True

    )