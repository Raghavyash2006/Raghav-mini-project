from io import BytesIO
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from PIL import Image
import pytesseract

from apps.localization.services.ocr_service import OCRService


class OCRServiceTests(SimpleTestCase):
    def _make_image_file(self):
        image = Image.new("RGB", (40, 20), color="white")
        file_obj = BytesIO()
        image.save(file_obj, format="PNG")
        file_obj.seek(0)
        return file_obj

    @patch("apps.localization.services.ocr_service.pytesseract.image_to_string")
    def test_extract_text_success(self, mocked_ocr):
        mocked_ocr.return_value = "  extracted text  "
        text = OCRService.extract_text(self._make_image_file())
        self.assertEqual(text, "extracted text")

    @patch("apps.localization.services.ocr_service.Image.open")
    def test_extract_text_invalid_image_raises_value_error(self, mocked_open):
        from PIL import UnidentifiedImageError

        mocked_open.side_effect = UnidentifiedImageError("bad image")
        with self.assertRaisesRegex(ValueError, "valid image"):
            OCRService.extract_text(BytesIO(b"not-an-image"))

    @patch("apps.localization.services.ocr_service.Image.open")
    @patch("apps.localization.services.ocr_service.pytesseract.image_to_string")
    def test_extract_text_tesseract_missing_raises_runtime_error(self, mocked_ocr, mocked_open):
        mocked_open.return_value = MagicMock()
        mocked_ocr.side_effect = pytesseract.TesseractNotFoundError()
        with self.assertRaisesRegex(RuntimeError, "Tesseract"):
            OCRService.extract_text(self._make_image_file())
