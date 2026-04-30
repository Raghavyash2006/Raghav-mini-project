from django.test import SimpleTestCase

from apps.localization.services.translation import TranslationService


class SmokeTranslationTests(SimpleTestCase):
    def test_translate_not_empty_with_fake_translator(self):
        class FakeTranslator:
            def __init__(self, source, target):
                self.source = source
                self.target = target

            def translate(self, text):
                return "Translated: " + text

        service = TranslationService()
        service._translator_cls = FakeTranslator

        result, notes = service.translate("Hello", "en", "es")

        self.assertTrue(result)
        self.assertIn("Translated", result)
