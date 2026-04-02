import os
from app.core.config import settings


def get_openai_client():
    try:
        import openai
    except ImportError as exc:
        raise RuntimeError("openai package not installed") from exc

    openai.api_key = settings.openai_api_key
    return openai


def complete_prompt(prompt: str, model: str = None) -> str:
    openai = get_openai_client()
    model = model or settings.openai_model

    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "system", "content": "You are an expert localization assistant."},
                  {"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=1024,
        n=1,
    )

    return response.choices[0].message.content.strip()
