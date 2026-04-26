import logging
from io import BytesIO

from PIL import Image
import pytesseract

logger = logging.getLogger(__name__)


class OCRService:
    @staticmethod
    def extract_text(uploaded_image):
        if uploaded_image is None:
            return ""

        try:
            image = Image.open(uploaded_image)
            extracted_text = pytesseract.image_to_string(image)
            return extracted_text.strip()
        except Exception as exc:
            logger.exception("OCR extraction failed")
            raise RuntimeError("Unable to extract text from the uploaded image. Ensure Tesseract is installed and the image is readable.") from exc
