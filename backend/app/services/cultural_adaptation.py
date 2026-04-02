from typing import Dict

CULTURAL_MAP: Dict[str, Dict[str, str]] = {
    "en->es": {
        "break a leg": "¡mucha mierda!",
        "time is money": "el tiempo es oro",
    },
    "en->fr": {
        "break a leg": "m... (tronche)?",  # placeholder
    },
}


def adapt_cultural_references(text: str, source_language: str, target_language: str) -> str:
    key = f"{source_language}->{target_language}"
    overrides = CULTURAL_MAP.get(key, {})
    normalized = text
    for phrase, replacement in overrides.items():
        normalized = normalized.replace(phrase, replacement)
    return normalized
