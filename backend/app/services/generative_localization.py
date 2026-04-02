from app.services.ai_client import complete_prompt


def build_prompt(source_text: str, source_language: str, target_language: str, audience: str, tone: str,
                 intent: str, sentiment: str) -> str:
    return (
        f"Localize the following text preserving meaning, tone, and intent from {source_language} to {target_language}. "
        f"Audience: {audience}. Tone: {tone}. Detected intent: {intent}. Sentiment: {sentiment}.\n"
        f"Text: {source_text}\n"
        "Return only the translated text and make culturally appropriate references."
    )


def generate_localized_text(*, source_text: str, source_language: str, target_language: str,
                            audience: str, tone: str, intent: str, sentiment: str) -> str:
    prompt = build_prompt(source_text, source_language, target_language, audience, tone, intent, sentiment)
    localized = complete_prompt(prompt)
    return localized
