from pathlib import Path
path = Path('app/services/localization_engine.py')
text = path.read_text(encoding='utf-8')
start = text.find('def generate_localization(')
end = text.find('# ============================================================================', start)
if start == -1 or end == -1:
    raise SystemExit('markers not found')
new_body = '''def generate_localization(
    text: str,
    source_language: str,
    target_language: str,
    tone: str = "neutral",
    sentiment: str = "neutral",
    characteristics: Optional[Dict] = None,
    model: Optional[str] = None
) -> Dict[str, any]:
    """Generate semantic, culturally-aware localization (stub-friendly)."""

    if characteristics is None:
        characteristics = {
            'word_count': len(text.split()),
            'is_technical': False,
            'has_urls': False,
            'is_question': text.strip().endswith('?'),
            'is_uppercase': text.isupper() if len(text) > 3 else False,
        }

    model = model or settings.openai_model

    logger.info(f"Starting localization: {source_language}→{target_language}, tone={tone}, sentiment={sentiment}")

    # Build prompt and context as before (for completeness)
    idioms = extract_idioms(text)
    cultural_rule = find_cultural_equivalent(text, source_language, target_language)
    sentiment_intensity = analyze_sentiment_intensity(text, sentiment)

    prompt = build_advanced_localization_prompt(
        text, source_language, target_language,
        tone, sentiment, characteristics,
        cultural_rule, sentiment_intensity
    )

    if not settings.openai_api_key or settings.openai_api_key == 'your_openai_api_key_here':
        logger.warning('OpenAI API key not configured; using local fallback stub translation.')
        localized_text = f'[stub] {text} ({target_language})'
        explanation_text = 'OpenAI key missing; using local fallback behavior.'
        return {
            'localized_text': localized_text,
            'explanation': explanation_text,
            'tone_applied': tone,
            'sentiment_preserved': sentiment,
            'quality_score': 72.0,
            'cultural_adaptations': [],
            'literal_translation': localized_text,
            'key_changes': [],
            'confidence': 0.72
        }

    try:
        openai = get_openai_client()
        tone_profile = TONE_PROFILES.get(tone, TONE_PROFILES['neutral'])
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {'role': 'system', 'content': 'You are a professional localization specialist. Only return JSON.'},
                {'role': 'user', 'content': prompt}
            ],
            temperature=tone_profile['temperature'],
            max_tokens=1500,
            top_p=0.9,
        )
        response_text = response.choices[0].message.content.strip()

        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0]
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0]

        result = json.loads(response_text)
        if 'localized_text' not in result or 'explanation' not in result:
            raise ValueError('Invalid OpenAI response schema')

        result['quality_score'] = result.get('confidence_score', 0.85) * 100
        result['tone_applied'] = tone
        result['sentiment_preserved'] = sentiment
        result['cultural_adaptations'] = result.get('idioms_adapted', [])

        return result

    except Exception as e:
        logger.exception(f'OpenAI call failed, returning fallback: {e}')
        localized_text = f'[stub] {text} ({target_language})'
        explanation_text = f'Failed OpenAI: {e}; using fallback.'
        return {
            'localized_text': localized_text,
            'explanation': explanation_text,
            'tone_applied': tone,
            'sentiment_preserved': sentiment,
            'quality_score': 70.0,
            'cultural_adaptations': [],
            'literal_translation': localized_text,
            'key_changes': [],
            'confidence': 0.70
        }
'''
path.write_text(text[:start] + new_body + text[end:])
print('generate_localization replaced')
