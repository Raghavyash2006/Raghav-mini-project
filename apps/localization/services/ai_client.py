import json
import logging
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class LocalizationPromptParts:
    role: str
    context: str
    task: str
    constraints: List[str]
    output_format: str


class LocalizationAIClient:
    def __init__(self, api_token: Optional[str] = None, model: Optional[str] = None, timeout: Optional[int] = None):
        self.api_token = api_token or os.getenv("HUGGING_FACE_API_TOKEN", "")
        self.model = model or os.getenv("HUGGING_FACE_MODEL", "HuggingFaceH4/zephyr-7b-beta")
        self.timeout = timeout or int(os.getenv("HUGGING_FACE_TIMEOUT", "45"))

    @property
    def configured(self):
        return bool(self.api_token)

    def build_context_lines(self, payload: Dict[str, object]) -> List[str]:
        return [
            f"source_language: {payload.get('source_language', 'en')}",
            f"target_language: {payload.get('target_language', 'en')}",
            f"target_region: {payload.get('target_region', 'global')}",
            f"tone: {payload.get('tone', 'neutral')}",
            f"audience: {payload.get('audience', 'general')}",
            f"preserve_intent: {payload.get('preserve_intent', True)}",
            f"preserve_sentiment: {payload.get('preserve_sentiment', True)}",
        ]

    def build_prompt_parts(self, payload: Dict[str, object]) -> LocalizationPromptParts:
        tone = str(payload.get("tone", "neutral")).lower()
        tone_guidance = {
            "formal": "Use polished, professional language and keep the wording respectful.",
            "professional": "Use concise business-ready language with clarity and credibility.",
            "casual": "Use natural conversational language without sounding sloppy.",
            "marketing": "Use persuasive, benefit-led language that feels local and culturally relevant.",
            "friendly": "Use warm, approachable wording while staying clear and respectful.",
            "persuasive": "Use motivating language with clear value and a light call to action.",
            "technical": "Use precise, domain-neutral technical language and avoid ambiguity.",
            "empathetic": "Acknowledge user concerns and use reassuring, human-centered wording.",
            "neutral": "Keep the wording clear, accurate, and widely understandable.",
        }.get(tone, "Keep the wording clear, accurate, and widely understandable.")

        audience = str(payload.get("audience", "general")).lower()
        audience_guidance, audience_constraints = self.build_audience_constraints(audience)

        constraints = [
            "Preserve the original meaning and intent.",
            "Preserve sentiment unless doing so would sound unnatural in the target language.",
            "Adapt idioms, cultural references, and examples to fit the target region.",
            "Avoid word-for-word translation when a natural localized equivalent exists.",
            "Return only the localized text with no bullet points or explanation.",
            *audience_constraints,
        ]
        if payload.get("preserve_intent", True):
            constraints.append("Keep the message goal intact.")
        if payload.get("preserve_sentiment", True):
            constraints.append("Keep the emotional tone aligned with the source text.")

        return LocalizationPromptParts(
            role="You are an expert localization assistant.",
            context="\n".join(self.build_context_lines(payload)),
            task="Transform the source text into a localized version for the target language and region.",
            constraints=[tone_guidance, audience_guidance, *constraints],
            output_format="Localized text only.",
        )

    def build_audience_constraints(self, audience: str):
        audience_profiles = {
            "gen z": (
                "Make the phrasing contemporary and concise.",
                [
                    "Prefer energetic, modern wording while staying clear and respectful.",
                    "Use short sentences and avoid overly corporate phrasing.",
                ],
            ),
            "gen-z": (
                "Make the phrasing contemporary and concise.",
                [
                    "Prefer energetic, modern wording while staying clear and respectful.",
                    "Use short sentences and avoid overly corporate phrasing.",
                ],
            ),
            "genz": (
                "Make the phrasing contemporary and concise.",
                [
                    "Prefer energetic, modern wording while staying clear and respectful.",
                    "Use short sentences and avoid overly corporate phrasing.",
                ],
            ),
            "students": (
                "Use accessible, educationally friendly language.",
                [
                    "Prefer straightforward vocabulary and clear transitions.",
                    "Keep explanations easy to follow and avoid jargon where possible.",
                ],
            ),
            "professionals": (
                "Keep the language credible and precise.",
                [
                    "Prefer domain-neutral but professional vocabulary.",
                    "Use concise, structured phrasing suitable for workplace communication.",
                ],
            ),
            "professional": (
                "Keep the language credible and precise.",
                [
                    "Prefer domain-neutral but professional vocabulary.",
                    "Use concise, structured phrasing suitable for workplace communication.",
                ],
            ),
        }

        marketing_profiles = {
            "marketing": (
                "Emphasize value and action.",
                ["Highlight benefits and include clear action-oriented language."],
            ),
            "buyers": (
                "Emphasize value and action.",
                ["Highlight benefits and include clear action-oriented language."],
            ),
            "customers": (
                "Emphasize value and action.",
                ["Highlight benefits and include clear action-oriented language."],
            ),
        }

        if audience in audience_profiles:
            return audience_profiles[audience]
        if audience in marketing_profiles:
            return marketing_profiles[audience]
        return ("Match the phrasing to a general audience.", ["Keep vocabulary simple, natural, and context-appropriate."])

    def build_prompt(self, payload: Dict[str, object]) -> str:
        parts = self.build_prompt_parts(payload)
        source_text = str(payload.get("source_text", "")).strip()
        constraints_block = "\n".join(f"- {constraint}" for constraint in parts.constraints)
        return (
            f"{parts.role}\n\n"
            f"Context:\n{parts.context}\n\n"
            f"Task:\n{parts.task}\n\n"
            f"Source text:\n{source_text}\n\n"
            f"Constraints:\n{constraints_block}\n\n"
            f"Output format:\n{parts.output_format}"
        ).strip()

    def _extract_generated_text(self, response_json: object) -> Optional[str]:
        if isinstance(response_json, list) and response_json:
            first_item = response_json[0]
            if isinstance(first_item, dict):
                return first_item.get("generated_text") or first_item.get("summary_text")
        if isinstance(response_json, dict):
            if response_json.get("generated_text"):
                return response_json["generated_text"]
            if response_json.get("summary_text"):
                return response_json["summary_text"]
            if response_json.get("error"):
                raise RuntimeError(str(response_json["error"]))
        return None

    def _strip_prompt_echo(self, prompt: str, generated_text: str) -> str:
        if generated_text.startswith(prompt):
            generated_text = generated_text[len(prompt):]
        return generated_text.strip().strip('"').strip("`")

    def generate(self, payload: Dict[str, object]) -> Optional[Dict[str, object]]:
        if not self.configured:
            return None

        prompt = self.build_prompt(payload)
        endpoint = f"https://api-inference.huggingface.co/models/{self.model}"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        body = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 256,
                "temperature": 0.3,
                "top_p": 0.9,
                "return_full_text": False,
            },
            "options": {
                "wait_for_model": True,
            },
        }

        try:
            response = requests.post(endpoint, headers=headers, json=body, timeout=self.timeout)
            response.raise_for_status()
            response_json = response.json()
            generated_text = self._extract_generated_text(response_json)
            if not generated_text:
                return None
            localized_text = self._strip_prompt_echo(prompt, generated_text)
            return {
                "localized_text": localized_text,
                "model": self.model,
                "prompt": prompt,
                "raw_response": response_json,
                "explanation": [
                    {"type": "model", "message": "Localized text generated through Hugging Face text generation."},
                    {"type": "context", "message": f"Adapted for {payload.get('target_language', 'en')} in {payload.get('target_region', 'global')} tone {payload.get('tone', 'neutral')}."},
                ],
            }
        except requests.RequestException as exc:
            logger.warning("Hugging Face request failed: %s", exc)
            return None
        except (ValueError, TypeError) as exc:
            logger.warning("Unable to parse Hugging Face response: %s", exc)
            return None