import logging

from ..ocr_utils import extract_text_from_image

logger = logging.getLogger(__name__)


class OCRService:
    @staticmethod
    def extract_text(uploaded_file):
        """
        Extract text from an uploaded image using hybrid OCR.
        
        Uses OCR.space API if USE_OCR_API=true (requires OCR_API_KEY),
        otherwise falls back to local Tesseract OCR.
        
        Args:
            uploaded_file: Django UploadedFile or file-like object
            
        Returns:
            Extracted text string
            
        Raises:
            ValueError: If file is invalid or no text extracted
            RuntimeError: If OCR processing fails
        """
        if uploaded_file is None:
            raise ValueError("No image file was provided.")

        try:
            # Use hybrid OCR utility (API or Tesseract)
            text = extract_text_from_image(uploaded_file)
            logger.info(f"OCR extraction successful. Extracted {len(text)} characters.")
            return text
            
        except (ValueError, RuntimeError):
            # Let validation errors and runtime errors propagate
            raise
