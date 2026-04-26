from unittest.mock import patch

from django.test import SimpleTestCase

from apps.localization.services.localization import LocalizationEngine


class DummyReview:
    def __init__(self, score=0.9):
        self.score = score

    def to_dict(self):
        return {
            "score": self.score,
            "flags": [],
            "recommendations": ["Keep wording globally understandable."],
            "ai_validation": [],
        }


class LocalizationEngineTests(SimpleTestCase):
    @patch("apps.localization.services.localization.LocalizationAIClient.generate")
    @patch("apps.localization.services.localization.IdiomCulturalAdapter.adapt")
    @patch("apps.localization.services.localization.CulturalSensitivityChecker.check")
    @patch("apps.localization.services.localization.TranslationService.translate")
    def test_localize_returns_structured_variations_and_explanation(
        self,
        mocked_translate,
        mocked_cultural_check,
        mocked_idiom_adapt,
        mocked_ai_generate,
    ):
        mocked_ai_generate.return_value = None
        mocked_translate.return_value = (
            "Mantente alerta para recibir actualizaciones.",
            [{"type": "translation", "message": "Translated from en to es."}],
        )
        mocked_idiom_adapt.return_value = {
            "adapted_text": "Please start quickly with momentum and share updates.",
            "matches": [
                {
                    "original": "hit the ground running",
                    "replacement": "start quickly with momentum",
                    "strategy": "rule-based",
                }
            ],
        }
        mocked_cultural_check.return_value = DummyReview(score=0.8)

        engine = LocalizationEngine()
        result = engine.localize(
            {
                "source_text": "Hit the ground running and share updates.",
                "source_language": "en",
                "target_language": "es",
                "target_region": "latam",
                "tone": "formal",
                "audience": "professionals",
                "variation_types": ["formal", "casual", "marketing"],
                "preserve_intent": True,
                "preserve_sentiment": True,
            }
        )

        self.assertIn("localized_text", result)
        self.assertIn("variations", result)
        self.assertEqual(len(result["variations"]), 3)
        self.assertSetEqual(set(result["variation_map"].keys()), {"formal", "casual", "marketing"})
        self.assertIn("explanation_data", result)
        self.assertIn("idiom_replacements", result["explanation_data"])
        self.assertIn("cultural_adaptations", result["explanation_data"])
        self.assertLessEqual(len(result["explanation"]), 5)
        self.assertTrue(any(item["type"] == "source" for item in result["explanation"]))
        self.assertEqual(result["intent_label"], result["context_analysis"]["intent"])
