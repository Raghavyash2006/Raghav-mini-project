"""
Context Intelligence Module

Analyzes input text to detect:
- Language (ISO 639-1 codes: 'en', 'fr', 'es', etc.)
- Sentiment (positive, negative, neutral)
- Intent (general context for localization)
"""

from typing import Dict, Tuple
from app.core.logger import get_logger


logger = get_logger(__name__)


def detect_language(text: str) -> str:
    """
    Detect the language of input text.
    
    Uses langdetect library (fast, pure Python, no compilation needed).
    
    Args:
        text: Input text to analyze
        
    Returns:
        ISO 639-1 language code (e.g., 'en', 'fr', 'es')
        Defaults to 'en' if detection fails
        
    Example:
        >>> detect_language("Bonjour le monde")
        'fr'
    """
    try:
        from langdetect import detect
        lang = detect(text)
        # Normalize some common variants
        lang_map = {
            'zh-cn': 'zh',
            'zh-tw': 'zh',
            'pt-br': 'pt',
            'pt': 'pt',
        }
        return lang_map.get(lang, lang)
    except Exception as e:
        logger.warning(f"Language detection failed: {e}. Defaulting to 'en'")
        return 'en'


def analyze_sentiment(text: str) -> str:
    """
    Analyze sentiment of input text.
    
    Returns sentiment classification: positive, negative, neutral
    
    Args:
        text: Input text to analyze
        
    Returns:
        Sentiment label: 'positive', 'negative', or 'neutral'
        
    Example:
        >>> analyze_sentiment("I love this product!")
        'positive'
    """
    try:
        from textblob import TextBlob
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        # Simple classification based on polarity score (-1 to 1)
        if polarity > 0.1:
            return 'positive'
        elif polarity < -0.1:
            return 'negative'
        else:
            return 'neutral'
            
    except Exception as e:
        logger.warning(f"Sentiment analysis failed: {e}. Defaulting to 'neutral'")
        return 'neutral'


def get_text_characteristics(text: str) -> Dict[str, any]:
    """
    Extract contextual characteristics for better localization.
    
    Args:
        text: Input text
        
    Returns:
        Dictionary with characteristics for AI prompt context
        
    Example:
        >>> get_text_characteristics("Buy now!")
        {'word_count': 2, 'is_question': False, 'has_urls': False, 'is_technical': False}
    """
    characteristics = {
        'word_count': len(text.split()),
        'char_count': len(text),
        'is_question': text.strip().endswith('?'),
        'is_uppercase': text.isupper() if len(text) > 3 else False,
        'has_urls': 'http://' in text or 'https://' in text or 'www.' in text,
        'is_technical': any(term in text.lower() for term in ['api', 'database', 'algorithm', 'code', 'debug', 'deploy']),
    }
    return characteristics


def validate_input(text: str, max_length: int = 5000) -> Tuple[bool, str]:
    """
    Validate input text before processing.
    
    Args:
        text: Input text
        max_length: Maximum allowed text length
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Example:
        >>> validate_input("", 5000)
        (False, 'Text cannot be empty')
    """
    if not text or not text.strip():
        return False, 'Text cannot be empty'
    
    if len(text) > max_length:
        return False, f'Text exceeds maximum length of {max_length} characters'
    
    if len(text) < 3:
        return False, 'Text must be at least 3 characters long'
    
    return True, ''


def analyze_context(text: str) -> Dict[str, any]:
    """
    Comprehensive context analysis orchestrator.
    
    Combines language, sentiment, and text characteristics
    into a single context dictionary for the localization engine.
    
    Args:
        text: Input text
        
    Returns:
        Context dictionary with all analysis results
        
    Example:
        >>> context = analyze_context("Great product!")
        >>> context['sentiment']
        'positive'
        >>> context['language']
        'en'
    """
    # Validate input first
    is_valid, error_msg = validate_input(text)
    if not is_valid:
        raise ValueError(error_msg)
    
    context = {
        'language': detect_language(text),
        'sentiment': analyze_sentiment(text),
        'characteristics': get_text_characteristics(text),
    }
    
    logger.info(f"Context analysis completed: language={context['language']}, sentiment={context['sentiment']}")
    return context
