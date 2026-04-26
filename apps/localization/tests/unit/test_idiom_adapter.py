from django.test import SimpleTestCase

from apps.localization.services.idiom_adapter import IdiomCulturalAdapter


class IdiomAdapterTests(SimpleTestCase):
    def test_piece_of_cake_with_victory_context_maps_to_easy_win(self):
        adapter = IdiomCulturalAdapter()
        result = adapter.adapt(
            text="Today victory was a piece of cake for me.",
            target_language="en",
            target_region="global",
            use_ai_assist=False,
        )

        self.assertIn("easy win", result["adapted_text"].lower())
        self.assertEqual(result["matches"][0]["replacement"], "an easy win")

    def test_under_the_weather_is_adapted(self):
        adapter = IdiomCulturalAdapter()
        result = adapter.adapt(
            text="I am under the weather today.",
            target_language="en",
            target_region="global",
            use_ai_assist=False,
        )

        self.assertIn("feeling unwell", result["adapted_text"].lower())
