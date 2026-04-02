"""
LocalizationEngine class wrapper
"""


class LocalizationEngine:
    """Main localization engine class"""
    
    def __init__(self):
        """Initialize the engine"""
        from app.core.config import settings
        from app.core.logger import get_logger
        self.logger = get_logger(__name__)
        self.openai_api_key = settings.openai_api_key
        self.openai_model = settings.openai_model
    
    def localize(
        self,
        text: str,
        target_language: str,
        tone: str = "neutral",
        source_language: str = None,
        sentiment_hint: str = None,
    ) -> dict:
        """
        Localize text to target language with tone and cultural adaptation.
        
        Args:
            text: Text to localize
            target_language: Target language code (e.g., 'es', 'fr')
            tone: Tone for localization (formal, casual, marketing, neutral)
            source_language: Optional known source language code
            sentiment_hint: Optional sentiment hint from earlier analysis
            
        Returns:
            Dictionary with localization result
        """
        import uuid
        from app.services.context_analyzer import analyze_sentiment, detect_language
        from app.services.cultural_adapter import CulturalAdapterEngine
        
        request_id = str(uuid.uuid4())
        
        try:
            # Detect source language
            source_language = detect_language(text)
            
            # Analyze sentiment
            sentiment_result = analyze_sentiment(text)
            sentiment = sentiment_result.get("sentiment", "neutral")
            
            # Use localization engine fallback translation function
            from app.services.localization_engine import generate_localization
            translation_result = generate_localization(
                text=text,
                source_language=source_language,
                target_language=target_language,
                tone=tone,
                sentiment=sentiment,
                characteristics=None,
                model=None,
            )
            localized_text = translation_result.get("localized_text", text)
            
            # Apply cultural adaptation
            adapter = CulturalAdapterEngine()
            adapted_text = adapter.adapt_cultural_references(
                localized_text,
                source_language,
                target_language
            )
            
            return {
                "original_text": text,
                "localized_text": adapted_text,
                "detected_language": source_language,
                "target_language": target_language,
                "tone": tone,
                "sentiment": sentiment,
                "request_id": request_id,
                "explanation": f"Translated from {source_language} to {target_language} with {tone} tone"
            }
        except Exception as e:
            self.logger.error(f"Localization failed: {e}")
            raise
