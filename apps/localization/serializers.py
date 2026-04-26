from rest_framework import serializers

from .models import Feedback, LocalizationJob, LocalizationVariation


SUPPORTED_LANGUAGE_CODES = {
    "en",
    "hi",
    "de",
    "fr",
    "es",
    "it",
    "pt",
    "ja",
    "zh",
    "ar",
}

LANGUAGE_ALIASES = {
    "english": "en",
    "hindi": "hi",
    "german": "de",
    "deutsch": "de",
    "french": "fr",
    "france": "fr",
    "spanish": "es",
    "italian": "it",
    "portuguese": "pt",
    "japanese": "ja",
    "chinese": "zh",
    "mandarin": "zh",
    "arabic": "ar",
}

SUPPORTED_TONES = [
    "neutral",
    "formal",
    "professional",
    "casual",
    "marketing",
    "friendly",
    "persuasive",
    "technical",
    "empathetic",
]


def normalize_language(value):
    language = (value or "").strip().lower()
    if not language:
        return "en"

    language = LANGUAGE_ALIASES.get(language, language)
    language = language.split("-")[0]
    if language in SUPPORTED_LANGUAGE_CODES:
        return language
    raise serializers.ValidationError(
        "Unsupported language. Choose one of: en, hi, de, fr, es, it, pt, ja, zh, ar."
    )


class LocalizationRequestSerializer(serializers.Serializer):
    source_text = serializers.CharField(required=False, allow_blank=True)
    source_image = serializers.ImageField(required=False, allow_null=True)
    source_language = serializers.CharField(required=False, default="en")
    target_language = serializers.CharField(required=False, default="en")
    target_region = serializers.CharField(required=False, default="global")
    tone = serializers.ChoiceField(choices=SUPPORTED_TONES, required=False, default="neutral")
    audience = serializers.CharField(required=False, default="general")
    preserve_intent = serializers.BooleanField(required=False, default=True)
    preserve_sentiment = serializers.BooleanField(required=False, default=True)
    use_ocr = serializers.BooleanField(required=False, default=True)
    variation_types = serializers.ListField(child=serializers.CharField(), required=False)

    def validate(self, attrs):
        if not attrs.get("source_text") and not attrs.get("source_image"):
            raise serializers.ValidationError("Provide source text or upload an image.")
        return attrs

    def validate_source_language(self, value):
        return normalize_language(value)

    def validate_target_language(self, value):
        return normalize_language(value)


class InputProcessingSerializer(serializers.Serializer):
    source_text = serializers.CharField(required=False, allow_blank=True)
    source_image = serializers.ImageField(required=False, allow_null=True)

    def validate(self, attrs):
        if not attrs.get("source_text") and not attrs.get("source_image"):
            raise serializers.ValidationError("Provide either source text or an image file.")
        return attrs


class VariationSerializer(serializers.ModelSerializer):
    feedback_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()

    class Meta:
        model = LocalizationVariation
        fields = ["id", "variant_name", "localized_text", "explanation", "cultural_risk_score", "feedback_count", "like_count", "dislike_count", "created_at"]

    def get_feedback_count(self, obj):
        return obj.feedback_entries.count()

    def get_like_count(self, obj):
        return obj.feedback_entries.filter(liked=True).count()

    def get_dislike_count(self, obj):
        return obj.feedback_entries.filter(liked=False).count()


class HistorySummarySerializer(serializers.ModelSerializer):
    variation_count = serializers.SerializerMethodField()

    class Meta:
        model = LocalizationJob
        fields = [
            "id",
            "version_group_key",
            "version_number",
            "source_language",
            "target_language",
            "target_region",
            "tone",
            "audience",
            "sentiment_label",
            "sentiment_score",
            "cultural_risk_score",
            "variation_count",
            "created_at",
        ]

    def get_variation_count(self, obj):
        return obj.variations.count()


class HistoryDetailSerializer(serializers.ModelSerializer):
    variations = VariationSerializer(many=True, read_only=True)

    class Meta:
        model = LocalizationJob
        fields = [
            "id",
            "version_group_key",
            "version_number",
            "source_text",
            "source_language",
            "target_language",
            "target_region",
            "tone",
            "audience",
            "preserve_intent",
            "preserve_sentiment",
            "use_ocr",
            "ocr_text",
            "sentiment_label",
            "sentiment_score",
            "cultural_risk_score",
            "explanation",
            "metadata",
            "variations",
            "created_at",
            "updated_at",
        ]


class HistoryCompareQuerySerializer(serializers.Serializer):
    left_job_id = serializers.UUIDField()
    right_job_id = serializers.UUIDField()


class FeedbackSerializer(serializers.Serializer):
    localization_job_id = serializers.UUIDField(required=False)
    variation_id = serializers.UUIDField()
    liked = serializers.BooleanField()
    source_channel = serializers.ChoiceField(choices=["web", "api", "mobile"], required=False, default="web")
    comment = serializers.CharField(required=False, allow_blank=True)


class FeedbackResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["id", "job", "variation", "liked", "source_channel", "comment", "created_at"]
