import re
from dataclasses import dataclass, field
from typing import List

from .ai_client import LocalizationAIClient
from .context_analysis import ContextAnalysisService
from .cultural import CulturalSensitivityChecker
from .explanation_engine import ExplanationEngine
from .idiom_adapter import IdiomCulturalAdapter
from .translation import TranslationService

DEFAULT_VARIANTS = ["formal", "casual", "marketing"]

FORMAL_REPLACEMENTS = {
    "can't": "cannot",
    "don't": "do not",
    "won't": "will not",
    "it's": "it is",
    "we're": "we are",
}

CASUAL_REPLACEMENTS = {
    "cannot": "can't",
    "do not": "don't",
    "will not": "won't",
    "it is": "it's",
    "we are": "we're",
}

TECHNICAL_REPLACEMENTS = {
    "fix": "resolve",
    "help": "assist",
    "start": "initialize",
    "check": "validate",
}

MARKETING_PREFIXES = [
    "Discover a clearer way to",
    "Experience a smarter way to",
    "Unlock an easier way to",
]

@dataclass
class VariationDraft:
    variant_name: str
    localized_text: str
    explanation: List[dict] = field(default_factory=list)
    cultural_risk_score: float = 0.0

    def to_dict(self):
        return {
            "variant_name": self.variant_name,
            "localized_text": self.localized_text,
            "explanation": self.explanation,
            "cultural_risk_score": self.cultural_risk_score,
        }


