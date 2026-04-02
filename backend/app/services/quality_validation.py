from typing import Dict

try:
    import language_tool_python
except ImportError:
    language_tool_python = None


def check_grammar(text: str, lang: str = "en") -> Dict[str, object]:
    if language_tool_python is None:
        return {"error": "language-tool-python not installed", "issues": []}

    tool = language_tool_python.LanguageToolPublicAPI(lang)
    matches = tool.check(text)
    corrections = []
    for m in matches:
        corrections.append({
            "message": m.message,
            "offset": m.offset,
            "length": m.errorLength,
            "replacements": m.replacements,
        })

    return {
        "issues": corrections,
        "is_fluent": len(corrections) == 0,
        "issue_count": len(corrections),
    }
