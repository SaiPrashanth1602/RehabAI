import streamlit as st
import plotly.graph_objects as go

from utils.api import get_sessions


def render_charts():

    sessions = get_sessions()

    if len(sessions) == 0:

        st.info("No rehabilitation sessions available.")

        return

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

    layout = dict(

        height=300,

        margin=dict(

            l=20,

            r=20,

            t=30,

            b=20

        ),

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)",

        showlegend=False

    )

    c1, c2 = st.columns(2)

    with c1:

        st.markdown("### 📈 Recovery Trend")

        fig = go.Figure()

        fig.add_trace(

            go.Scatter(

                x=x,

                y=recovery,

                mode="lines+markers"

            )

        )

        fig.update_layout(**layout)

        st.plotly_chart(

            fig,

            use_container_width=True

        )

    with c2:

        st.markdown("### 📐 Range of Motion")

        fig = go.Figure()

        fig.add_trace(

            go.Scatter(

                x=x,

                y=rom,

                mode="lines+markers"

            )

        )

        fig.update_layout(**layout)

        st.plotly_chart(

            fig,

            use_container_width=True

        )