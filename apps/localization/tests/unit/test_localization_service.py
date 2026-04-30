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
    def test_apply_tone_accepts_language_aliases(self):
        engine = LocalizationEngine()

        result, notes = engine.apply_tone("Hola mundo", "casual", target_language="spanish")

        self.assertTrue(result.startswith("Mire,"))
        self.assertEqual(notes[0]["type"], "tone")

    def test_apply_tone_creates_distinct_hindi_outputs(self):
        engine = LocalizationEngine()
        base_text = "आज मौसम बारिश का है और मुझे पिज़्ज़ा खाने की इच्छा है।"

        professional, professional_notes = engine.apply_tone(base_text, "professional", target_language="hi")
        casual, casual_notes = engine.apply_tone(base_text, "casual", target_language="hi")
        marketing, marketing_notes = engine.apply_tone(base_text, "marketing", target_language="hi")

        self.assertTrue(professional.startswith("कृपया ध्यान दें:"))
        self.assertTrue(casual.startswith("देखिए,"))
        self.assertTrue(marketing.startswith("ज़रा सोचिए—"))
        self.assertNotEqual(professional, casual)
        self.assertNotEqual(casual, marketing)
        self.assertNotEqual(professional, marketing)
        self.assertEqual(professional_notes[0]["type"], "tone")
        self.assertEqual(casual_notes[0]["type"], "tone")
        self.assertEqual(marketing_notes[0]["type"], "tone")

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
        self.assertTrue(result["localized_text"].startswith("Tenga en cuenta:"))
        variation_texts = [variation["localized_text"] for variation in result["variations"]]
        self.assertEqual(len(set(variation_texts)), 3)
        self.assertTrue(any(text.startswith("Tenga en cuenta:") for text in variation_texts))
        self.assertTrue(any(text.startswith("Mire,") for text in variation_texts))
        self.assertTrue(any(text.startswith("Piense en esto—") for text in variation_texts))
        self.assertIn("explanation_data", result)
        self.assertIn("idiom_replacements", result["explanation_data"])
        self.assertIn("cultural_adaptations", result["explanation_data"])
        self.assertLessEqual(len(result["explanation"]), 5)
        self.assertTrue(any(item["type"] == "source" for item in result["explanation"]))
        self.assertEqual(result["intent_label"], result["context_analysis"]["intent"])
