from io import BytesIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase


class LocalizationApiIntegrationTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="tester", email="tester@example.com", password="password123")
        self.client.force_login(self.user)

    def _make_image_file(self, name="sample.png"):
        image = Image.new("RGB", (50, 20), color="white")
        file_obj = BytesIO()
        image.save(file_obj, format="PNG")
        file_obj.seek(0)
        file_obj.name = name
        return file_obj

    @patch("apps.localization.views.OCRService.extract_text")
    def test_process_input_with_image_uses_ocr(self, mocked_extract_text):
        mocked_extract_text.return_value = "Extracted from image"

        response = self.client.post(
            reverse("process-input"),
            {"source_image": self._make_image_file()},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["source_type"], "image")
        self.assertEqual(response.data["processed_text"], "Extracted from image")

    @patch("apps.localization.services.localization.IdiomCulturalAdapter._ai_suggest_replacement")
    @patch("apps.localization.services.cultural.CulturalSensitivityChecker._ai_validate")
    def test_localize_history_feedback_and_compare_flow(self, mocked_cultural_ai_validate, mocked_idiom_ai):
        mocked_cultural_ai_validate.return_value = []
        mocked_idiom_ai.return_value = None

        payload = {
            "source_text": "Please keep your eyes peeled for updates.",
            "source_language": "en",
            "target_language": "es",
            "target_region": "latam",
            "tone": "formal",
            "audience": "professionals",
            "preserve_intent": True,
            "preserve_sentiment": True,
            "use_ocr": False,
        }

        first = self.client.post(reverse("localize"), payload, format="multipart")
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertIn("job_id", first.data)
        self.assertIn("variations", first.data)
        self.assertIn("variation_map", first.data)
        self.assertEqual(set(first.data["variation_map"].keys()), {"formal", "casual", "marketing"})

        second_payload = dict(payload)
        second_payload["tone"] = "casual"
        second = self.client.post(reverse("localize"), second_payload, format="multipart")
        self.assertEqual(second.status_code, status.HTTP_201_CREATED)

        history = self.client.get(reverse("history-list"))
        self.assertEqual(history.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(history.data), 2)

        detail = self.client.get(reverse("history-detail", kwargs={"pk": first.data["job_id"]}))
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(str(detail.data["id"]), str(first.data["job_id"]))
        self.assertIn("source_text", detail.data)
        self.assertIn("metadata", detail.data)

        versions = self.client.get(reverse("history-versions", kwargs={"pk": first.data["job_id"]}))
        self.assertEqual(versions.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(versions.data["records"]), 2)

        compare = self.client.get(
            reverse("history-compare"),
            {
                "left_job_id": first.data["job_id"],
                "right_job_id": second.data["job_id"],
            },
        )
        self.assertEqual(compare.status_code, status.HTTP_200_OK)
        self.assertIn("changes", compare.data)
        self.assertIn("variation_changes", compare.data["changes"])

        first_variation_id = first.data["variations"][0]["id"]
        feedback = self.client.post(
            reverse("feedback"),
            {
                "localization_job_id": first.data["job_id"],
                "variation_id": first_variation_id,
                "liked": True,
                "source_channel": "api",
                "comment": "Useful output",
            },
            format="json",
        )
        self.assertEqual(feedback.status_code, status.HTTP_201_CREATED)
        self.assertEqual(str(feedback.data["localization_job"]), str(first.data["job_id"]))
        self.assertEqual(feedback.data["source_channel"], "api")

        delete_response = self.client.delete(reverse("history-detail", kwargs={"pk": first.data["job_id"]}))
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        missing_detail = self.client.get(reverse("history-detail", kwargs={"pk": first.data["job_id"]}))
        self.assertEqual(missing_detail.status_code, status.HTTP_404_NOT_FOUND)
