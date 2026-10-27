import streamlit as st

from medreport_agent import (
    AGENT_NAME,
    AWS_REGION,
    REPORTS_BUCKET,
    get_agent,
    health_check,
    save_report_to_s3,
)


st.set_page_config(
    page_title="MedReport AI",
    page_icon="🏥",
    layout="centered"
)


st.title("🏥 MedReport AI")

st.write(
    "Convert incident notes into a structured AI-assisted "
    "medical incident report."
)

st.warning(
    "For demonstration purposes only. Do not enter real confidential "
    "patient information."
)


# -----------------------------
# Sidebar
# -----------------------------

with st.sidebar:
    st.header("System Status")

    health = health_check()

    st.success(
        f"{health['service']} is {health['status']}"
    )

    st.write(f"**AWS Region:** {AWS_REGION}")

    if REPORTS_BUCKET:
        st.success("Amazon S3 storage configured")
    else:
        st.warning("Amazon S3 storage not configured")


# -----------------------------
# Incident Input
# -----------------------------

st.subheader("Incident Notes")

incident_notes = st.text_area(
    "Describe what happened:",
    height=180,
    placeholder=(
        "Example: A staff member slipped near the stairs "
        "and injured their left wrist. They reported "
        "moderate pain and swelling."
    )
)


save_to_s3 = st.checkbox(
    "Save generated report to Amazon S3"
)


# -----------------------------
# Generate Report
# -----------------------------

if st.button(
    "Generate Incident Report",
    type="primary",
    use_container_width=True
):

    if not incident_notes.strip():

        st.error(
            "Please enter incident notes before generating a report."
        )

    else:

        try:

            with st.spinner(
                "MedReport AI is analysing the incident..."
            ):

                agent = get_agent()

                response = agent(
                    incident_notes.strip()
                )

                report = str(response)

            st.session_state["report"] = report

            st.success(
                "Incident report generated successfully."
            )

        except Exception:
            st.error(
                "The report could not be generated. "
                "Check your AWS configuration and try again."
            )


# -----------------------------
# Display Report
# -----------------------------

if "report" in st.session_state:

    report = st.session_state["report"]

    st.divider()

    st.subheader("Generated Incident Report")

    st.text_area(
        "Report",
        value=report,
        height=350,
        disabled=True
    )

    st.download_button(
        label="Download Report",
        data=report,
        file_name="medreport_incident_report.txt",
        mime="text/plain",
        use_container_width=True
    )


    # -----------------------------
    # Optional S3 Storage
    # -----------------------------

    if save_to_s3:

        if st.button(
            "Save Report to Amazon S3",
            use_container_width=True
        ):

            result = save_report_to_s3(
                report
            )

            if result.startswith(
                "Report saved successfully"
            ):
                st.success(result)

            else:
                st.error(result)


st.divider()

st.caption(
    "MedReport AI | Amazon Bedrock • Amazon Nova Pro • "
    "Bedrock AgentCore • Amazon S3"
)