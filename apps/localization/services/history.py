import hashlib

from django.db import transaction
from django.db.models import Max

from ..models import Feedback, LocalizationJob, LocalizationVariation


class HistoryService:
    def _build_version_group_key(self, payload, user=None):
        user_key = str(getattr(user, "pk", "") or payload.get("user_id", "") or "").strip().lower()
        raw = "|".join(
            [
                user_key,
                (payload.get("source_text") or "").strip().lower(),
                str(payload.get("source_language", "en")).lower(),
                str(payload.get("target_language", "en")).lower(),
                str(payload.get("target_region", "global")).lower(),
                str(payload.get("audience", "general")).lower(),
            ]
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _next_version_number(self, version_group_key):
        max_version = LocalizationJob.objects.filter(version_group_key=version_group_key).aggregate(max_version=Max("version_number"))["max_version"]
        return (max_version or 0) + 1

    @transaction.atomic
    def save_result(self, payload, result, ocr_text="", user=None):
        version_group_key = self._build_version_group_key(payload, user=user)
        version_number = self._next_version_number(version_group_key)

        job = LocalizationJob.objects.create(
            user=user,
            version_group_key=version_group_key,
            version_number=version_number,
            source_text=payload["source_text"],
            source_language=payload.get("source_language", "en"),
            target_language=payload.get("target_language", "en"),
            target_region=payload.get("target_region", "global"),
            tone=payload.get("tone", "neutral"),
            audience=payload.get("audience", "general"),
            preserve_intent=payload.get("preserve_intent", True),
            preserve_sentiment=payload.get("preserve_sentiment", True),
            use_ocr=payload.get("use_ocr", True),
            ocr_text=ocr_text,
            sentiment_label=result.get("sentiment_label", ""),
            sentiment_score=result.get("sentiment_score", 0),
            cultural_risk_score=result.get("cultural_review", {}).get("score", 0),
            explanation=result.get("explanation", []),
            metadata={
                "localized_text": result.get("localized_text", ""),
                "variation_count": len(result.get("variations", [])),
                "variation_map": result.get("variation_map", {}),
                "explanation_data": result.get("explanation_data", {}),
                "intent_preserved": result.get("intent_preserved", True),
                "sentiment_preserved": result.get("sentiment_preserved", True),
                "intent_label": result.get("intent_label", "informative"),
                "context_analysis": result.get("context_analysis", {}),
                "idiom_adaptation": result.get("idiom_adaptation", {}),
            },
        )

        for variation in result.get("variations", []):
            LocalizationVariation.objects.create(
                job=job,
                variant_name=variation["variant_name"],
                localized_text=variation["localized_text"],
                explanation=variation.get("explanation", []),
                cultural_risk_score=variation.get("cultural_risk_score", 0),
            )
        return job

    def list_versions(self, job):
        return LocalizationJob.objects.filter(version_group_key=job.version_group_key).prefetch_related("variations").order_by("version_number", "created_at")

    def compare_jobs(self, left_job, right_job):
        left_variation_map = left_job.metadata.get("variation_map", {})
        right_variation_map = right_job.metadata.get("variation_map", {})

        def _variation_change(key):
            left_text = left_variation_map.get(key, "")
            right_text = right_variation_map.get(key, "")
            return {
                "left": left_text,
                "right": right_text,
                "changed": left_text != right_text,
            }

        return {
            "left": {
                "id": str(left_job.id),
                "version_number": left_job.version_number,
                "created_at": left_job.created_at,
                "input": left_job.source_text,
                "output": left_job.metadata.get("localized_text", ""),
            },
            "right": {
                "id": str(right_job.id),
                "version_number": right_job.version_number,
                "created_at": right_job.created_at,
                "input": right_job.source_text,
                "output": right_job.metadata.get("localized_text", ""),
            },
            "changes": {
                "input_changed": left_job.source_text != right_job.source_text,
                "output_changed": left_job.metadata.get("localized_text", "") != right_job.metadata.get("localized_text", ""),
                "tone_changed": left_job.tone != right_job.tone,
                "audience_changed": left_job.audience != right_job.audience,
                "sentiment_score_delta": round(float(right_job.sentiment_score) - float(left_job.sentiment_score), 2),
                "cultural_risk_score_delta": round(float(right_job.cultural_risk_score) - float(left_job.cultural_risk_score), 2),
                "variation_changes": {
                    "formal": _variation_change("formal"),
                    "casual": _variation_change("casual"),
                    "marketing": _variation_change("marketing"),
                },
            },
        }

    def record_feedback(self, job, variation, liked, source_channel="web", comment=""):
        return Feedback.objects.create(
            job=job,
            variation=variation,
            liked=liked,
            source_channel=source_channel,
            comment=comment,
        )
