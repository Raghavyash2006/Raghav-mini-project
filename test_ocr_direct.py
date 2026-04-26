#!/usr/bin/env python
"""Direct OCR test to debug image reading"""
import os
import sys
from io import BytesIO

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mini_localize.settings')

import django
django.setup()

from PIL import Image
from apps.localization.services.ocr_service import OCRService

# Create a simple test image with text info
print("\n=== OCR Direct Test ===\n")

# Test 1: Create simple test image
print("Test 1: Creating simple test image...")
try:
    img = Image.new('RGB', (200, 100), color='white')
    # We can't add text without PIL.ImageDraw, so let's just verify it can be opened
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Test PIL can read it
    test_img = Image.open(img_bytes)
    print(f"  ✓ Created test image. Mode: {test_img.mode}, Size: {test_img.size}")
except Exception as e:
    print(f"  ✗ Failed to create test image: {e}")

# Test 2: Test OCR with simple image
print("\nTest 2: Testing OCR with simple image...")
try:
    img_bytes.seek(0)
    result = OCRService.extract_text(img_bytes)
    print(f"  ✓ OCR extracted: '{result}' (expected empty on blank image)")
except ValueError as e:
    if "No readable text" in str(e):
        print(f"  ✓ OCR working (expected: no text in blank image)")
    else:
        print(f"  ✗ ValueError: {e}")
except Exception as e:
    print(f"  ✗ Error: {type(e).__name__}: {e}")

# Test 3: Check if Tesseract is configured
print("\nTest 3: Checking Tesseract configuration...")
try:
    import pytesseract
    OCRService._configure_tesseract()
    
    # Try to get Tesseract version
    version = pytesseract.get_tesseract_version()
    print(f"  ✓ Tesseract found: {version}")
except Exception as e:
    print(f"  ✗ Tesseract not found: {e}")

print("\n=== Test Complete ===\n")
