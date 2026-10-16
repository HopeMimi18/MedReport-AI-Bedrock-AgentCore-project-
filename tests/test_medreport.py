import os
import unittest
from unittest.mock import patch

from botocore.exceptions import ClientError

# Prevent boto3 from trying EC2 metadata during local unit tests
os.environ["AWS_EC2_METADATA_DISABLED"] = "true"

import medreport_agent


class TestMedReportAI(unittest.TestCase):

    def test_health_check(self):
        result = medreport_agent.health_check()

        self.assertEqual(result["status"], "healthy")
        self.assertEqual(
            result["service"],
            "MedReport AI"
        )

    def test_format_medical_report(self):
        report = medreport_agent.format_medical_report(
            incident_summary="Person slipped near stairs",
            affected_person="Staff member",
            injury_condition="Left wrist injury",
            symptoms_observed="Pain and swelling",
            severity_level="Moderate",
            recommended_action="Medical evaluation",
            notes="Person remained conscious"
        )

        self.assertIn(
            "Person slipped near stairs",
            report
        )

        self.assertIn(
            "Left wrist injury",
            report
        )

        self.assertIn(
            "Disclaimer:",
            report
        )

    def test_save_report_without_s3_bucket(self):
        with patch.object(
            medreport_agent,
            "REPORTS_BUCKET",
            None
        ):
            result = medreport_agent.save_report_to_s3(
                "Test medical report"
            )

        self.assertIn(
            "REPORTS_BUCKET environment variable is not configured",
            result
        )

    def test_save_report_to_s3_success(self):
        with patch.object(
            medreport_agent,
            "REPORTS_BUCKET",
            "test-medreport-bucket"
        ):
            with patch.object(
                medreport_agent.s3,
                "put_object"
            ) as mock_put_object:

                result = medreport_agent.save_report_to_s3(
                    "Example report"
                )

                mock_put_object.assert_called_once()

                arguments = mock_put_object.call_args.kwargs

                self.assertEqual(
                    arguments["Bucket"],
                    "test-medreport-bucket"
                )

                self.assertEqual(
                    arguments["Body"],
                    b"Example report"
                )

                self.assertEqual(
                    arguments["ContentType"],
                    "text/plain"
                )

                self.assertTrue(
                    arguments["Key"].startswith(
                        "reports/medical_report_"
                    )
                )

                self.assertEqual(
                    arguments["Metadata"]["generated-by"],
                    "medreport-ai"
                )

                self.assertIn(
                    "Report saved successfully",
                    result
                )

    def test_s3_access_denied_is_handled(self):
        aws_error = ClientError(
            {
                "Error": {
                    "Code": "AccessDenied",
                    "Message": "Access denied"
                }
            },
            "PutObject"
        )

        with patch.object(
            medreport_agent,
            "REPORTS_BUCKET",
            "test-medreport-bucket"
        ):
            with patch.object(
                medreport_agent.s3,
                "put_object",
                side_effect=aws_error
            ):

                result = medreport_agent.save_report_to_s3(
                    "Example report"
                )

        self.assertIn(
            "AccessDenied",
            result
        )

    def test_empty_prompt_is_rejected(self):
        with patch.object(
            medreport_agent,
            "get_agent"
        ) as mock_get_agent:

            result = medreport_agent.invoke(
                {"prompt": ""}
            )

            self.assertIn(
                "Please provide incident notes",
                result["result"]
            )

            mock_get_agent.assert_not_called()

    def test_invalid_payload_is_rejected(self):
        result = medreport_agent.invoke(
            "this is not a dictionary"
        )

        self.assertEqual(
            result["result"],
            "Invalid request format."
        )


if __name__ == "__main__":
    unittest.main()