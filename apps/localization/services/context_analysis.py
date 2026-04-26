from dataclasses import asdict, dataclass


SENTIMENT_KEYWORDS = {
    "positive": {"great", "good", "excellent", "amazing", "love", "happy", "fast", "easy", "smart", "awesome"},
    "negative": {"bad", "hard", "hate", "slow", "problem", "issue", "risk", "difficult", "angry", "poor"},
}

INTENT_KEYWORDS = {
    "persuasive": {
        "buy",
        "choose",
        "try",
        "discover",
        "join",
        "best",
        "offer",
        "limited",
        "sale",
        "upgrade",
    },
    "educational": {
        "learn",
        "understand",
        "tutorial",
        "guide",
        "lesson",
        "course",
        "explain",
        "how to",
        "example",
        "step",
    },
    "informative": {
        "report",
        "update",
        "details",
        "information",
        "announce",
        "overview",
        "status",
        "facts",
        "summary",
        "note",
    },
}


@dataclass
class ContextAnalysisResult:
    sentiment: str
    sentiment_score: float
    intent: str

    def to_dict(self):
        return asdict(self)


class ContextAnalysisService:
    def detect_sentiment(self, text):
        lowered = (text or "").lower()
        positive = sum(1 for word in SENTIMENT_KEYWORDS["positive"] if word in lowered)
        negative = sum(1 for word in SENTIMENT_KEYWORDS["negative"] if word in lowered)

        score = max(min((positive - negative) / 4.0, 1.0), -1.0)
        if score > 0.2:
            label = "positive"
        elif score < -0.2:
            label = "negative"
        else:
            label = "neutral"
        return label, round(score, 2)

    def detect_intent(self, text):
        lowered = (text or "").lower()
        scores = {
            label: sum(1 for word in keywords if word in lowered)
            for label, keywords in INTENT_KEYWORDS.items()
        }
        top_label = max(scores, key=scores.get)
        if scores[top_label] == 0:
            return "informative"
        return top_label

    def analyze(self, text):
        sentiment, sentiment_score = self.detect_sentiment(text)
        intent = self.detect_intent(text)
        return ContextAnalysisResult(
            sentiment=sentiment,
            sentiment_score=sentiment_score,
            intent=intent,
        ).to_dict()