class LocalizationEngine:
    def __init__(self):
        self.ai_client = LocalizationAIClient()
        self.context_analyzer = ContextAnalysisService()
        self.cultural_checker = CulturalSensitivityChecker()
        self.explanation_engine = ExplanationEngine()
        self.idiom_adapter = IdiomCulturalAdapter()
        self.translation_service = TranslationService()

    def _text_excerpt(self, text, limit=96):
        excerpt = re.sub(r"\s+", " ", (text or "")).strip()
        if len(excerpt) <= limit:
            return excerpt
        return excerpt[: max(limit - 3, 0)].rstrip() + "..."

    def _build_concise_explanation(
        self,
        source_text,
        source_language,
        target_language,
        target_region,
        tone,
        audience,
        idiom_notes,
        translation_notes,
        tone_notes,
        audience_notes,
        cultural_review,
    ):
        explanation = []
        excerpt = self._text_excerpt(source_text, limit=90)
        source_label = (source_language or "en").lower()
        target_label = (target_language or "en").lower()
        region_label = (target_region or "global").lower()

        explanation.append(
            {
                "type": "intent",
                "message": f"Translated the source text from {source_label} to {target_label} while keeping the original meaning intact.",
            }
        )
        if excerpt:
            explanation.append(
                {
                    "type": "source",
                    "message": f"Used the source text '{excerpt}' as the basis for the localized output.",
                }
            )
        if idiom_notes:
            explanation.append(
                {
                    "type": "idiom",
                    "message": f"Adapted {len(idiom_notes)} idiomatic expression(s) so the wording sounds natural for {region_label}.",
                }
            )

        style_parts = []
        if tone_notes:
            style_parts.append(tone_notes[0].get("message", f"Applied a {tone} tone."))
        if audience_notes:
            style_parts.append(audience_notes[0].get("message", f"Matched the wording to a {audience} audience."))
        if style_parts:
            explanation.append(
                {
                    "type": "style",
                    "message": " ".join(style_parts[:2]),
                }
            )

        review_score = getattr(cultural_review, "score", None)
        score_text = f" (score={review_score:.2f})" if isinstance(review_score, (int, float)) else ""
        explanation.append(
            {
                "type": "quality",
                "message": f"Completed a cultural review for {region_label}{score_text} to keep the output clear and appropriate.",
            }
        )

        if translation_notes and len(explanation) < 5:
            explanation.insert(1, translation_notes[0])

        return explanation[:5]

    def apply_tone(self, text, tone, target_language="en"):
        tone = (tone or "neutral").lower()
        target_language = (target_language or "en").lower()

        if target_language != "en":
            if tone == "neutral":
                return text, [{"type": "tone", "message": "Neutral tone maintained."}]
            return text, [{"type": "tone", "message": f"{tone.title()} tone preference preserved for translated output."}]

        if tone == "formal":
            for source, target in FORMAL_REPLACEMENTS.items():
                text = re.sub(rf"\b{re.escape(source)}\b", target, text, flags=re.IGNORECASE)
            return text, [{"type": "tone", "message": "Formal wording strengthened for professional delivery."}]
        if tone == "professional":
            for source, target in FORMAL_REPLACEMENTS.items():
                text = re.sub(rf"\b{re.escape(source)}\b", target, text, flags=re.IGNORECASE)
            return text, [{"type": "tone", "message": "Professional tone applied with concise business wording."}]
        if tone == "casual":
            for source, target in CASUAL_REPLACEMENTS.items():
                text = re.sub(rf"\b{re.escape(source)}\b", target, text, flags=re.IGNORECASE)
            return text, [{"type": "tone", "message": "Wording relaxed for a conversational read."}]
        if tone == "marketing":
            prefix = MARKETING_PREFIXES[0]
            text = f"{prefix} {text[0].lower() + text[1:] if text else text}" if text else text
            return text, [{"type": "tone", "message": "Marketing framing added to emphasize value and action."}]
        if tone == "friendly":
            text = f"Thanks for checking in - {text}" if text else text
            return text, [{"type": "tone", "message": "Friendly tone applied for warmer communication."}]
        if tone == "persuasive":
            text = f"Don't miss out: {text}" if text else text
            return text, [{"type": "tone", "message": "Persuasive tone applied with stronger call-to-action language."}]
        if tone == "technical":
            for source, target in TECHNICAL_REPLACEMENTS.items():
                text = re.sub(rf"\b{re.escape(source)}\b", target, text, flags=re.IGNORECASE)
            return text, [{"type": "tone", "message": "Technical tone applied with precise terminology."}]
        if tone == "empathetic":
            text = f"We understand your concern, and {text[0].lower() + text[1:] if text else text}" if text else text
            return text, [{"type": "tone", "message": "Empathetic tone applied to acknowledge user concerns."}]
        return text, [{"type": "tone", "message": "Neutral tone maintained."}]

    def audience_adaptation(self, text, audience, target_language="en"):
        audience = (audience or "general").lower()
        target_language = (target_language or "en").lower()
        notes = []
        if target_language != "en":
            return text, [{"type": "audience", "message": "Audience preference retained for translated output."}]

        if audience in {"gen z", "gen-z", "genz"}:
            replacements = {
                "very": "super",
                "important": "key",
                "difficult": "tricky",
                "excellent": "awesome",
            }
            for source, target in replacements.items():
                text = re.sub(rf"\b{re.escape(source)}\b", target, text, flags=re.IGNORECASE)
            notes.append({"type": "audience", "message": "Contemporary, concise wording selected for Gen Z audiences."})
        elif audience in {"students", "student"}:
            replacements = {
                "utilize": "use",
                "commence": "start",
                "therefore": "so",
                "approximately": "about",
            }
            for source, target in replacements.items():
                text = re.sub(rf"\b{re.escape(source)}\b", target, text, flags=re.IGNORECASE)
            notes.append({"type": "audience", "message": "Accessible, learning-friendly phrasing selected for students."})
        elif audience in {"professionals", "professional"}:
            replacements = {
                "lots of": "numerous",
                "a lot of": "many",
                "get": "obtain",
                "fix": "resolve",
            }
            for source, target in replacements.items():
                text = re.sub(rf"\b{re.escape(source)}\b", target, text, flags=re.IGNORECASE)
            notes.append({"type": "audience", "message": "Professional audience framing kept precise and credible."})
        elif audience in {"marketing", "buyers", "customers"}:
            notes.append({"type": "audience", "message": "Benefit-led phrasing emphasized for conversion-focused readers."})
        else:
            notes.append({"type": "audience", "message": "General audience wording retained."})
        return text, notes

    def generate_variants(self, text, variation_types, target_region, target_language, source_text="", source_language="en"):
        variants = []
        prior_variant_texts = []
        source_language = (source_language or "en").lower()
        target_language = (target_language or "en").lower()

        for variant_name in variation_types:
            localized_text = text
            explanation = []

            if source_text and source_language == "en" and target_language != "en":
                toned_source, tone_notes = self.apply_tone(source_text, variant_name, target_language="en")
                localized_text, translation_notes = self.translation_service.translate(
                    toned_source,
                    source_language=source_language,
                    target_language=target_language,
                )
                explanation.extend(tone_notes)
                explanation.extend(translation_notes)
            else:
                localized_text, tone_notes = self.apply_tone(localized_text, variant_name, target_language=target_language)
                explanation.extend(tone_notes)

            localized_text, diversity_note = self._ensure_meaningful_difference(
                variant_name=variant_name,
                variant_text=localized_text,
                base_text=text,
                prior_texts=prior_variant_texts,
                target_language=target_language,
            )
            if diversity_note:
                explanation.append({"type": "diversity", "message": diversity_note})

            review = self.cultural_checker.check(
                localized_text,
                target_region=target_region,
                target_language=target_language,
                use_ai_validation=True,
            )
            explanation.append({"type": "cultural", "message": "Cultural review completed for the target region."})
            variants.append(
                VariationDraft(
                    variant_name=variant_name,
                    localized_text=localized_text,
                    explanation=explanation,
                    cultural_risk_score=review.score,
                )
            )
            prior_variant_texts.append(localized_text)
        return variants

    def _jaccard_similarity(self, left, right):
        left_tokens = set(re.findall(r"\w+", (left or "").lower()))
        right_tokens = set(re.findall(r"\w+", (right or "").lower()))
        if not left_tokens or not right_tokens:
            return 0.0
        intersection = len(left_tokens & right_tokens)
        union = len(left_tokens | right_tokens)
        return intersection / union if union else 0.0

    def _inject_tone_signature(self, variant_name, text, target_language="en"):
        if (target_language or "en").lower() != "en":
            return text

        signatures = {
            "formal": "Please note that",
            "casual": "Quick heads-up:",
            "marketing": "Act now to",
        }
        signature = signatures.get(variant_name)
        if not signature or not text:
            return text

        if variant_name == "marketing" and text.lower().startswith("act now to"):
            return text
        if text.lower().startswith(signature.lower()):
            return text
        return f"{signature} {text[0].lower() + text[1:] if len(text) > 1 else text.lower()}"

    def _ensure_meaningful_difference(self, variant_name, variant_text, base_text, prior_texts, target_language="en"):
        reference_texts = [base_text, *prior_texts]
        max_similarity = max((self._jaccard_similarity(variant_text, ref) for ref in reference_texts if ref), default=0.0)
        if max_similarity < 0.88:
            return variant_text, ""

        adjusted_text = self._inject_tone_signature(variant_name, variant_text, target_language=target_language)
        adjusted_similarity = max((self._jaccard_similarity(adjusted_text, ref) for ref in reference_texts if ref), default=0.0)
        if adjusted_similarity < max_similarity:
            return adjusted_text, f"Adjusted {variant_name} wording to increase stylistic separation from other outputs."
        return variant_text, ""

    def _build_variation_map(self, variation_items):
        return {
            "formal": next((item["localized_text"] for item in variation_items if item.get("variant_name") == "formal"), ""),
            "casual": next((item["localized_text"] for item in variation_items if item.get("variant_name") == "casual"), ""),
            "marketing": next((item["localized_text"] for item in variation_items if item.get("variant_name") == "marketing"), ""),
        }

    def localize(self, payload):
        source_text = payload["source_text"].strip()
        source_language = payload.get("source_language", "en")
        target_language = payload.get("target_language", "en")
        target_region = payload.get("target_region", "global")
        tone = payload.get("tone", "neutral")
        audience = payload.get("audience", "general")
        variation_types = payload.get("variation_types") or DEFAULT_VARIANTS
        context_analysis = self.context_analyzer.analyze(source_text)

        idiom_adaptation = self.idiom_adapter.adapt(
            text=source_text,
            target_language=target_language,
            target_region=target_region,
            use_ai_assist=True,
        )
        idiom_notes = [
            {
                "type": "idiom",
                "original": match["original"],
                "replacement": match["replacement"],
                "strategy": match["strategy"],
                "message": "Culturally adapted idiomatic expression while preserving semantic meaning.",
            }
            for match in idiom_adaptation.get("matches", [])
        ]
        idiom_adapted_text = idiom_adaptation.get("adapted_text", source_text)

        translated_text = idiom_adapted_text
        translation_notes = []
        if source_language != target_language:
            translated_text, translation_notes = self.translation_service.translate(
                text=idiom_adapted_text,
                source_language=source_language,
                target_language=target_language,
            )

        adapted_text = translated_text
        adapted_text, tone_notes = self.apply_tone(adapted_text, tone, target_language=target_language)
        adapted_text, audience_notes = self.audience_adaptation(adapted_text, audience, target_language=target_language)
        cultural_review = self.cultural_checker.check(
            adapted_text,
            target_region=target_region,
            target_language=target_language,
            use_ai_validation=True,
        )
        variants = self.generate_variants(
            adapted_text,
            variation_types,
            target_region,
            target_language,
            source_text=idiom_adapted_text,
            source_language=source_language,
        )

        explanation = self._build_concise_explanation(
            source_text=source_text,
            source_language=source_language,
            target_language=target_language,
            target_region=target_region,
            tone=tone,
            audience=audience,
            idiom_notes=idiom_notes,
            translation_notes=translation_notes,
            tone_notes=tone_notes,
            audience_notes=audience_notes,
            cultural_review=cultural_review,
        )

        return {
            "localized_text": adapted_text,
            "variations": [variant.to_dict() for variant in variants],
            "variation_map": self._build_variation_map([variant.to_dict() for variant in variants]),
            "explanation": explanation,
            "cultural_review": cultural_review.to_dict(),
            "explanation_data": self.explanation_engine.build(
                selected_tone=tone,
                target_region=target_region,
                idiom_adaptation=idiom_adaptation,
                cultural_review=cultural_review.to_dict(),
                base_explanation=explanation,
                variations=[variant.to_dict() for variant in variants],
            ),
            "context_analysis": context_analysis,
            "idiom_adaptation": idiom_adaptation,
            "sentiment_label": context_analysis["sentiment"],
            "sentiment_score": context_analysis["sentiment_score"],
            "intent_label": context_analysis["intent"],
            "intent_preserved": bool(payload.get("preserve_intent", True)),
            "sentiment_preserved": bool(payload.get("preserve_sentiment", True)),
        }

    def _normalize_ai_payload(self, ai_payload, payload, context_analysis, idiom_adaptation):
        target_region = payload.get("target_region", "global")
        target_language = payload.get("target_language", "en")
        variation_types = payload.get("variation_types") or DEFAULT_VARIANTS
        localized_text = ai_payload.get("localized_text", payload["source_text"])
        cultural_review = ai_payload.get("cultural_review") or self.cultural_checker.check(
            localized_text,
            target_region=target_region,
            target_language=target_language,
            use_ai_validation=True,
        ).to_dict()
        variations = ai_payload.get("variations") or []

        normalized_variations = []
        if isinstance(variations, dict):
            for variant_name, localized_text in variations.items():
                normalized_variations.append({
                    "variant_name": variant_name,
                    "localized_text": localized_text,
                    "explanation": [{"type": "ai", "message": f"Generated by AI for {variant_name} tone."}],
                    "cultural_risk_score": cultural_review.get("score", 0),
                })
        else:
            for variant_name in variation_types:
                match = next((item for item in variations if item.get("variant_name") == variant_name), None)
                if match:
                    normalized_variations.append(match)

        if not normalized_variations:
            normalized_variations = self.generate_variants(localized_text, variation_types, target_region, target_language)
            normalized_variations = [variant.to_dict() for variant in normalized_variations]

        # Guarantee variant separation even when upstream AI returns near-identical strings.
        adjusted_variations = []
        prior_variant_texts = []
        for item in normalized_variations:
            adjusted_text, diversity_note = self._ensure_meaningful_difference(
                variant_name=item.get("variant_name", "neutral"),
                variant_text=item.get("localized_text", ""),
                base_text=localized_text,
                prior_texts=prior_variant_texts,
                target_language=target_language,
            )
            updated_item = {
                **item,
                "localized_text": adjusted_text,
                "explanation": item.get("explanation", []),
            }
            if diversity_note:
                updated_item["explanation"] = [
                    *updated_item["explanation"],
                    {"type": "diversity", "message": diversity_note},
                ]
            adjusted_variations.append(updated_item)
            prior_variant_texts.append(adjusted_text)

        return {
            "localized_text": localized_text,
            "variations": adjusted_variations,
            "variation_map": self._build_variation_map(adjusted_variations),
            "explanation": [
                *[
                    {
                        "type": "idiom",
                        "original": match["original"],
                        "replacement": match["replacement"],
                        "strategy": match["strategy"],
                        "message": "Culturally adapted idiomatic expression while preserving semantic meaning.",
                    }
                    for match in idiom_adaptation.get("matches", [])
                ],
                *(ai_payload.get("explanation") or [
                    {"type": "ai", "message": "Localized text generated by Hugging Face and validated with cultural checks."}
                ]),
            ],
            "cultural_review": cultural_review,
            "explanation_data": ai_payload.get("explanation_data") or self.explanation_engine.build(
                selected_tone=payload.get("tone", "neutral"),
                target_region=target_region,
                idiom_adaptation=idiom_adaptation,
                cultural_review=cultural_review,
                base_explanation=ai_payload.get("explanation") or [],
                variations=adjusted_variations,
            ),
            "context_analysis": ai_payload.get("context_analysis") or context_analysis,
            "idiom_adaptation": ai_payload.get("idiom_adaptation") or idiom_adaptation,
            "sentiment_label": ai_payload.get("sentiment_label") or context_analysis["sentiment"],
            "sentiment_score": ai_payload.get("sentiment_score") or context_analysis["sentiment_score"],
            "intent_label": ai_payload.get("intent_label") or context_analysis["intent"],
            "intent_preserved": ai_payload.get("intent_preserved", True),
            "sentiment_preserved": ai_payload.get("sentiment_preserved", True),
        }
