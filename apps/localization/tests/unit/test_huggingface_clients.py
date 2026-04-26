from unittest.mock import patch

from django.test import SimpleTestCase

from apps.localization.services.ai_client import LocalizationAIClient
from apps.localization.services.cultural import CulturalSensitivityChecker


class DummyResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class HuggingFaceClientTests(SimpleTestCase):
    @patch("apps.localization.services.ai_client.requests.post")
    def test_localization_ai_client_generate_with_mocked_hf_response(self, mocked_post):
        mocked_post.return_value = DummyResponse([
            {"generated_text": "localized output"}
        ])

        client = LocalizationAIClient(api_token="test-token", model="fake-model", timeout=5)
        result = client.generate(
            {
                "source_text": "Hello world",
                "source_language": "en",
                "target_language": "es",
                "target_region": "latam",
                "tone": "formal",
                "audience": "professionals",
                "preserve_intent": True,
                "preserve_sentiment": True,
            }
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["localized_text"], "localized output")
        mocked_post.assert_called_once()

    @patch("apps.localization.services.cultural.requests.post")
    def test_cultural_checker_merges_ai_validation(self, mocked_post):
        mocked_post.return_value = DummyResponse([
            {
                "generated_text": (
                    '[{"term":"guys","validated":true,'
                    '"safer_alternative":"everyone",'
                    '"rationale":"More inclusive wording"}]'
                )
            }
        ])

        checker = CulturalSensitivityChecker(hf_token="test-token", hf_model="fake-model", timeout=5)
        review = checker.check(
            text="Hey guys, this is important.",
            target_region="global",
            target_language="en",
            use_ai_validation=True,
        )

        review_data = review.to_dict()
        self.assertGreaterEqual(len(review_data["flags"]), 1)
        guys_flag = next(item for item in review_data["flags"] if item["term"] == "guys")
        self.assertEqual(guys_flag["source"], "rule-based+ai")
        self.assertEqual(guys_flag["safer_alternative"], "everyone")
