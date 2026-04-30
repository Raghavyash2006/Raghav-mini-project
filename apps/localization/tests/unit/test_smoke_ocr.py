from io import BytesIO
from unittest.mock import patch

from django.test import SimpleTestCase
from PIL import Image

from apps.localization.services.ocr_service import OCRService


class SmokeOCRTests(SimpleTestCase):
    @patch("apps.localization.services.ocr_service.pytesseract.image_to_string")
    def test_ocr_returns_text_for_image_like_input(self, mocked_image_to_string):
        mocked_image_to_string.return_value = "extracted text"

        # Create a minimal in-memory PNG image
        image = Image.new("RGB", (10, 10), color="white")
        buf = BytesIO()
        image.save(buf, format="PNG")
        buf.seek(0)

        result = OCRService.extract_text(buf)
        self.assertTrue(result)
        self.assertIn("extracted", result)
