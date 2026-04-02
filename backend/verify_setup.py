#!/usr/bin/env python3
"""
AI Content Localization Platform - Setup Verification Script

This script verifies that the project is properly configured and ready for testing.

Run this from the backend directory:
    python verify_setup.py
"""

import sys
import os
from pathlib import Path

print("=" * 70)
print("AI CONTENT LOCALIZATION PLATFORM - SETUP VERIFICATION")
print("=" * 70)

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'


def check(condition, message):
    """Print check result."""
    status = f"{GREEN}✓{RESET}" if condition else f"{RED}✗{RESET}"
    print(f"{status} {message}")
    return condition


def section(title):
    """Print section header."""
    print(f"\n{YELLOW}━━ {title} ━━{RESET}")


all_checks_passed = True

# ============================================================================
# 1. PYTHON ENVIRONMENT
# ============================================================================
section("Python Environment")

python_version = sys.version_info
check_01 = check(
    python_version.major >= 3 and python_version.minor >= 8,
    f"Python version: {python_version.major}.{python_version.minor} (requires 3.8+)"
)
all_checks_passed = all_checks_passed and check_01

# ============================================================================
# 2. DEPENDENCIES
# ============================================================================
section("Required Dependencies")

required_packages = {
    'flask': 'Flask (web framework)',
    'flask_cors': 'Flask-CORS (CORS support)',
    'sqlalchemy': 'SQLAlchemy (database ORM)',
    'langdetect': 'langdetect (language detection)',
    'textblob': 'TextBlob (NLP)',
    'openai': 'OpenAI (API client)',
    'language_tool_python': 'language-tool-python (grammar checking)',
    'dotenv': 'python-dotenv (environment loading)',
}

missing_packages = []
for package, description in required_packages.items():
    try:
        __import__(package)
        check(True, description)
    except ImportError:
        check(False, description)
        missing_packages.append(package)
        all_checks_passed = False

if missing_packages:
    print(f"\n{RED}Missing packages. Install with:{RESET}")
    print(f"  pip install {' '.join(missing_packages)}")

# ============================================================================
# 3. FILE STRUCTURE
# ============================================================================
section("Project Structure")

files_to_check = {
    'app.py': 'Main Flask application',
    'requirements.txt': 'Python dependencies',
    '.env': 'Environment configuration',
    'app/models.py': 'Database models',
    'app/database.py': 'Database setup',
    'app/services/context_analyzer.py': 'Context analysis module',
    'app/services/localization_engine.py': 'Localization engine',
    'app/services/cultural_adapter.py': 'Cultural adaptation',
    'app/services/quality_validation.py': 'Quality validation',
    'app/core/logger.py': 'Logger setup',
    '../frontend/index.html': 'Frontend application',
}

for filepath, description in files_to_check.items():
    exists = Path(filepath).exists()
    check(exists, description)
    if not exists:
        all_checks_passed = False

# ============================================================================
# 4. CONFIGURATION
# ============================================================================
section("Configuration")

env_exists = Path('.env').exists()
check(env_exists, ".env file exists")
if not env_exists:
    all_checks_passed = False
    print(f"  {YELLOW}Create .env from .env.example:{RESET} cp .env.example .env")

if env_exists:
    from dotenv import load_dotenv
    load_dotenv()
    
    openai_key = os.getenv('OPENAI_API_KEY')
    check(
        openai_key and openai_key.startswith('sk-'),
        "OPENAI_API_KEY configured"
    )
    if not (openai_key and openai_key.startswith('sk-')):
        all_checks_passed = False
        print(f"  {YELLOW}Add your OpenAI API key to .env{RESET}")
    
    db_url = os.getenv('DATABASE_URL', 'sqlite:///./localization.db')
    check(db_url, f"DATABASE_URL configured: {db_url}")

# ============================================================================
# 5. DATABASE
# ============================================================================
section("Database")

try:
    from sqlalchemy import create_engine
    database_url = os.getenv('DATABASE_URL', 'sqlite:///./localization.db')
    engine = create_engine(database_url)
    
    # Try to connect
    with engine.connect() as connection:
        check(True, f"Database connection: {database_url}")
except Exception as e:
    check(False, f"Database connection failed: {e}")
    all_checks_passed = False

# ============================================================================
# 6. MODULE IMPORTS
# ============================================================================
section("Module Imports")

modules_to_import = {
    'app.models': 'Database models',
    'app.database': 'Database utilities',
    'app.services.context_analyzer': 'Context analyzer',
    'app.services.localization_engine': 'Localization engine',
    'app.services.cultural_adapter': 'Cultural adapter',
    'app.services.quality_validation': 'Quality validation',
    'app.core.logger': 'Logger',
}

for module_path, description in modules_to_import.items():
    try:
        __import__(module_path)
        check(True, f"Import {description}")
    except Exception as e:
        check(False, f"Import {description}: {e}")
        all_checks_passed = False

# ============================================================================
# 7. SERVICES
# ============================================================================
section("Service Modules")

try:
    from app.services.context_analyzer import detect_language, analyze_sentiment
    test_lang = detect_language("Hello world")
    test_sentiment = analyze_sentiment("I love this!")
    check(test_lang == 'en', f"Language detection: detected '{test_lang}'")
    check(test_sentiment in ['positive', 'negative', 'neutral'], f"Sentiment analysis: detected '{test_sentiment}'")
except Exception as e:
    check(False, f"Service test failed: {e}")
    all_checks_passed = False

# ============================================================================
# 8. SUMMARY
# ============================================================================
section("Summary")

if all_checks_passed:
    print(f"\n{GREEN}✓ All checks passed! Project is ready for testing.{RESET}\n")
    print("Next steps:")
    print("  1. Start Flask server: python app.py")
    print("  2. Open frontend: Open frontend/index.html in browser")
    print("  3. Test API: curl http://127.0.0.1:5000/health")
    sys.exit(0)
else:
    print(f"\n{RED}✗ Some checks failed. Please fix the issues above.{RESET}\n")
    print("For help:")
    print("  1. Check TESTING_SETUP_GUIDE.md for detailed instructions")
    print("  2. Run: pip install -r requirements.txt")
    print("  3. Edit .env with your OpenAI API key")
    sys.exit(1)
