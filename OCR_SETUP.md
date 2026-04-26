# OCR Setup Instructions

The OCR feature requires the Tesseract OCR engine to be installed on your system.

## Windows Installation

### Option 1: Tesseract Installer (Recommended)
1. Download the installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Download the latest `.exe` file (e.g., `tesseract-ocr-w64-setup-v5.x.x.exe`)
3. Run the installer and follow the setup wizard
4. **Important**: Note the installation path (default is `C:\Program Files\Tesseract-OCR`)
5. The application will auto-detect Tesseract at common paths

### Option 2: Using Chocolatey (if installed)
```powershell
choco install tesseract
```

### Option 3: Using Scoop (if installed)
```powershell
scoop install tesseract
```

## macOS Installation

```bash
brew install tesseract
```

## Linux Installation

### Ubuntu/Debian
```bash
sudo apt-get install tesseract-ocr
```

### Fedora/RHEL
```bash
sudo dnf install tesseract
```

## Verification

After installation, restart Django and test the OCR feature with any image file.

If you continue to see errors, check:
1. Tesseract is installed in one of these Windows paths:
   - `C:\Program Files\Tesseract-OCR\tesseract.exe`
   - `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`
   - `C:\Users\{YourUsername}\AppData\Local\Tesseract-OCR\tesseract.exe`

2. Restart the Django development server after installing Tesseract

3. Ensure the image file is readable and contains text
