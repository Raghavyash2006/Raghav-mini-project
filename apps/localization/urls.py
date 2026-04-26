from django.urls import path

from .views import (
    FeedbackView,
    HealthView,
    HistoryCompareView,
    HistoryDetailView,
    HistoryListView,
    HistoryVersionsView,
    InputProcessingView,
    LocalizationView,
    VariationDetailView,
)

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("process-input/", InputProcessingView.as_view(), name="process-input"),
    path("localize/", LocalizationView.as_view(), name="localize"),
    path("history/", HistoryListView.as_view(), name="history-list"),
    path("history/compare/", HistoryCompareView.as_view(), name="history-compare"),
    path("history/<uuid:pk>/", HistoryDetailView.as_view(), name="history-detail"),
    path("history/<uuid:pk>/versions/", HistoryVersionsView.as_view(), name="history-versions"),
    path("feedback/", FeedbackView.as_view(), name="feedback"),
    path("variations/<uuid:pk>/", VariationDetailView.as_view(), name="variation-detail"),
]
