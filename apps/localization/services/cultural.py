import logging
import os
import re
from dataclasses import asdict, dataclass, field

import requests

logger = logging.getLogger(__name__)


PHRASE_RULES = {
    "crazy": {
        "message": "Potentially insensitive mental health wording.",
        "safer_alternative": "unexpected",
        "severity": "medium",
    },
    "insane": {
        "message": "Potentially insensitive mental health wording.",
        "safer_alternative": "extreme",
        "severity": "medium",
    },
    "guys": {
        "message": "Potentially non-inclusive collective reference.",
        "safer_alternative": "everyone",
        "severity": "low",
    },
    "blindly": {
        "message": "Potentially ableist expression.",
        "safer_alternative": "without verification",
        "severity": "medium",
    },
    "kill two birds with one stone": {
        "message": "May be perceived as violent phrasing in some contexts.",
        "safer_alternative": "solve two problems at once",
        "severity": "low",
    },
    "manpower": {
        "message": "Potentially gendered workplace language.",
        "safer_alternative": "workforce",
        "severity": "low",
    },
    "blacklist": {
        "message": "Potentially exclusionary terminology.",
        "safer_alternative": "blocklist",
        "severity": "medium",
    },
    "whitelist": {
        "message": "Potentially exclusionary terminology.",
        "safer_alternative": "allowlist",
        "severity": "medium",
    },
}

REGIONAL_NOTES = {
    "latam": ["Use LATAM-friendly vocabulary and avoid Spain-specific colloquialisms."],
    "es-es": ["Prefer Spain-standard phrasing and regional spelling."],
    "global": ["Keep wording widely understandable across regions."],
}


@dataclass
class CulturalReview:
    score: float
    flags: list
    recommendations: list
    ai_validation: list = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


class CulturalSensitivityChecker:
    def __init__(self, hf_token=None, hf_model=None, timeout=15):
        self.hf_token = hf_token or os.getenv("HUGGING_FACE_API_TOKEN", "")
        self.hf_model = hf_model or os.getenv("HUGGING_FACE_MODEL", "HuggingFaceH4/zephyr-7b-beta")
        self.timeout = timeout

    @property
    def ai_enabled(self):
        return bool(self.hf_token)

    def _rule_based_flags(self, text):
        lowered = (text or "").lower()
        flags = []
        recommendations = []

        for phrase, rule in PHRASE_RULES.items():
            if re.search(rf"\b{re.escape(phrase)}\b", lowered):
                flags.append(
                    {
                        "term": phrase,
                        "message": rule["message"],
                        "safer_alternative": rule["safer_alternative"],
                        "severity": rule["severity"],
                        "source": "rule-based",
                    }
                )
                recommendations.append(f"Replace '{phrase}' with '{rule['safer_alternative']}'.")

        return flags, recommendations

    def _ai_validate(self, text, target_region, target_language, flags):
        if not self.ai_enabled or not flags:
            return []

        prompt = (
            "You are a cultural sensitivity reviewer for localization. "
            "Validate flagged phrases and suggest safer alternatives. "
            "Return compact JSON array only with keys: term, validated, safer_alternative, rationale.\n"
            f"target_language={target_language}\n"
            f"target_region={target_region}\n"
            f"text={text}\n"
            f"flags={flags}"
        )
        endpoint = f"https://api-inference.huggingface.co/models/{self.hf_model}"
        headers = {
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json",
        }
        body = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 220,
                "temperature": 0.1,
                "return_full_text": False,
            },
            "options": {"wait_for_model": True},
        }

        try:
            response = requests.post(endpoint, headers=headers, json=body, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
            if isinstance(payload, list) and payload and isinstance(payload[0], dict):
                text_out = payload[0].get("generated_text", "").strip()
                # Best-effort JSON extraction.
                match = re.search(r"\[[\s\S]*\]", text_out)
                if match:
                    import json

                    return json.loads(match.group(0))
        except requests.RequestException as exc:
            logger.warning("Cultural AI validation failed: %s", exc)
        except Exception as exc:
            logger.warning("Cultural AI response parsing failed: %s", exc)
        return []

    def _merge_ai_validation(self, flags, ai_validation):
        if not ai_validation:
            return flags

        merged = []
        for flag in flags:
            ai_match = next((item for item in ai_validation if item.get("term", "").lower() == flag.get("term", "").lower()), None)
            if ai_match:
                merged.append(
                    {
                        **flag,
                        "validated": bool(ai_match.get("validated", True)),
                        "safer_alternative": ai_match.get("safer_alternative") or flag.get("safer_alternative"),
                        "ai_rationale": ai_match.get("rationale", ""),
                        "source": "rule-based+ai",
                    }
                )
            else:
                merged.append(flag)
        return merged

    def check(self, text, target_region="global", target_language="en", use_ai_validation=True):
        flags, recommendations = self._rule_based_flags(text)
        recommendations.extend(REGIONAL_NOTES.get(target_region.lower(), REGIONAL_NOTES["global"]))

        ai_validation = []
        if use_ai_validation:
            ai_validation = self._ai_validate(text, target_region, target_language, flags)
            flags = self._merge_ai_validation(flags, ai_validation)

        recommendations.extend(
            [
                f"Prefer '{flag.get('safer_alternative')}' instead of '{flag.get('term')}'."
                for flag in flags
                if flag.get("safer_alternative")
            ]
        )

        base_score = 1.0 - min(len(flags) * 0.2, 0.8)
        severe_penalty = 0.1 * sum(1 for flag in flags if flag.get("severity") == "medium")
        score = round(max(base_score - severe_penalty, 0.1), 2)
        return CulturalReview(score=score, flags=flags, recommendations=recommendations, ai_validation=ai_validation)
