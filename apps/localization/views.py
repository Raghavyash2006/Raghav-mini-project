import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import LoginForm, SignupForm
from .models import LocalizationJob, LocalizationVariation
from .serializers import (
    FeedbackSerializer,
    HistoryCompareQuerySerializer,
    HistoryDetailSerializer,
    HistorySummarySerializer,
    InputProcessingSerializer,
    LocalizationRequestSerializer,
    VariationSerializer,
)
from .services.history import HistoryService
from .services.localization import LocalizationEngine
from .services.ocr_service import OCRService

logger = logging.getLogger(__name__)


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        jobs = LocalizationJob.objects.filter(user=self.request.user).order_by("-created_at")
        variations = LocalizationVariation.objects.filter(job__user=self.request.user)

        context.update(
            {
                "user_job_count": jobs.count(),
                "user_variation_count": variations.count(),
                "recent_job": jobs.first(),
                "latest_language_pair": jobs.values_list("source_language", "target_language").first(),
            }
        )
        return context


class LoginPageView(LoginView):
    template_name = "auth.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "mode": "login",
                "page_title": "Sign in to LocaleForge",
                "page_subtitle": "Resume your private localization workspace and keep each request tied to your account.",
            }
        )
        return context

    def get_success_url(self):
        return reverse_lazy("home")


class SignupPageView(FormView):
    template_name = "auth.html"
    form_class = SignupForm
    success_url = reverse_lazy("login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "mode": "signup",
                "page_title": "Create your LocaleForge account",
                "page_subtitle": "Set up a private workspace for your translations, OCR extractions, and saved history.",
            }
        )
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Account created. Sign in to start localizing your content.")
        return super().form_valid(form)


class LogoutPageView(LogoutView):
    next_page = reverse_lazy("login")


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "ok", "service": "localeforge"})


class ProtectedAPIView(APIView):
    permission_classes = [IsAuthenticated]


