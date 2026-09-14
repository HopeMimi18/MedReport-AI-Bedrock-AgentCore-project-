import os
from datetime import datetime
from strands import Agent, tool
from strands.models import BedrockModel

try:
    from bedrock_agentcore.runtime import BedrockAgentCoreApp
except ImportError:
    from bedrock_agentcore import BedrockAgentCoreApp


AGENT_NAME = "MedReport AI"
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-pro-v1:0")

app = BedrockAgentCoreApp()

SYSTEM_PROMPT = f"""
You are {AGENT_NAME}, a professional healthcare incident reporting assistant.

Your personality:
- Calm, clear, and professional
- Focused on safety and accuracy
- Helpful without sounding robotic
- You write in a structured medical-report style

Your job:
- Convert messy incident notes into clean structured incident reports
- Extract important details such as injury, symptoms, body part affected, severity, and recommendations
- Use professional wording
- Keep reports concise but complete

Rules:
- Do not pretend to be a doctor
- Do not provide a diagnosis
- Do not invent facts that were not provided
- If details are missing, clearly say "Not specified"
- Always include a short disclaimer that the report is AI-generated and should be reviewed by a healthcare professional if needed
- Always use the format_medical_report tool to create the final report
- If the user asks to save or log the report, use the save_report_to_file tool

Report format:
Incident Report
- Incident Summary:
- Affected Person:
- Injury/Condition:
- Symptoms Observed:
- Severity Level:
- Recommended Action:
- Notes:
"""


@tool
def format_medical_report(
    incident_summary: str,
    affected_person: str,
    injury_condition: str,
    symptoms_observed: str,
    severity_level: str,
    recommended_action: str,
    notes: str
) -> str:
    """
    Formats medical incident information into a structured report.
    """
    return f"""Incident Report
- Incident Summary: {incident_summary}
- Affected Person: {affected_person}
- Injury/Condition: {injury_condition}
- Symptoms Observed: {symptoms_observed}
- Severity Level: {severity_level}
- Recommended Action: {recommended_action}
- Notes: {notes}

Disclaimer: This AI-generated report is for documentation support only and should be reviewed by a qualified healthcare professional if necessary.
"""


@tool
def save_report_to_file(report_text: str, filename: str = "medical_reports.txt") -> str:
    """
    Saves a generated medical report to a temporary file.

    In AWS AgentCore, local files are not long-term storage.
    For production, use S3 or a database.
    """
    safe_filename = os.path.basename(filename) or "medical_reports.txt"
    file_path = os.path.join("/tmp", safe_filename)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(file_path, "a", encoding="utf-8") as file:
        file.write(f"\n--- Report Saved: {timestamp} ---\n")
        file.write(report_text)
        file.write("\n")

    return f"Report saved successfully to {file_path}"


_agent = None


def get_agent():
    """
    Lazy-loads the agent only when a request comes in.
    This is better for cloud startup.
    """
    global _agent

    if _agent is None:
        model = BedrockModel(
            model_id=MODEL_ID,
            region_name=AWS_REGION,
            temperature=0.5,
            max_tokens=1024
        )

        _agent = Agent(
            model=model,
            system_prompt=SYSTEM_PROMPT,
            tools=[format_medical_report, save_report_to_file]
        )

    return _agent


@app.entrypoint
def invoke(payload):
    """
    AgentCore calls this function.

    Expected input:
    {
        "prompt": "Patient slipped near the stairs..."
    }
    """
    user_message = payload.get("prompt", "").strip()

    if not user_message:
        return {
            "result": "Please provide incident notes so I can format the medical incident report."
        }

    response = get_agent()(user_message)

    return {
        "result": str(response)
    }


if __name__ == "__main__":
    app.run()