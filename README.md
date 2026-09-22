# MedReport AI - Amazon Bedrock AgentCore

MedReport AI is an AI-powered medical incident reporting assistant built with AWS generative AI services. It converts unstructured incident notes into clear, structured incident reports using Amazon Bedrock, Amazon Nova Pro, Strands Agents, and Amazon Bedrock AgentCore.

## WeThinkCode_ Verification

**Verification Code:** `WTC-8A3CUF37`

## Project Overview

The goal of MedReport AI is to help transform rough or incomplete incident notes into a consistent report format that can be reviewed by a healthcare professional.

The application is designed to:

- Accept natural-language incident notes
- Identify key incident details
- Structure the information into a professional report
- Highlight missing information as "Not specified"
- Avoid inventing medical facts
- Avoid providing diagnoses
- Include an AI-generated-report disclaimer
- Run as an agent through Amazon Bedrock AgentCore

> **Important:** MedReport AI is a learning and demonstration project. It is not a medical diagnostic system and should not be used as a substitute for professional medical advice.

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
   |                 |
   v                 v
Format Report     Save Report
                      |
                      v
             Temporary /tmp storage
```

## AWS and AI Technologies

- **Amazon Bedrock** - managed access to foundation models
- **Amazon Nova Pro** - foundation model used by the agent
- **Amazon Bedrock AgentCore** - runtime for hosting and invoking the AI agent
- **Strands Agents** - agent framework and tool integration
- **Boto3** - AWS SDK for Python
- **Docker** - containerised runtime support

## Main Features

### Structured Incident Reporting

The agent converts unstructured notes into the following format:

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

### Responsible AI Behaviour

The system prompt instructs the agent to:

- Never pretend to be a doctor
- Never provide a diagnosis
- Never invent information that was not supplied
- Clearly identify missing details
- Keep reports concise and professional
- Include a disclaimer for human review

### Custom Agent Tools

The project currently includes:

- `format_medical_report` - creates the structured incident report
- `save_report_to_file` - saves a generated report to temporary runtime storage

## Project Structure

```text
.
|-- .bedrock_agentcore/
|   `-- medreport_ai/
|       `-- Dockerfile
|-- .dockerignore
|-- .gitignore
|-- medreport_agent.py
|-- requirements.txt
|-- test_nova.py
`-- README.md
```

## Requirements

- Python 3
- AWS account
- AWS credentials configured locally
- Access to Amazon Bedrock
- Amazon Bedrock AgentCore tooling

Python dependencies are listed in `requirements.txt`:

```text
strands-agents
bedrock-agentcore
boto3
```

## Local Setup

Clone the repository:

```bash
git clone https://github.com/HopeMimi18/MedReport-AI-Bedrock-AgentCore-project-.git
cd MedReport-AI-Bedrock-AgentCore-project-
```

Create a virtual environment:

### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure AWS credentials using the AWS CLI before running the project.

## Environment Configuration

The application supports the following environment variables:

```text
AWS_REGION
BEDROCK_MODEL_ID
```

Defaults used by the current implementation:

```text
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0
```

Do not commit AWS credentials, access keys, `.env` files, or private configuration files to GitHub.

## Example Input

```text
A staff member slipped near the stairs and injured their left wrist.
They reported moderate pain and swelling but remained conscious.
```

The agent processes the notes and produces a structured incident report for review.

## Testing

The repository includes `test_nova.py` for testing access to the Amazon Nova model through Amazon Bedrock.

## Current Limitations

- Saved reports currently use temporary `/tmp` runtime storage
- The system is not intended for real clinical diagnosis
- Real patient information should not be used in development or demonstrations

## Planned Improvements

Future iterations may include:

- Amazon S3 for persistent report storage
- Amazon DynamoDB for incident metadata
- Amazon CloudWatch for monitoring and logging
- Amazon SNS for incident notifications
- API Gateway for controlled API access
- Authentication and role-based access
- Automated testing
- A web dashboard for viewing generated reports

## Learning Goals

This project is part of my Cloud Computing learning journey and demonstrates practical experience with:

- AWS cloud services
- Generative AI
- AI agents
- Amazon Bedrock
- Amazon Bedrock AgentCore
- Python
- Containerisation
- Responsible AI design
- Cloud application architecture

## Author

**Hope Lekgeu**

Cloud Computing / Software Engineering Student

## Disclaimer

This project is for educational and demonstration purposes. Generated reports must be reviewed by an appropriate human professional before being relied upon for real-world healthcare decisions.