class InputProcessingView(ProtectedAPIView):
    def post(self, request):
        serializer = InputProcessingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payload = serializer.validated_data
        source_text = (payload.get("source_text") or "").strip()
        source_image = payload.get("source_image")

        try:
            if source_text:
                resolved_text = source_text
                source_type = "text"
            else:
                try:
                    resolved_text = OCRService.extract_text(source_image)
                    source_type = "image"
                except (ValueError, RuntimeError) as ocr_exc:
                    logger.warning("OCR extraction failed: %s", str(ocr_exc))
                    return Response({"detail": f"OCR failed: {str(ocr_exc)}"}, status=status.HTTP_400_BAD_REQUEST)

            return Response(
                {
                    "source_type": source_type,
                    "processed_text": resolved_text,
                    "resolved_text": resolved_text,
                },
                status=status.HTTP_200_OK,
            )
        except Exception:
            logger.exception("Unexpected input processing failure")
            return Response({"detail": "Unexpected server error while processing input."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LocalizationView(ProtectedAPIView):
    def post(self, request):
        serializer = LocalizationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        try:
            source_text = payload.get("source_text", "")
            ocr_text = ""
            if payload.get("source_image") and payload.get("use_ocr", True):
                try:
                    ocr_text = OCRService.extract_text(payload["source_image"])
                    source_text = f"{source_text}\n{ocr_text}".strip() if source_text else ocr_text
                except (ValueError, RuntimeError) as ocr_exc:
                    logger.warning("OCR extraction failed: %s", str(ocr_exc))
                    return Response(
                        {"detail": f"OCR failed: {str(ocr_exc)}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            if not source_text:
                return Response({"detail": "No source text could be resolved."}, status=status.HTTP_400_BAD_REQUEST)

            payload["source_text"] = source_text
            result = LocalizationEngine().localize(payload)
            job = HistoryService().save_result(payload, result, ocr_text=ocr_text, user=request.user)
            saved_variations = VariationSerializer(job.variations.all(), many=True).data

            return Response(
                {
                    "job_id": job.id,
                    "version_group_key": job.version_group_key,
                    "version_number": job.version_number,
                    "source_language": payload.get("source_language", "en"),
                    "target_language": payload.get("target_language", "en"),
                    "tone": payload.get("tone", "neutral"),
                    "audience": payload.get("audience", "general"),
                    "resolved_text": source_text,
                    "ocr_text": ocr_text,
                    "localized_text": result["localized_text"],
                    "variations": saved_variations,
                    "variation_map": result.get("variation_map", {}),
                    "explanation": result["explanation"],
                    "explanation_data": result.get("explanation_data", {}),
                    "cultural_review": result["cultural_review"],
                    "context_analysis": result.get("context_analysis", {}),
                    "idiom_adaptation": result.get("idiom_adaptation", {}),
                    "sentiment_label": result["sentiment_label"],
                    "sentiment_score": result["sentiment_score"],
                    "intent_label": result.get("intent_label", "informative"),
                    "intent_preserved": result["intent_preserved"],
                    "sentiment_preserved": result["sentiment_preserved"],
                },
                status=status.HTTP_201_CREATED,
            )
        except RuntimeError as exc:
            logger.warning("Localization request failed: %s", exc)
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.exception("Unexpected localization failure")
            return Response({"detail": "Unexpected server error while generating localization."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HistoryListView(ProtectedAPIView):
    def get(self, request):
        jobs = LocalizationJob.objects.filter(user=request.user).prefetch_related("variations")[:50]
        return Response(HistorySummarySerializer(jobs, many=True).data)


class HistoryDetailView(ProtectedAPIView):
    def get(self, request, pk):
        job = get_object_or_404(LocalizationJob.objects.prefetch_related("variations"), pk=pk, user=request.user)
        return Response(HistoryDetailSerializer(job).data)

    def delete(self, request, pk):
        job = get_object_or_404(LocalizationJob, pk=pk, user=request.user)
        job.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class HistoryVersionsView(ProtectedAPIView):
    def get(self, request, pk):
        job = get_object_or_404(LocalizationJob, pk=pk, user=request.user)
        versions = HistoryService().list_versions(job)
        return Response(
            {
                "version_group_key": job.version_group_key,
                "current_version": job.version_number,
                "records": HistorySummarySerializer(versions, many=True).data,
            }
        )


class HistoryCompareView(ProtectedAPIView):
    def get(self, request):
        serializer = HistoryCompareQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        left_job = get_object_or_404(LocalizationJob, pk=serializer.validated_data["left_job_id"], user=request.user)
        right_job = get_object_or_404(LocalizationJob, pk=serializer.validated_data["right_job_id"], user=request.user)
        comparison = HistoryService().compare_jobs(left_job, right_job)
        return Response(comparison)


class FeedbackView(ProtectedAPIView):
    def post(self, request):
        serializer = FeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        variation = get_object_or_404(LocalizationVariation, pk=serializer.validated_data["variation_id"], job__user=request.user)

        requested_job_id = serializer.validated_data.get("localization_job_id")
        if requested_job_id and str(variation.job_id) != str(requested_job_id):
            return Response(
                {"detail": "Provided localization_job_id does not match the selected variation."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        feedback = HistoryService().record_feedback(
            job=variation.job,
            variation=variation,
            liked=serializer.validated_data["liked"],
            source_channel=serializer.validated_data.get("source_channel", "web"),
            comment=serializer.validated_data.get("comment", ""),
        )
        return Response(
            {
                "id": feedback.id,
                "localization_job": str(feedback.job_id),
                "variation": str(feedback.variation_id),
                "liked": feedback.liked,
                "source_channel": feedback.source_channel,
                "comment": feedback.comment,
                "created_at": feedback.created_at,
            },
            status=status.HTTP_201_CREATED,
        )


class VariationDetailView(ProtectedAPIView):
    def get(self, request, pk):
        variation = get_object_or_404(LocalizationVariation, pk=pk, job__user=request.user)
        return Response(VariationSerializer(variation).data)