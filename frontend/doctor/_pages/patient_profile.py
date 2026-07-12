import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from frontend.common.utils.api import (
    get_patient as get_patient_by_id,  
    get_patient_sessions,
    get_patient,
    get_dashboard,
)


def render_patient_profile_page():

    patient_id = st.session_state.selected_patient_id

    patient = get_patient(patient_id)
    dashboard = get_dashboard(patient_id)
    sessions = get_patient_sessions(patient_id)

    if not patient:

        st.error("Unable to locate patient.")

        if st.button("Return"):
            st.session_state.selected_patient_id = None
            st.rerun()

        return

    # ======================================================
    # HEADER
    # ======================================================

    h1, h2 = st.columns([4, 1])

    with h1:
        st.title(f"📋 Clinical Case Ledger : {patient['name']}")

    with h2:

        if st.button(
            "← Directory",
            use_container_width=True
        ):

            st.session_state.selected_patient_id = None
            st.rerun()

    st.divider()

    # ======================================================
    # PROFILE
    # ======================================================

    col1, col2 = st.columns([1, 3])

    with col1:

        with st.container(border=True):

            st.markdown(
                "<div style='text-align:center;font-size:70px;'>👤</div>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<h4 style='text-align:center'>{patient['name']}</h4>",
                unsafe_allow_html=True
            )

            st.caption(f"Patient ID : {patient['id']}")

    with col2:

        with st.container(border=True):

            r1, r2, r3 = st.columns(3)

            with r1:

                st.markdown(
                    f"**Age / Gender**  \n{patient['age']} yrs / {patient['gender']}"
                )

            with r2:

                st.markdown(
                    f"**Diagnosis**  \n{patient['injury']}"
                )

            with r3:

                status = dashboard["status"]

                color = "green"

                if status == "WAITING_FOR_SETUP":
                    color = "orange"

                st.markdown(
                    f"**Current Status**  \n:{color}[{status}]"
                )

            st.divider()

            m1, m2, m3, m4 = st.columns(4)

            with m1:

                st.metric(
                    "Recovery Score",
                    f"{dashboard['recovery_score']:.1f}"
                )

            with m2:

                st.metric(
                    "ROM",
                    f"{dashboard['rom']:.1f}°"
                )

            with m3:

                st.metric(
                    "Movement Quality",
                    f"{dashboard['movement_quality']:.1f}%"
                )

            with m4:

                st.metric(
                    "Repetitions",
                    dashboard["rep_count"]
                )

    st.write("")

    tabs = st.tabs(
        [
            "📋 Overview",
            "📂 Session History",
            "📊 Analytics"
        ]
    )

    # ======================================================
    # OVERVIEW
    # ======================================================

    with tabs[0]:

        c1, c2 = st.columns(2)

        with c1:

            with st.container(border=True):

                st.subheader("Today's Exercise")

                st.info(
                    dashboard["exercise"]
                )

        with c2:

            with st.container(border=True):

                st.subheader("AI Recommendation")

                st.success(
                    dashboard["recommendation"]
                )

        st.write("")

        a1, a2 = st.columns(2)

        with a1:

            st.metric(
                "Recovery Trend",
                dashboard["trend"]
            )

        with a2:

            st.metric(
                "Recovery Deviation",
                dashboard["recovery_deviation"]
            )

    # ======================================================
    # SESSION HISTORY
    # ======================================================

    with tabs[1]:

        if len(sessions) == 0:

            st.info("No rehabilitation sessions found.")

        else:

            df = pd.DataFrame([
                {
                    "Timestamp": s["timestamp"],
                    "Exercise": s["exercise"],
                    "ROM": s["rom"],
                    "Recovery": s["recovery_score"],
                    "Movement Quality": s["movement_quality"],
                    "Trend": s["trend"],
                    "Recommendation": s["recommendation"]
                }
                for s in sessions
            ])

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
                # ======================================================
    # ANALYTICS
    # ======================================================

    with tabs[2]:

        if len(sessions) == 0:

            st.info("Not enough rehabilitation sessions to generate analytics.")

        else:

            # --------------------------------------------
            # Prepare Data
            # --------------------------------------------

            sessions = list(reversed(sessions))

            x = list(range(1, len(sessions) + 1))

            recovery = [
                s["recovery_score"]
                for s in sessions
            ]

            rom = [
                s["rom"]
                for s in sessions
            ]

            movement = [
                s["movement_quality"]
                for s in sessions
            ]

            deviation = [
                s["recovery_deviation"]
                for s in sessions
            ]

            chart_layout = dict(
                height=320,
                margin=dict(
                    l=20,
                    r=20,
                    t=35,
                    b=20
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                xaxis=dict(
                    title="Session",
                    showgrid=True,
                    gridcolor="rgba(128,128,128,0.15)"
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor="rgba(128,128,128,0.15)"
                )
            )

            # --------------------------------------------
            # Recovery Score
            # --------------------------------------------

            c1, c2 = st.columns(2)

            with c1:

                st.markdown("### 📈 Recovery Score Progression")

                fig = go.Figure()

                fig.add_trace(

                    go.Scatter(
                        x=x,
                        y=recovery,
                        mode="lines+markers",
                        line=dict(width=3),
                        marker=dict(size=8)
                    )

                )

                fig.update_layout(**chart_layout)

                fig.update_yaxes(title="Recovery Score")

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            # --------------------------------------------
            # ROM
            # --------------------------------------------

            with c2:

                st.markdown("### 📐 Range of Motion")

                fig = go.Figure()

                fig.add_trace(

                    go.Scatter(
                        x=x,
                        y=rom,
                        mode="lines+markers",
                        line=dict(width=3),
                        marker=dict(size=8)
                    )

                )

                fig.update_layout(**chart_layout)

                fig.update_yaxes(title="Degrees")

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            # --------------------------------------------
            # Movement Quality
            # --------------------------------------------

            c3, c4 = st.columns(2)

            with c3:

                st.markdown("### 🏃 Movement Quality")

                fig = go.Figure()

                fig.add_trace(

                    go.Bar(
                        x=x,
                        y=movement
                    )

                )

                fig.update_layout(**chart_layout)

                fig.update_yaxes(title="%")

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            # --------------------------------------------
            # Recovery Deviation
            # --------------------------------------------

            with c4:

                st.markdown("### 📉 Recovery Deviation")

                colors = [
                    "green" if d >= 0 else "red"
                    for d in deviation
                ]

                fig = go.Figure()

                fig.add_trace(

                    go.Bar(
                        x=x,
                        y=deviation,
                        marker_color=colors
                    )

                )

                fig.update_layout(**chart_layout)

                fig.update_yaxes(title="Deviation")

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            st.divider()

            latest = sessions[-1]

            st.subheader("🧠 Latest AI Analysis")

            st.success(
                latest["recommendation"]
            )

            info1, info2, info3 = st.columns(3)

            with info1:
                st.metric(
                    "Current Exercise",
                    latest["exercise"]
                )

            with info2:
                st.metric(
                    "Current Status",
                    latest["status"]
                )

            with info3:
                st.metric(
                    "Repetition Count",
                    latest["rep_count"]
                )