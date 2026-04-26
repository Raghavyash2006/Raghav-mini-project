import logging
import os
import platform
from io import BytesIO

from PIL import Image, UnidentifiedImageError
import pytesseract

logger = logging.getLogger(__name__)


class OCRService:
    _tesseract_configured = False

    @staticmethod
    def _configure_tesseract():
        """Configure pytesseract to find Tesseract OCR engine on Windows."""
        if OCRService._tesseract_configured:
            return
        
        if platform.system() == "Windows":
            # Common Windows installation paths for Tesseract
            possible_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                r"C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe".format(os.getenv("USERNAME", "User")),
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.pytesseract_cmd = path
                    logger.info(f"Configured Tesseract at: {path}")
                    OCRService._tesseract_configured = True
                    
                    # Also add to PATH for subprocess execution
                    tesseract_dir = os.path.dirname(path)
                    if tesseract_dir not in os.environ.get("PATH", ""):
                        os.environ["PATH"] = f"{tesseract_dir};{os.environ.get('PATH', '')}"
                        logger.info(f"Added Tesseract directory to PATH: {tesseract_dir}")
                    
                    return True
        
        OCRService._tesseract_configured = True
        return False

    @staticmethod
    def extract_text(uploaded_file):
        if uploaded_file is None:
            raise ValueError("No image file was provided.")

        try:
            # Configure Tesseract on first use
            OCRService._configure_tesseract()
            
            # Reset file pointer to beginning (important for Django file uploads)
            if hasattr(uploaded_file, 'seek'):
                try:
                    uploaded_file.seek(0)
                except (OSError, IOError):
                    pass  # Some file objects don't support seeking
            
            # Read file content
            if hasattr(uploaded_file, 'read'):
                file_content = uploaded_file.read()
                file_stream = BytesIO(file_content)
            else:
                file_stream = uploaded_file
            
            # Open image
            logger.debug(f"Opening image file: {getattr(uploaded_file, 'name', 'unknown')}")
            image = Image.open(file_stream)
            
            # Verify it's a valid image
            image.load()
            logger.debug(f"Image opened successfully. Format: {image.format}, Size: {image.size}")
            
            # Convert to RGB if necessary (handles RGBA, grayscale, etc.)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text
            logger.debug("Starting OCR extraction with Tesseract...")
            extracted_text = pytesseract.image_to_string(image)
            text = extracted_text.strip()
            
            if not text:
                raise ValueError("No readable text could be extracted from the image. Ensure image quality is sufficient and contains visible text.")
            
            logger.info(f"OCR extraction successful. Extracted {len(text)} characters.")
            return text
            
        except UnidentifiedImageError as exc:
            logger.warning("Invalid image uploaded for OCR: %s", str(exc))
            raise ValueError("Uploaded file is not a valid image format. Use PNG, JPG, GIF, or BMP.") from exc
        except pytesseract.TesseractNotFoundError as exc:
            logger.exception("Tesseract OCR engine not found")
            raise RuntimeError(
                "Tesseract OCR engine is not installed or not found. Please install it from: "
                "https://github.com/UB-Mannheim/tesseract/wiki. "
                "On Windows, use the installer and ensure it's installed in: C:\\Program Files\\Tesseract-OCR\\ or C:\\Program Files (x86)\\Tesseract-OCR\\"
            ) from exc
        except OSError as exc:
            logger.exception("OCR image loading failed: %s", str(exc))
            raise ValueError(f"Uploaded file could not be processed as an image: {str(exc)}") from exc
        except Exception as exc:
            logger.exception("OCR extraction failed: %s", str(exc))
            raise RuntimeError(f"Unable to extract text from the uploaded image: {str(exc)}") from exc