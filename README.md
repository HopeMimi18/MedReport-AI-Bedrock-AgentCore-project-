# MedReport AI — Amazon Bedrock AgentCore

MedReport AI is an AI-powered medical incident reporting assistant built with AWS generative AI and cloud services.

The application converts unstructured incident notes into clear, structured incident reports using **Amazon Bedrock**, **Amazon Nova Pro**, **Strands Agents**, **Amazon Bedrock AgentCore**, and **Amazon S3**.

---

## WeThinkCode_ Verification

**Verification Code:** `WTC-8A3CUF37`

---

## Project Overview

Medical incident notes are often written quickly and may be incomplete, inconsistent, or difficult to review.

MedReport AI is designed to transform those notes into a consistent incident-report format while maintaining clear safety boundaries.

The application can:

- Accept natural-language incident notes
- Extract important information from the notes
- Format the information into a structured incident report
- Identify missing information as `Not specified`
- Avoid inventing information that was not provided
- Avoid making medical diagnoses
- Generate professional report wording
- Save generated reports to Amazon S3
- Handle AWS S3 errors gracefully
- Generate unique report identifiers
- Run as an AI agent through Amazon Bedrock AgentCore

> **Important:** MedReport AI is an educational and demonstration project. It is not a medical diagnostic system and should not replace professional medical advice or clinical judgment.

---

## Current Architecture

```text
User Incident Notes
        |
        v
Amazon Bedrock AgentCore
        |
        v
MedReport AI Agent
        |
        v
Amazon Nova Pro
        |
        v
Strands Agent Tools
   |                    |
   v                    v
Format Report       Save Report
                         |
                         v
                    Amazon S3
                         |
                         v
              Persistent Report Storage
```

---

## How It Works

A user provides notes describing an incident.

Example:

```text
A staff member slipped near the stairs and injured their left wrist.
They reported moderate pain and swelling but remained conscious.
```

The request is processed by the MedReport AI agent running through Amazon Bedrock AgentCore.

Amazon Nova Pro analyses the notes and extracts information such as:

- Incident summary
- Affected person
- Injury or condition
- Symptoms
- Severity
- Recommended action
- Additional notes

The information is then passed to a custom Strands Agent tool that creates the final structured report.

If the user requests that the report be saved, another tool uploads it to a private Amazon S3 bucket.

---

## Example Output

```text
Incident Report

- Incident Summary: Staff member slipped near the stairs.
- Affected Person: Staff member
- Injury/Condition: Left wrist injury
- Symptoms Observed: Moderate pain and swelling
- Severity Level: Moderate
- Recommended Action: Seek appropriate medical evaluation.
- Notes: Person remained conscious.

Disclaimer: This AI-generated report is for documentation support only
and should be reviewed by a qualified healthcare professional if necessary.
```

---

## AWS Services and Technologies

### Amazon Bedrock

Amazon Bedrock provides managed access to foundation models used by the application.

---

### Amazon Nova Pro

Amazon Nova Pro is the foundation model currently used by MedReport AI to understand incident notes and generate structured information.

Default model:

```text
us.amazon.nova-pro-v1:0
```

---

### Amazon Bedrock AgentCore

Bedrock AgentCore provides the runtime used to host and invoke the AI agent.

The main application exposes an AgentCore entry point through:

```python
@app.entrypoint
def invoke(payload):
```

---

### Amazon S3

Amazon S3 is used for persistent storage of generated incident reports.

Reports are stored using object keys similar to:

```text
reports/medical_report_20261002_123456_a1b2c3d4.txt
```

A unique ID is added to each report filename to reduce the risk of two reports overwriting each other.

---

### Strands Agents

Strands Agents provides the agent framework and custom tool functionality used by MedReport AI.

---

### Boto3

Boto3 is the AWS SDK for Python.

The project uses Boto3 to communicate with Amazon S3.

---

### Docker

The project includes Docker configuration used by Bedrock AgentCore for containerised deployment.

---

## Main Features

### 1. Structured Incident Reporting

The AI converts unstructured incident notes into:

```text
Incident Report
- Incident Summary:
- Affected Person:
- Injury/Condition:
- Symptoms Observed:
- Severity Level:
- Recommended Action:
- Notes:
```

---

### 2. Responsible AI Behaviour

The system prompt instructs the agent to:

- Never pretend to be a doctor
- Never provide a diagnosis
- Never invent information
- Clearly indicate when information is missing
- Use professional and concise wording
- Include an AI-generated report disclaimer
- Recommend human review when appropriate

---

### 3. Amazon S3 Report Storage

Generated reports can be saved directly to Amazon S3.

The application uses:

```python
s3.put_object()
```

to upload the report.

---

### 4. Unique Report IDs

Each report receives a short UUID value.

Example:

```text
a1b2c3d4
```

This is combined with the timestamp:

```text
medical_report_20261002_123456_a1b2c3d4.txt
```

This helps prevent filename collisions.

---

### 5. AWS Error Handling

The project handles AWS SDK errors using:

```python
ClientError
BotoCoreError
```

If an S3 operation fails, the agent returns a controlled error message instead of crashing.

---

### 6. Lazy Agent Initialisation

The AI agent is created only when the first request arrives.

```python
_agent = None
```

The `get_agent()` function then initialises the model when required.

This avoids unnecessary agent creation during application startup.

---

## Custom Agent Tools

### `format_medical_report`

Creates the final structured incident report.

It receives:

```text
incident_summary
affected_person
injury_condition
symptoms_observed
severity_level
recommended_action
notes
```

---

### `save_report_to_s3`

Stores a generated incident report in Amazon S3.

The tool:

- Checks whether an S3 bucket has been configured
- Generates a timestamp
- Generates a unique report ID
- Creates an S3 object key
- Uploads the report
- Handles AWS errors safely
- Returns the S3 location when successful

---

## Project Structure

```text
MedReport-AI-Bedrock-AgentCore-project-/
│
├── .bedrock_agentcore/
│   └── medreport_ai/
│       └── Dockerfile
│
├── .dockerignore
├── .gitignore
├── medreport_agent.py
├── requirements.txt
├── test_nova.py
└── README.md
```

---

## Python Dependencies

Dependencies are listed in:

```text
requirements.txt
```

Current dependencies:

```text
strands-agents
bedrock-agentcore
boto3
```

Install them with:

```bash
pip install -r requirements.txt
```

---

# Local Setup

## Clone the Repository

```bash
git clone https://github.com/HopeMimi18/MedReport-AI-Bedrock-AgentCore-project-.git

cd MedReport-AI-Bedrock-AgentCore-project-
```

---

## Windows Setup

### 1. Check Python

Open PowerShell:

```powershell
python --version
```

Python 3.10 or later is recommended.

---

### 2. Create a Virtual Environment

```powershell
python -m venv .venv
```

---

### 3. Activate the Virtual Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

Your terminal should change to something similar to:

```text
(.venv) PS C:\Users\YourName\MedReport-AI-Bedrock-AgentCore-project->
```

If PowerShell blocks the activation script:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then try again:

```powershell
.\.venv\Scripts\Activate.ps