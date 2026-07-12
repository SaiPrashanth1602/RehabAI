import streamlit as st
import pandas as pd

from frontend.common.utils.api import get_patients


def render_patient_table():

    patients = get_patients()

    if len(patients) == 0:

        st.info("No registered patients.")

        return

    table = pd.DataFrame([

        {

            "Patient": p["name"],

            "Age": p["age"],

            "Gender": p["gender"],

            "Diagnosis": p["injury"],

            "Doctor": p["doctor"]

        }

        for p in patients

    ])

    st.dataframe(

        table,

        use_container_width=True,

        hide_index=True

    )