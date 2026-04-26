import uuid

from django.db import models
from django.conf import settings


class LocalizationJob(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="localization_jobs", on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    version_group_key = models.CharField(max_length=64, db_index=True, default="")
    version_number = models.PositiveIntegerField(default=1)
    source_text = models.TextField(blank=True)
    source_language = models.CharField(max_length=32, default="en")
    target_language = models.CharField(max_length=32, default="en")
    target_region = models.CharField(max_length=64, default="global")
    tone = models.CharField(max_length=32, default="neutral")
    audience = models.CharField(max_length=64, default="general")
    preserve_intent = models.BooleanField(default=True)
    preserve_sentiment = models.BooleanField(default=True)
    use_ocr = models.BooleanField(default=True)
    ocr_text = models.TextField(blank=True)
    sentiment_label = models.CharField(max_length=32, blank=True)
    sentiment_score = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    cultural_risk_score = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    explanation = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["version_group_key", "version_number"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["source_language", "target_language", "created_at"]),
        ]


class LocalizationVariation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(LocalizationJob, related_name="variations", on_delete=models.CASCADE)
    variant_name = models.CharField(max_length=32)
    localized_text = models.TextField()
    explanation = models.JSONField(default=list, blank=True)
    cultural_risk_score = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        unique_together = ["job", "variant_name"]
        indexes = [
            models.Index(fields=["job", "variant_name"]),
            models.Index(fields=["created_at"]),
        ]


class Feedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(LocalizationJob, related_name="feedback_entries", on_delete=models.CASCADE)
    variation = models.ForeignKey(LocalizationVariation, related_name="feedback_entries", on_delete=models.CASCADE)
    liked = models.BooleanField(default=True)
    source_channel = models.CharField(max_length=32, default="web")
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["job", "created_at"]),
            models.Index(fields=["variation", "created_at"]),
            models.Index(fields=["liked", "created_at"]),
        ]
