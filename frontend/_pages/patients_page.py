import streamlit as st
import time
from utils.api import get_patients


def render_patients_page():

    st.title("👥 Patient Management Workspace")
    st.markdown("#### Registered Rehabilitation Patients")
    st.divider()

    with st.spinner("Loading patients..."):
        time.sleep(0.3)
        patients = get_patients()

    if not patients:
        st.info("No patients found.")
        return

    injuries = sorted(list(set(p["injury"] for p in patients)))

    search = st.text_input(
        "Search Patient",
        placeholder="Search by patient name..."
    ).strip().lower()

    selected = st.selectbox(
        "Filter by Injury",
        ["All Injuries"] + injuries
    )

    filtered = []

    for patient in patients:

        if search not in patient["name"].lower():
            continue

        if (
            selected != "All Injuries"
            and patient["injury"] != selected
        ):
            continue

        filtered.append(patient)

    cols_per_row = 3

    for i in range(0, len(filtered), cols_per_row):

        cols = st.columns(cols_per_row)

        for j, patient in enumerate(filtered[i:i+cols_per_row]):

            with cols[j]:

                with st.container(border=True):

                    st.subheader(patient["name"])

                    st.write(f"**Age:** {patient['age']}")

                    st.write(f"**Gender:** {patient['gender']}")

                    st.write(f"**Injury:** {patient['injury']}")

                    st.write(f"**Doctor:** {patient['doctor']}")

                    st.divider()

                    if st.button(
                        "Open Clinical Case",
                        key=patient["id"],
                        use_container_width=True
                    ):

                        st.session_state.selected_patient_id = patient["id"]

                        st.switch_page("pages/patient_profile.py")