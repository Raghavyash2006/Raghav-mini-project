import logging
import os
from io import BytesIO

import requests
from PIL import Image

logger = logging.getLogger(__name__)


def extract_text_from_image(image_file):
    """
    Hybrid OCR extraction: API-based or Tesseract fallback.
    
    Environment variables:
    - USE_OCR_API: If "true", use OCR.space API; otherwise use pytesseract
    - OCR_API_KEY: API key for OCR.space (required if USE_OCR_API is true)
    
    Args:
        image_file: Django UploadedFile or file-like object with image data
        
    Returns:
        Extracted text string
        
    Raises:
        ValueError: If image is invalid or no text could be extracted
        RuntimeError: If OCR processing fails
    """
    
    use_api = os.getenv("USE_OCR_API", "false").lower() in {"1", "true", "yes", "on"}
    
    if use_api:
        return _extract_text_via_api(image_file)
    else:
        return _extract_text_via_tesseract(image_file)


def _extract_text_via_api(image_file):
    """
    Extract text using OCR.space API.
    
    Requires OCR_API_KEY environment variable.
    Free tier: 25 requests/day (no key needed, but limited)
    Paid tier: Use OCR_API_KEY for higher limits
    """
    api_key = os.getenv("OCR_API_KEY", "")
    url = "https://api.ocr.space/parse/image"
    
    try:
        # Read file content
        if hasattr(image_file, 'seek'):
            try:
                image_file.seek(0)
            except (OSError, IOError):
                pass
        
        if hasattr(image_file, 'read'):
            file_content = image_file.read()
        else:
            file_content = image_file
        
        # Validate image format
        try:
            img = Image.open(BytesIO(file_content))
            img.load()
            logger.debug(f"Image validated. Format: {img.format}, Size: {img.size}")
        except Exception as exc:
            raise ValueError("Uploaded file is not a valid image format. Use PNG, JPG, GIF, or BMP.") from exc
        
        # Prepare request
        files = {"filename": file_content}
        payload = {
            "isOverlayRequired": False,
            "apikey": api_key,
            "language": "eng",
        }
        
        logger.debug("Sending request to OCR.space API...")
        response = requests.post(url, files=files, data=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if not result.get("IsErroredOnProcessing", False):
            extracted_text = result.get("ParsedText", "").strip()
            if extracted_text:
                logger.info(f"OCR.space API extraction successful. Extracted {len(extracted_text)} characters.")
                return extracted_text
            else:
                raise ValueError("No readable text could be extracted from the image via OCR.space API.")
        else:
            error_msg = result.get("ErrorMessage", "Unknown API error")
            logger.warning(f"OCR.space API error: {error_msg}")
            raise RuntimeError(f"OCR.space API processing failed: {error_msg}")
            
    except requests.RequestException as exc:
        logger.exception("OCR.space API request failed")
        raise RuntimeError(f"Failed to connect to OCR.space API: {str(exc)}") from exc
    except Exception as exc:
        logger.exception("OCR.space API extraction failed")
        raise RuntimeError(f"OCR.space API extraction failed: {str(exc)}") from exc


def _extract_text_via_tesseract(image_file):
    """
    Extract text using local Tesseract OCR engine via pytesseract.
    
    Falls back when OCR.space API is unavailable or not configured.
    Requires Tesseract-OCR installed locally.
    """
    import platform
    import pytesseract
    
    try:
        # Configure Tesseract on Windows if needed
        if platform.system() == "Windows":
            _configure_tesseract()
        
        # Reset file pointer
        if hasattr(image_file, 'seek'):
            try:
                image_file.seek(0)
            except (OSError, IOError):
                pass
        
        # Read file content
        if hasattr(image_file, 'read'):
            file_content = image_file.read()
            file_stream = BytesIO(file_content)
        else:
            file_stream = image_file
        
        # Open and validate image
        logger.debug(f"Opening image file: {getattr(image_file, 'name', 'unknown')}")
        image = Image.open(file_stream)
        image.load()
        logger.debug(f"Image opened successfully. Format: {image.format}, Size: {image.size}")
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Extract text
        logger.debug("Starting OCR extraction with Tesseract...")
        extracted_text = pytesseract.image_to_string(image)
        text = extracted_text.strip()
        
        if not text:
            raise ValueError("No readable text could be extracted from the image. Ensure image quality is sufficient and contains visible text.")
        
        logger.info(f"Tesseract OCR extraction successful. Extracted {len(text)} characters.")
        return text
        
    except pytesseract.TesseractNotFoundError as exc:
        logger.exception("Tesseract OCR engine not found")
        raise RuntimeError(
            "Tesseract OCR engine is not installed or not found. Please install it from: "
            "https://github.com/UB-Mannheim/tesseract/wiki. "
            "On Windows, use the installer and ensure it's installed in: C:\\Program Files\\Tesseract-OCR\\ or C:\\Program Files (x86)\\Tesseract-OCR\\"
        ) from exc
    except Exception as exc:
        logger.exception("Tesseract OCR extraction failed")
        raise RuntimeError(f"Tesseract OCR extraction failed: {str(exc)}") from exc


def _configure_tesseract():
    """Configure pytesseract to find Tesseract OCR engine on Windows."""
    import pytesseract
    
    possible_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe".format(os.getenv("USERNAME", "User")),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.pytesseract_cmd = path
            logger.info(f"Configured Tesseract at: {path}")
            
            # Add to PATH for subprocess execution
            tesseract_dir = os.path.dirname(path)
            if tesseract_dir not in os.environ.get("PATH", ""):
                os.environ["PATH"] = f"{tesseract_dir};{os.environ.get('PATH', '')}"
                logger.info(f"Added Tesseract directory to PATH: {tesseract_dir}")
            
            return True
    
    return False
