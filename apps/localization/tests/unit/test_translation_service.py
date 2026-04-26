from django.test import SimpleTestCase

from apps.localization.services.translation import TranslationService


class TranslationServiceTests(SimpleTestCase):
    def test_translate_normalizes_language_aliases(self):
        class FakeTranslator:
            calls = []

            def __init__(self, source, target):
                self.source = source
                self.target = target

            def translate(self, text):
                FakeTranslator.calls.append((self.source, self.target, text))
                return "Hola mundo"

        service = TranslationService()
        service._translator_cls = FakeTranslator

        result, notes = service.translate("Hello world", "english", "spanish")

        self.assertEqual(result, "Hola mundo")
        self.assertEqual(notes[0]["message"], "Translated from en to es.")
        self.assertEqual(FakeTranslator.calls[0][:2], ("en", "es"))

    def test_translate_retries_with_auto_source(self):
        class FallbackTranslator:
            calls = []

            def __init__(self, source, target):
                self.source = source
                self.target = target

            def translate(self, text):
                FallbackTranslator.calls.append((self.source, self.target, text))
                if self.source != "auto":
                    raise RuntimeError("source mapping failed")
                return "Hello"

        service = TranslationService()
        service._translator_cls = FallbackTranslator

        result, notes = service.translate("Bonjour", "fr", "en")

        self.assertEqual(result, "Hello")
        self.assertEqual(notes[0]["message"], "Translated from auto-detected source to en.")
        self.assertEqual([call[0] for call in FallbackTranslator.calls], ["fr", "auto"])

    def test_hindi_postprocess_improves_sentence_flow(self):
        service = TranslationService()

        input_text = "यह हस्तलिखित है उदाहरण जितना हो सके उतना अच्छा लिखे।"
        result = service._postprocess_translation(input_text, "hi")

        self.assertEqual(result, "यह हस्तलिखित उदाहरण है, जितना हो सके उतना अच्छा लिखें।")

    def test_postprocess_keeps_non_hindi_unchanged(self):
        service = TranslationService()

        input_text = "This is already clear."
        result = service._postprocess_translation(input_text, "en")

        self.assertEqual(result, input_text)
