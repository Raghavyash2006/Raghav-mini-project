import logging
import os
from io import BytesIO

import requests
from PIL import Image

logger = logging.getLogger(__name__)


def extract_text_from_image(image_file):
    """
    Hybrid OCR:
    - Uses OCR API (Render)
    - Uses Tesseract (local)
    """
    use_api = os.getenv("USE_OCR_API", "false").lower() in {"1", "true", "yes", "on"}

    if use_api:
        return _extract_text_via_api(image_file)
    else:
        return _extract_text_via_tesseract(image_file)


# ===================== OCR API =====================
def _extract_text_via_api(image_file):
    api_key = os.getenv("OCR_API_KEY", "")
    url = "https://api.ocr.space/parse/image"

    try:
        # Reset pointer
        if hasattr(image_file, "seek"):
            try:
                image_file.seek(0)
            except Exception:
                pass

        # Read file
        file_content = image_file.read() if hasattr(image_file, "read") else image_file

        # Validate + detect format
        img = Image.open(BytesIO(file_content))
        img.load()

        image_format = img.format.lower() if img.format else "jpeg"
        mime_type = f"image/{image_format}"

        # ✅ CORRECT FILE FORMAT (IMPORTANT FIX)
        files = {
            "file": (
                getattr(image_file, "name", f"image.{image_format}"),
                file_content,
                mime_type,
            )
        }

        payload = {
            "apikey": api_key,
            "language": "eng",
            "isOverlayRequired": False,
        }

        logger.debug("Sending OCR request to API...")

        response = requests.post(url, files=files, data=payload, timeout=30)
        response.raise_for_status()

        result = response.json()

        # ✅ CORRECT RESPONSE PARSING (IMPORTANT FIX)
        if not result.get("IsErroredOnProcessing", False):
            parsed_results = result.get("ParsedResults")

            if parsed_results and len(parsed_results) > 0:
                extracted_text = parsed_results[0].get("ParsedText", "").strip()

                if extracted_text:
                    logger.info(f"OCR success. Characters: {len(extracted_text)}")
                    return extracted_text

            return "No text found in image"

        else:
            error_msg = result.get("ErrorMessage", "OCR API failed")
            logger.warning(error_msg)
            return f"OCR API failed: {error_msg}"

    except requests.RequestException as exc:
        logger.exception("API request failed")
        return f"OCR API connection error: {str(exc)}"

    except Exception as exc:
        logger.exception("OCR API error")
        return f"OCR API error: {str(exc)}"


# ===================== TESSERACT FALLBACK =====================
def _extract_text_via_tesseract(image_file):
    import pytesseract
    import platform

    try:
        # Windows path config
        if platform.system() == "Windows":
            _configure_tesseract()

        # Reset pointer
        if hasattr(image_file, "seek"):
            try:
                image_file.seek(0)
            except Exception:
                pass

        file_content = image_file.read()
        image = Image.open(BytesIO(file_content))

        if image.mode != "RGB":
            image = image.convert("RGB")

        text = pytesseract.image_to_string(image).strip()

        if not text:
            return "No text found in image"

        return text

    except Exception as exc:
        return f"Tesseract OCR error: {str(exc)}"


# ===================== WINDOWS CONFIG =====================
def _configure_tesseract():
    import pytesseract

    possible_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            return True

    return False