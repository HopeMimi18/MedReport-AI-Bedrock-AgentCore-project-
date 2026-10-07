from uuid import uuid4
from botocore.exceptions import BotoCoreError, ClientError
import os
from datetime import datetime
from strands import Agent, tool
from strands.models import BedrockModel
import boto3
import logging

try:
    from bedrock_agentcore.runtime import BedrockAgentCoreApp
except ImportError:
    from bedrock_agentcore import BedrockAgentCoreApp


AGENT_NAME = "MedReport AI"
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-pro-v1:0")
REPORTS_BUCKET = os.getenv("REPORTS_BUCKET")

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)

app = BedrockAgentCoreApp()
s3 = boto3.client(
    "s3",
    region_name=AWS_REGION
)



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
- If the user asks to save or log the report, use the save_report_to_s3 tool

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
def save_report_to_s3(report_text: str) -> str:
    """
    Saves a generated medical incident report to Amazon S3.
    """

    if not REPORTS_BUCKET:
        logger.warning(
        "Report save skipped because REPORTS_BUCKET is not configured"
    )

        return "REPORTS_BUCKET environment variable is not configured."

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_id = uuid4().hex[:8]

    file_name = (
        f"reports/medical_report_{timestamp}_{report_id}.txt"
    )

    try:
        s3.put_object(
            Bucket=REPORTS_BUCKET,
            Key=file_name,
            Body=report_text.encode("utf-8"),
            ContentType="text/plain"
        )

        logger.info(
            "Medical report saved to S3 bucket=%s key=%s",
            REPORTS_BUCKET,
            file_name
       )

        return (
            f"Report saved successfully to "
            f"s3://{REPORTS_BUCKET}/{file_name}"
        )

    except ClientError as error:
        error_code = error.response.get(
            "Error", {}
        ).get("Code", "Unknown")

        logger.error(
        "Amazon S3 upload failed with AWS error code=%s",
        error_code
        )

        return (
            f"Unable to save report to Amazon S3. "
            f"AWS error: {error_code}"
        )

    except BotoCoreError:
        logger.exception(
            "Amazon S3 connection or configuration error"
        )

        return (
            "Unable to save report to Amazon S3 "
            "because of an AWS connection or configuration error."
    )

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

        logger.info(
            "Initializing MedReport AI model=%s region=%s",
            MODEL_ID,
            AWS_REGION
        )
        
        model = BedrockModel(
            model_id=MODEL_ID,
            region_name=AWS_REGION,
            temperature=0.5,
            max_tokens=1024
        )

        _agent = Agent(
            model=model,
            system_prompt=SYSTEM_PROMPT,
            tools=[format_medical_report,save_report_to_s3]
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
    logger.info("MedReport AI invocation received")
    if not user_message:
        logger.warning("Invocation rejected because prompt was empty")

        return {
            "result": "Please provide incident notes so I can format the medical incident report."
        }

    user_message = payload.get("prompt", "").strip()

    if not user_message:
        return {
            "result": "Please provide incident notes so I can format the medical incident report."
        }

    response = get_agent()(user_message)
    logger.info("MedReport AI invocation completed successfully")

    return {
        "result": str(response)
    }


if __name__ == "__main__":
    app.run()