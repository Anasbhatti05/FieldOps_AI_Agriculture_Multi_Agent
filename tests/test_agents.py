import os
import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from agents.coordinator import coordinate
from agents.models import FieldAssessment
from app import build_report
from vision.inference import inspect_crop_image, vision_enabled


def sample_field(**changes):
    values = {
        "crop": "Wheat",
        "crop_stage": "Flowering",
        "field_area_acres": 5,
        "soil_moisture_pct": 17,
        "recent_rain_mm": 1,
        "forecast_rain_mm": 0,
        "temperature_c": 34,
        "wind_kph": 8,
        "location": "Multan",
        "image_bytes": None,
        "notes": "Some leaves look pale",
    }
    values.update(changes)
    return FieldAssessment(**values)


class AgentWorkflowTests(unittest.TestCase):
    def test_streamlit_cloud_secrets_can_enable_private_vision(self):
        response = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content=json.dumps(
                            {
                                "visible_signs": "Leaves appear pale",
                                "possible_causes": "Several possibilities",
                                "next_check": "Compare several plants",
                            }
                        )
                    )
                )
            ]
        )
        completion = unittest.mock.Mock(return_value=response)
        client = SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(create=completion))
        )
        streamlit_module = SimpleNamespace(
            secrets={"GROQ_API_KEY": "fresh-test-key", "GROQ_VISION_ENABLED": "true"}
        )
        with patch.dict(
            os.environ,
            {"GROQ_API_KEY": "", "GROQ_VISION_ENABLED": "", "GROQ_VISION_MODEL": ""},
        ):
            with patch("vision.inference.st", streamlit_module):
                with patch("vision.inference.Groq", return_value=client) as groq_client:
                    result = inspect_crop_image(b"test-image")

        groq_client.assert_called_once_with(api_key="fresh-test-key")
        completion.assert_called_once()
        self.assertIn("Leaves appear pale", result["finding"])

    def test_groq_vision_is_disabled_even_when_a_key_exists(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-key", "GROQ_VISION_ENABLED": "false"}):
            with patch("vision.inference.Groq") as groq_client:
                result = inspect_crop_image(b"test-image")

        self.assertFalse(vision_enabled())
        groq_client.assert_not_called()
        self.assertIn("not sent", result["finding"])

    def test_coordinator_returns_six_structured_findings_and_safety_flags(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": ""}):
            result = coordinate(sample_field())

        self.assertEqual(len(result.findings), 6)
        self.assertTrue(all(finding.evidence for finding in result.findings))
        self.assertEqual(result.priority, "soon")
        self.assertTrue(any("not a live forecast" in flag for flag in result.review_flags))
        self.assertTrue(any("preliminary" in flag for flag in result.review_flags))

    def test_rain_that_offsets_demo_deficit_is_flagged_for_field_review(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": ""}):
            result = coordinate(sample_field(forecast_rain_mm=40))

        irrigation = next(item for item in result.findings if item.agent == "Irrigation agent")
        self.assertEqual(irrigation.calculation["estimated_net_water_m3"], 0.0)
        self.assertTrue(any("forecast rain" in flag for flag in result.review_flags))
        self.assertIn("forecast rain", result.summary)

    def test_report_exports_urdu_and_json_without_photo_bytes(self):
        field = sample_field(image_bytes=b"private-photo-bytes", notes="پتے زرد دکھائی دے رہے ہیں", location="ملتان")
        with patch.dict(os.environ, {"GROQ_API_KEY": ""}):
            result = coordinate(field)
        markdown, json_text = build_report(field, result, "ur")
        data = json.loads(json_text)

        self.assertIn("کھیت کی جانچ", markdown)
        self.assertNotIn("private-photo-bytes", json_text)
        self.assertNotIn("image_bytes", json_text)
        self.assertNotIn("Demo target moisture", markdown + json_text)
        self.assertNotIn("Estimated effective rainfall", markdown + json_text)
        self.assertNotIn("Soil moisture:", markdown + json_text)
        self.assertFalse(any(character.isascii() and character.isalpha() for character in markdown + json_text))
        self.assertEqual(len(data["جانچ"]["ماہرین کی جانچ"]), 6)


if __name__ == "__main__":
    unittest.main()