import re


def normalize_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\u201c|\u201d", '"', text)
    text = re.sub(r"\u2018|\u2019", "'", text)
    return text


def clean_input(text: str) -> str:
    text = normalize_text(text)
    text = re.sub(r"[^\x00-\x7F\n\u00A0-\u017F]", "", text)
    return text
