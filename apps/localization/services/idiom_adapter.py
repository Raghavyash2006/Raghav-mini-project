import logging
import os
import re
from dataclasses import asdict, dataclass, field

import requests

logger = logging.getLogger(__name__)


@dataclass
class IdiomEntry:
    phrase: str
    default_replacement: str
    regional_replacements: dict = field(default_factory=dict)


@dataclass
class IdiomMatch:
    original: str
    replacement: str
    strategy: str
    region: str
    target_language: str

    def to_dict(self):
        return asdict(self)


@dataclass
class IdiomAdaptationResult:
    adapted_text: str
    matches: list

    def to_dict(self):
        return {
            "adapted_text": self.adapted_text,
            "matches": [match.to_dict() for match in self.matches],
        }


class IdiomDictionary:
    def __init__(self, entries=None):
        self._entries = {}
        for entry in entries or self.default_entries():
            self.register(entry)

    @staticmethod
    def default_entries():
        return [
            IdiomEntry(
                phrase="break the ice",
                default_replacement="start the conversation naturally",
                regional_replacements={
                    "latam": "iniciar la conversacion con cercania",
                    "es-es": "romper la barrera inicial",
                },
            ),
            IdiomEntry(
                phrase="hit the ground running",
                default_replacement="start quickly with momentum",
                regional_replacements={
                    "latam": "arrancar con ritmo desde el inicio",
                    "es-es": "empezar con ritmo desde el primer momento",
                },
            ),
            IdiomEntry(
                phrase="think outside the box",
                default_replacement="approach it creatively",
                regional_replacements={
                    "latam": "pensar de forma creativa",
                    "es-es": "buscar un enfoque creativo",
                },
            ),
            IdiomEntry(
                phrase="keep your eyes peeled",
                default_replacement="stay alert",
                regional_replacements={
                    "latam": "mantente atento",
                    "es-es": "permanece atento",
                },
            ),
            IdiomEntry(
                phrase="ballpark figure",
                default_replacement="rough estimate",
                regional_replacements={
                    "latam": "estimacion aproximada",
                    "es-es": "estimacion orientativa",
                },
            ),
            IdiomEntry(
                phrase="piece of cake",
                default_replacement="very easy",
                regional_replacements={
                    "latam": "muy facil",
                    "es-es": "muy facil",
                },
            ),
            IdiomEntry(
                phrase="under the weather",
                default_replacement="feeling unwell",
                regional_replacements={
                    "latam": "sintiendose mal",
                    "es-es": "encontrandose mal",
                },
            ),
            IdiomEntry(
                phrase="hit the sack",
                default_replacement="go to sleep",
                regional_replacements={
                    "latam": "irse a dormir",
                    "es-es": "irse a dormir",
                },
            ),
            IdiomEntry(
                phrase="once in a blue moon",
                default_replacement="very rarely",
                regional_replacements={
                    "latam": "muy rara vez",
                    "es-es": "muy rara vez",
                },
            ),
            IdiomEntry(
                phrase="spill the beans",
                default_replacement="reveal the secret",
                regional_replacements={
                    "latam": "revelar el secreto",
                    "es-es": "desvelar el secreto",
                },
            ),
        ]

    def register(self, entry):
        self._entries[entry.phrase.lower()] = entry

    def get(self, phrase):
        return self._entries.get((phrase or "").lower())

    def all(self):
        return list(self._entries.values())


class IdiomCulturalAdapter:
    def __init__(self, dictionary=None, hf_token=None, hf_model=None, timeout=20):
        self.dictionary = dictionary or IdiomDictionary()
        self.hf_token = hf_token or os.getenv("HUGGING_FACE_API_TOKEN", "")
        self.hf_model = hf_model or os.getenv("HUGGING_FACE_MODEL", "HuggingFaceH4/zephyr-7b-beta")
        self.timeout = timeout

    @property
    def ai_configured(self):
        return bool(self.hf_token)

    def find_matches(self, text):
        matches = []
        if not text:
            return matches

        for entry in self.dictionary.all():
            pattern = re.compile(rf"\b{re.escape(entry.phrase)}\b", re.IGNORECASE)
            for match in pattern.finditer(text):
                matches.append((entry, match.group(0), match.start(), match.end()))
        matches.sort(key=lambda item: item[2])
        return matches

    def _rule_replacement(self, entry, target_region):
        region_key = (target_region or "").lower()
        return entry.regional_replacements.get(region_key) or entry.default_replacement

    def _contextual_replacement(self, entry, full_text, original_replacement):
        phrase = (entry.phrase or "").lower()
        if phrase not in {"piece of cake", "break the ice"}:
            return original_replacement

        context_text = (full_text or "").lower()
        if phrase == "piece of cake" and re.search(r"\b(victory|win|won|winning|defeat|beat)\b", context_text):
            return "an easy win"
        if phrase == "break the ice" and re.search(r"\b(meeting|intro|introduction|team|client|conversation)\b", context_text):
            return "start the conversation comfortably"
        return original_replacement

    def _ai_suggest_replacement(self, idiom, sentence, target_language, target_region):
        if not self.ai_configured:
            return None

        prompt = (
            "Rewrite only the idiomatic expression below with a culturally natural equivalent while preserving meaning. "
            "Return only the replacement phrase.\n"
            f"target_language={target_language}\n"
            f"target_region={target_region}\n"
            f"idiom={idiom}\n"
            f"sentence={sentence}"
        )
        endpoint = f"https://api-inference.huggingface.co/models/{self.hf_model}"
        headers = {
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json",
        }
        body = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 40,
                "temperature": 0.2,
                "return_full_text": False,
            },
            "options": {"wait_for_model": True},
        }

        try:
            response = requests.post(endpoint, headers=headers, json=body, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
            if isinstance(payload, list) and payload and isinstance(payload[0], dict):
                generated = payload[0].get("generated_text", "").strip()
                if generated:
                    return generated.strip('"').strip("`")
        except requests.RequestException as exc:
            logger.warning("Idiom AI assist failed: %s", exc)
        except (TypeError, ValueError):
            logger.warning("Idiom AI assist response parsing failed")
        return None

    def adapt(self, text, target_language="en", target_region="global", use_ai_assist=True):
        matches = self.find_matches(text)
        if not matches:
            return IdiomAdaptationResult(adapted_text=text, matches=[]).to_dict()

        adapted_text = text
        notes = []

        # Replace from the end of the string to keep indexes stable.
        for entry, original, start, end in sorted(matches, key=lambda item: item[2], reverse=True):
            replacement = self._rule_replacement(entry, target_region)
            replacement = self._contextual_replacement(entry, text, replacement)
            strategy = "rule-based"
            if use_ai_assist:
                ai_replacement = self._ai_suggest_replacement(entry.phrase, text, target_language, target_region)
                if ai_replacement:
                    replacement = ai_replacement
                    strategy = "ai-assisted"

            adapted_text = f"{adapted_text[:start]}{replacement}{adapted_text[end:]}"
            adapted_text = re.sub(r"\ba\s+an\s+", "an ", adapted_text, flags=re.IGNORECASE)
            notes.append(
                IdiomMatch(
                    original=original,
                    replacement=replacement,
                    strategy=strategy,
                    region=(target_region or "global"),
                    target_language=(target_language or "en"),
                )
            )

        notes.reverse()
        return IdiomAdaptationResult(adapted_text=adapted_text, matches=notes).to_dict()
