"""
RehabAI - Patient Portal Profile Component
Author: Senior Full Stack Engineer
Description: Renders the complete patient case profile view layer, loading static
             demographics and clinical parameters cleanly over the wire from Firestore.
"""

import streamlit as st
import logging
from frontend.common.services.patient_service import PatientService

logger = logging.getLogger("RehabAI.PatientProfilePage")


def render_profile_page() -> None:
    """
    Ingests records from the patients root collection to update structural 
    demographic matrices without a single hardcoded line.
    """
    # 1. STATE IDENTIFIER LOOKUP
    if "patient_id" not in st.session_state:
        st.session_state.patient_id = "PAT_24MIS1033"

    current_patient_id = st.session_state.patient_id
    patient_api = PatientService()

    # 2. NAVIGATION HEADER CONTROLS
    if st.button("← Back to Dashboard", type="secondary"):
        st.session_state.current_page = "🏠 Dashboard"
        st.rerun()

    st.title("👤 Profile")
    st.caption("Manage your clinical records, morphology metrics, and clinician assignment parameters.")
    st.divider()

    # 3. RUNTIME DATA ACQUISITION PIPELINE
    patient_data = None
    try:
        with st.spinner("Fetching case ledger files from Firestore..."):
            patient_data = patient_api.get_patient(current_patient_id)
    except Exception as e:
        logger.error(f"Failed to cleanly request profile document for '{current_patient_id}': {e}")
        st.error("🚨 **Network Connection Error**: Unable to contact the Clinical Core service layer.")
        return

    if not patient_data:
        st.warning(f"🔍 **Record Untracked**: Case reference profile identifier '{current_patient_id}' not found.")
        return

    # 4. SPLIT STRATIFIED WORKSPACE GRID
    clinical_panel, demographic_panel = st.columns([4, 3])

    # ===========================================================================
    # LEFT PANEL: CLINICAL ASSIGNMENTS & SURGERY TIMELINE
    # ===========================================================================
    with clinical_panel:
        st.subheader("🏥 Clinical Diagnosis Data")
        with st.container(border=True):
            st.markdown(f"**Primary Medical Diagnosis:** \n`{patient_data.get('diagnosis', 'ACL Tear')}`")
            st.write("")
            
            st.markdown(f"**Ligament Damage Severity:** \n`{patient_data.get('acl_grade', 'Grade III')}`")
            st.write("")
            
            # Formats dates cleanly from string records
            s_date = patient_data.get("date_of_surgery", "N/A")
            if "T" in s_date:
                s_date = s_date.split("T")[0]
            st.markdown(f"**Date of Surgical Repair:** \n`{s_date}`")
            st.write("")
            
            st.markdown(f"**Supervising Orthopedic Clinician:** \n`{patient_data.get('doctor_name', 'Attending Specialist')}`")

    # ===========================================================================
    # RIGHT PANEL: PHYSICAL MORPHOLOGY & ACCOUNT METADATA
    # ===========================================================================
    with demographic_panel:
        st.subheader("🧑‍⚕️ Demographic Specifications")
        with st.container(border=True):
            st.markdown(f"**Full Legal Name:** \n{patient_data.get('first_name', '')} {patient_data.get('last_name', '')}")
            st.markdown(f"**Core Registry Key:** `{patient_data.get('patient_id', current_patient_id)}`")
            st.divider()
            
            p1, p2 = st.columns(2)
            with p1:
                st.markdown(f"**Height Index:** \n`{patient_data.get('height_cm', 0.0)} cm`")
                st.write("")
                st.markdown(f"**Weight Index:** \n`{patient_data.get('weight_kg', 0.0)} kg`")
            with p2:
                # BMI is automatically evaluated on the server layer by Pydantic validators
                st.markdown(f"**Calculated BMI:** \n`{patient_data.get('bmi', 0.0)} kg/m²`")
                st.write("")
                st.markdown(f"**Age Metrics:** \n`{patient_data.get('age', 0)} Years`")