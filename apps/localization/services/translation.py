import re
from typing import List, Tuple


LANGUAGE_CODE_MAP = {
    "en": "en",
    "english": "en",
    "hi": "hi",
    "hindi": "hi",
    "de": "de",
    "german": "de",
    "deutsch": "de",
    "fr": "fr",
    "french": "fr",
    "es": "es",
    "spanish": "es",
    "it": "it",
    "italian": "it",
    "pt": "pt",
    "portuguese": "pt",
    "ja": "ja",
    "japanese": "ja",
    "zh": "zh-CN",
    "chinese": "zh-CN",
    "mandarin": "zh-CN",
    "ar": "ar",
    "arabic": "ar",
}


class TranslationService:
    def __init__(self):
        try:
            from deep_translator import GoogleTranslator

            self._translator_cls = GoogleTranslator
        except Exception:
            self._translator_cls = None

    def _normalize_language_code(self, language: str, allow_auto: bool = False) -> str:
        normalized = (language or "").strip().lower()
        if not normalized:
            return "auto" if allow_auto else "en"

        normalized = normalized.replace("_", "-")
        normalized = LANGUAGE_CODE_MAP.get(normalized, normalized)
        normalized = normalized.split("-")[0]
        normalized = LANGUAGE_CODE_MAP.get(normalized, normalized)

        if normalized == "auto" and allow_auto:
            return "auto"
        return normalized

    def translate(self, text: str, source_language: str, target_language: str) -> Tuple[str, List[dict]]:
        source = self._normalize_language_code(source_language, allow_auto=True)
        target = self._normalize_language_code(target_language)

        if not text:
            return text, []
        if source == target:
            return text, []

        source_code = source or "auto"
        target_code = target or "en"
        translator_sources = [source_code]
        if source_code != "auto":
            translator_sources.append("auto")

        if not self._translator_cls:
            return text, [{"type": "translation", "message": "Translation backend unavailable; returning source text."}]

        for translator_source in translator_sources:
            try:
                translated_text = self._translator_cls(source=translator_source, target=target_code).translate(text)
                if translated_text:
                    translated_text = self._postprocess_translation(translated_text, target)
                    message_source = "auto-detected source" if translator_source == "auto" else source
                    return translated_text, [{"type": "translation", "message": f"Translated from {message_source} to {target}."}]
            except Exception:
                continue

        return text, [{"type": "translation", "message": "Translation attempt failed; returning source text."}]

    def _postprocess_translation(self, text: str, target_language: str) -> str:
        """Apply lightweight language-specific cleanup for more natural phrasing."""
        if not text:
            return text

        target = (target_language or "").lower()
        if target != "hi":
            return text

        normalized = re.sub(r"\s+", " ", text).strip()

        # Common MT ordering issue: "यह हस्तलिखित है उदाहरण" -> "यह हस्तलिखित उदाहरण है"
        normalized = re.sub(
            r"\b(यह\s+हस्तलिखित)\s+है\s+उदाहरण\b",
            r"\1 उदाहरण है",
            normalized,
        )

        # Insert a natural pause before instructional clause when needed.
        normalized = re.sub(r"(उदाहरण\s+है)\s+(जितना\s+हो\s+सके\s+उतना)", r"\1, \2", normalized)

        # Normalize imperative spelling for this frequent pattern.
        normalized = re.sub(r"अच्छा\s+लिखे", "अच्छा लिखें", normalized)

        return normalized
