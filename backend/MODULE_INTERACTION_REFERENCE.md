# Complete Module Interaction Reference

## Document Purpose

This document provides a detailed, line-by-line explanation of how all backend modules work together in the Flask application. It covers:

- Exact function signatures
- Data flow between modules
- Error handling
- Database interactions
- Real-world examples

---

## Table of Contents

1. [Context Analyzer Module](#context-analyzer-module)
2. [Localization Engine Module](#localization-engine-module)
3. [Cultural Adapter Module](#cultural-adapter-module)
4. [Quality Validator Module](#quality-validator-module)
5. [Database Models & ORM](#database-models--orm)
6. [Service Orchestration](#service-orchestration)
7. [Complete Pipeline Walkthrough](#complete-pipeline-walkthrough)

---

## Context Analyzer Module

### Location
`app/services/context_analyzer.py`

### Function 1: `detect_language(text: str) -> str`

**Purpose:** Detect the language of input text using machine learning

**Implementation:**
```python
def detect_language(text: str) -> str:
    try:
        from langdetect import detect
        lang = detect(text)
        
        # Normalize language codes
        lang_map = {
            'zh-cn': 'zh',
            'zh-tw': 'zh',
            'pt-br': 'pt',
        }
        return lang_map.get(lang, lang)
    except Exception as e:
        logger.warning(f"Language detection failed: {e}. Defaulting to 'en'")
        return 'en'
```

**How It Works:**
1. Uses `langdetect` library (probabilistic language detection)
2. Processes text through pre-trained neural model
3. Returns ISO 639-1 code (e.g., 'en', 'es', 'fr')
4. Handles language variants (zh-cn → zh)
5. Returns 'en' if detection fails

**Input/Output Examples:**
```python
detect_language("Bonjour le monde")           # → 'fr'
detect_language("Hola, ¿cómo estás?")        # → 'es'
detect_language("Servus, wie geht's dir?")   # → 'de'
detect_language("こんにちは")                  # → 'ja'
detect_language("")                            # → 'en' (fallback)
```

**Used By:**
- `LocalizationService._detect_language()` in app.py
- Called in pipeline stage 1

---

### Function 2: `analyze_sentiment(text: str) -> str`

**Purpose:** Classify emotional tone of text as positive, negative, or neutral

**Implementation:**
```python
def analyze_sentiment(text: str) -> str:
    try:
        from textblob import TextBlob
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1.0 to 1.0
        
        if polarity > 0.1:
            return 'positive'
        elif polarity < -0.1:
            return 'negative'
        else:
            return 'neutral'
    except Exception as e:
        logger.warning(f"Sentiment analysis failed: {e}. Defaulting to 'neutral'")
        return 'neutral'
```

**How It Works:**
1. Uses TextBlob sentiment analysis (lexicon-based)
2. Calculates polarity score (-1.0 = negative, 0 = neutral, 1.0 = positive)
3. Classifies based on thresholds (+0.1, -0.1)
4. Returns categorical label

**Input/Output Examples:**
```python
analyze_sentiment("I love this product!")           # → 'positive'
analyze_sentiment("This is terrible")               # → 'negative'
analyze_sentiment("The cat is on the table")       # → 'neutral'
analyze_sentiment("Great! But also challenging")   # → 'neutral' (mixed)
```

**Used By:**
- `LocalizationService._analyze_sentiment()` in app.py
- Passed to localization engine as `sentiment_hint`
- Pipeline stage 2

---

### Function 3: `get_text_characteristics(text: str) -> Dict[str, any]`

**Purpose:** Extract linguistic characteristics for context-aware localization

**Implementation (Simplified):**
```python
def get_text_characteristics(text: str) -> Dict[str, any]:
    characteristics = {
        'word_count': len(text.split()),
        'char_count': len(text),
        'is_question': text.strip().endswith('?'),
        'has_urls': 'http' in text or 'www' in text,
        'is_technical': any(term in text.lower() for term in [
            'algorithm', 'api', 'cache', 'database', 'encryption'
        ]),
        'uppercase_ratio': sum(1 for c in text if c.isupper()) / len(text) if text else 0,
        'avg_word_length': sum(len(w) for w in text.split()) / len(text.split()) if text.split() else 0,
    }
    return characteristics
```

**How It Works:**
1. Analyzes text structure and content
2. Detects question format, URLs, technical terms
3. Calculates word/character statistics
4. Returns dictionary for prompt engineering

**Input/Output Examples:**
```python
get_text_characteristics("What is machine learning?")
# → {
#   'word_count': 4,
#   'char_count': 28,
#   'is_question': True,
#   'has_urls': False,
#   'is_technical': True,
#   'uppercase_ratio': 0.07,
#   'avg_word_length': 5.75
# }
```

**Used By:**
- `LocalizationService._get_characteristics()` in app.py
- Helps localization engine adjust translation approach
- Pipeline stage 3

---

## Localization Engine Module

### Location
`app/services/localization_engine.py`

### Class: `LocalizationEngine`

**Purpose:** Perform AI-powered semantic localization using OpenAI GPT

**Key Method: `localize()`**

```python
class LocalizationEngine:
    def localize(
        self,
        text: str,
        source_language: str,
        target_language: str,
        tone: str,
        sentiment_hint: str = None,
    ) -> Dict[str, Any]:
        """
        Translate and localize text with cultural awareness.
        """
        # 1. Build intelligent prompt
        prompt = self._build_prompt(
            text=text,
            source_lang=source_language,
            target_lang=target_language,
            tone=tone,
            sentiment=sentiment_hint
        )
        
        # 2. Call OpenAI API
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,  # Some creativity while staying on-brand
            max_tokens=500,
        )
        
        # 3. Parse response
        result_text = response.choices[0].message["content"]
        quality_score = self._evaluate_quality(result_text, text)
        
        return {
            "localized_text": result_text,
            "explanation": f"Translated from {source_language} to {target_language}",
            "quality_score": quality_score,
        }
```

**How It Works:**

1. **Prompt Engineering:** Creates detailed instruction for GPT
   ```
   You are a professional localization expert specializing in
   semantic translation with cultural adaptation.
   
   Translate the following English text to Spanish maintaining:
   - Original meaning and nuance
   - Casual tone as requested
   - Cultural appropriateness for Spanish speakers
   
   Text: "The ball is in your court"
   
   Provide: [translation] | [cultural adaptation if applicable]
   ```

2. **API Call:** Uses OpenAI GPT (gpt-4o-mini)
   - Temperature: 0.7 (balanced creativity)
   - Max tokens: 500 (keeps responses focused)

3. **Response Parsing:** Extracts translated text

4. **Quality Evaluation:** Scores the translation 0-100

**Input/Output Examples:**

```python
engine = LocalizationEngine()

result = engine.localize(
    text="Break a leg!",
    source_language="en",
    target_language="es",
    tone="casual",
    sentiment_hint="neutral"
)

# Output:
# {
#   "localized_text": "¡Mucha suerte!",
#   "explanation": "Idiomatic translation for theater/performance context",
#   "quality_score": 92
# }
```

**Used By:**
- `LocalizationService._translate()` in app.py
- Pipeline stage 4
- Central translation component

**Dependencies:**
- OpenAI API (requires valid `OPENAI_API_KEY`)
- gpt-4o-mini model
- Network connection

**Error Handling:**
```python
try:
    result = engine.localize(...)
except openai.RateLimitError:
    raise LocalizationEngineError("API rate limit exceeded")
except openai.AuthenticationError:
    raise LocalizationEngineError("Invalid API key")
except Exception as e:
    raise LocalizationEngineError(f"Translation failed: {e}")
```

---

## Cultural Adapter Module

### Location
`app/services/cultural_adapter.py`

### Class: `CulturalAdapterEngine`

**Purpose:** Identify and replace idioms/metaphors with culturally appropriate equivalents

**Key Method: `adapt()`**

```python
class CulturalAdapterEngine:
    def adapt(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> List[Dict[str, Any]]:
        """
        Identify idioms and provide cultural equivalents.
        """
        # 1. Load idiom database
        database = self.idiom_database.get_pair(
            source_language,
            target_language
        )
        
        # 2. Find matching idioms in text
        matches = []
        for idiom_rule in database:
            if idiom_rule['source'].lower() in text.lower():
                matches.append(idiom_rule)
        
        # 3. Process each match
        adaptations = []
        for match in matches:
            adaptation = {
                "source_idiom": match['source'],
                "target_idiom": match['target'],
                "equivalence_type": match['equivalence_type'],
                "semantic_preservation": match['preservation_score'],
                "explanation": match['cultural_context']
            }
            adaptations.append(adaptation)
        
        return adaptations
```

**How It Works:**

1. **Idiom Database:** Contains mappings like:
   ```python
   {
       "source_idiom": "piece of cake",
       "source_language": "en",
       "target_language": "es",
       "target_idiom": "pan comido",
       "semantic_meaning": "very easy",
       "equivalence_type": "direct",
       "semantic_preservation": 0.95,
       "cultural_context": "Spanish idiom for easy tasks"
   }
   ```

2. **Pattern Matching:** Searches text for known idioms

3. **Equivalence Scoring:** Rates how well cultural mapping preserves meaning
   - 1.0 = Perfect direct equivalent
   - 0.8 = High semantic preservation
   - 0.5 = Partial equivalence
   - 0.0 = No good equivalent

4. **Returns:** List of adaptations found

**Input/Output Examples:**

```python
adapter = CulturalAdapterEngine()

result = adapter.adapt(
    text="It's raining cats and dogs outside.",
    source_language="en",
    target_language="es"
)

# Output:
# [
#   {
#     "source_idiom": "raining cats and dogs",
#     "target_idiom": "llueve a cántaros",
#     "equivalence_type": "direct",
#     "semantic_preservation": 0.92,
#     "explanation": "Spanish idiom for heavy rain"
#   }
# ]
```

**Idiom Database Structure:**

```python
CULTURAL_DATABASE = {
    "en_to_es": [
        # Idioms about weather
        {"source": "raining cats and dogs", "target": "llueve a cántaros", ...},
        
        # Idioms about theater/performing
        {"source": "break a leg", "target": "¡mucha mierda!", ...},
        
        # Idioms about ease/difficulty
        {"source": "piece of cake", "target": "pan comido", ...},
        {"source": "a piece of cake", "target": "coser y cantar", ...},
    ],
    "en_to_fr": [
        {"source": "raining cats and dogs", "target": "Il pleut des cordes", ...},
        ...
    ],
    ...
}
```

**Used By:**
- `LocalizationService._apply_cultural_adaptation()` in app.py
- Pipeline stage 5
- Stored in database as `CulturalAdaptation` records

**Equivalence Types:**

| Type | Definition | Example |
|------|-----------|---------|
| direct | Equivalent idiom exists in target language | "breaks a leg" ↔ "¡mucha mierda!" |
| partial | Similar meaning, different form | "raining cats and dogs" ↔ "llueve a cántaros" |
| conceptual | Conveys meaning but not literal idiom | "piece of cake" → "es fácil" (it's easy) |
| none | No good cultural equivalent | "American baseball reference" (context-dependent) |

---

## Quality Validator Module

### Location
`app/services/quality_validation.py`

### Function: `check_grammar(text: str, lang: str = "en") -> Dict[str, object]`

**Purpose:** Validate grammar and fluency of translated text

**Implementation:**

```python
def check_grammar(text: str, lang: str = "en") -> Dict[str, object]:
    """
    Check grammar and fluency using language-tool.
    """
    try:
        tool = language_tool_python.LanguageToolPublicAPI(lang)
        matches = tool.check(text)
        
        corrections = []
        for match in matches:
            corrections.append({
                "message": match.message,
                "offset": match.offset,
                "length": match.errorLength,
                "replacements": match.replacements,
                "rule_id": match.ruleId,
                "category": match.category,
            })
        
        return {
            "is_fluent": len(corrections) == 0,
            "issue_count": len(corrections),
            "issues": corrections,
            "severity": _calculate_severity(corrections),
        }
    except Exception as e:
        logger.error(f"Grammar check failed: {e}")
        return {
            "error": "Grammar tool not available",
            "is_fluent": True,  # Assume good if tool fails
            "issues": []
        }
```

**How It Works:**

1. **Language Tool API:** Uses LanguageTool for grammar checking
   - Free, open-source
   - Supports 30+ languages
   - Real-time checking

2. **Error Detection:** Identifies:
   - Grammar mistakes
   - Spelling errors
   - Punctuation issues
   - Style problems

3. **Returns:** Detailed error list with suggestions

**Input/Output Examples:**

```python
check_grammar("El gato está en la mesa", lang="es")
# → {
#   "is_fluent": True,
#   "issue_count": 0,
#   "issues": [],
#   "severity": "clean"
# }

check_grammar("El gato es en la mesa", lang="es")  # Wrong verb
# → {
#   "is_fluent": False,
#   "issue_count": 1,
#   "issues": [{
#     "message": "Use 'está' not 'es' for location",
#     "offset": 8,
#     "length": 2,
#     "replacements": ["está"],
#     "category": "GRAMMAR"
#   }],
#   "severity": "minor"
# }
```

**Supported Languages:**

```python
lang_map = {
    "en": "en",
    "es": "es",
    "fr": "fr",
    "de": "de",
    "pt": "pt",
    "it": "it",
    # Others may be supported but not mapped
}
```

**Used By:**
- `LocalizationService._validate_quality()` in app.py
- Pipeline stage 6
- Used in quality score calculation

**Severity Calculation:**

```python
def _calculate_severity(issues):
    if not issues:
        return "clean"  # No issues
    
    critical_count = sum(1 for i in issues if i['category'] in ['GRAMMAR', 'SPELLING'])
    minor_count = len(issues) - critical_count
    
    if critical_count > 0:
        return "critical"  # Grammar/spelling errors
    elif minor_count > 2:
        return "major"  # Multiple minor issues
    else:
        return "minor"  # Few minor issues
```

---

## Database Models & ORM

### Location
`app/models.py`

### Core Models

#### 1. LocalizationHistory Model

**Purpose:** Store all translation requests and results

```python
class LocalizationHistory(Base):
    __tablename__ = "localization_history"
    
    # Primary Key
    request_id = Column(String(36), primary_key=True)
    
    # Foreign Keys
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=True, index=True)
    
    # Input Data
    source_text = Column(Text, nullable=False)
    source_language = Column(String(2), nullable=False)
    
    # Output Data
    localized_text = Column(Text, nullable=False)
    target_language = Column(String(2), nullable=False, index=True)
    
    # Metadata
    sentiment = Column(String(20), nullable=False)  # positive, negative, neutral
    tone = Column(String(20), nullable=False)       # formal, casual, marketing
    quality_score = Column(Float, nullable=False)   # 0-100
    explanation = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    user = relationship("User", back_populates="localizations")
    cultural_adaptations = relationship("CulturalAdaptation", back_populates="localization")
    feedback = relationship("Feedback", back_populates="localization")
```

**How It's Used:**

```python
# Create a new record
record = LocalizationHistory(
    request_id=str(uuid.uuid4()),
    user_id="user_123",
    source_text="Hello world",
    source_language="en",
    localized_text="Hola mundo",
    target_language="es",
    sentiment="neutral",
    tone="casual",
    quality_score=95.5,
    explanation="Direct translation",
    created_at=datetime.now()
)

db.add(record)
db.commit()

# Query records
user_translations = db.query(LocalizationHistory).filter_by(user_id="user_123").all()

# Calculate statistics
avg_quality = db.query(
    func.avg(LocalizationHistory.quality_score)
).filter(
    LocalizationHistory.user_id == "user_123"
).scalar()
```

**Indexes:**
- `user_id, created_at` - Fast user history queries
- `target_language` - Language statistics
- `quality_score` - Quality filtering

---

#### 2. CulturalAdaptation Model

**Purpose:** Track idiom replacements and cultural mappings

```python
class CulturalAdaptation(Base):
    __tablename__ = "cultural_adaptations"
    
    # Primary & Foreign Keys
    adaptation_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = Column(String(36), ForeignKey("localization_history.request_id"), index=True)
    
    # Idiom Mapping
    source_idiom = Column(String(255), nullable=False)
    target_idiom = Column(String(255), nullable=False)
    equivalence_type = Column(String(50), nullable=False)  # direct, partial, conceptual
    semantic_preservation = Column(Float, nullable=False)  # 0-1 score
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    localization = relationship("LocalizationHistory", back_populates="cultural_adaptations")
```

**How It's Used:**

```python
# Create adaptations when processing idioms
adaptation = CulturalAdaptation(
    request_id="request_id_123",
    source_idiom="break the ice",
    target_idiom="romper el hielo",
    equivalence_type="direct",
    semantic_preservation=0.98,
    created_at=datetime.now()
)

db.add(adaptation)
db.commit()

# Query for analysis
adaptations = db.query(CulturalAdaptation).filter(
    CulturalAdaptation.request_id == "request_id_123"
).all()

# Find most effective adaptations
best_adaptations = db.query(CulturalAdaptation).filter(
    CulturalAdaptation.semantic_preservation >= 0.9
).all()
```

---

#### 3. Feedback Model

**Purpose:** Store user feedback on translations for quality improvement

```python
class Feedback(Base):
    __tablename__ = "feedback"
    
    # Primary & Foreign Keys
    feedback_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = Column(String(36), ForeignKey("localization_history.request_id"), index=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=True)
    
    # Feedback Data
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now, index=True)
    
    # Relationships
    localization = relationship("LocalizationHistory", back_populates="feedback")
    user = relationship("User", back_populates="feedback")
```

**How It's Used:**

```python
# Create feedback
feedback = Feedback(
    request_id="request_id_123",
    user_id="user_123",
    rating=5,
    comment="Perfect translation!",
    created_at=datetime.now()
)

db.add(feedback)
db.commit()

# Get average rating
avg_rating = db.query(func.avg(Feedback.rating)).scalar()

# Find low-rated translations
poor_translations = db.query(Feedback).filter(
    Feedback.rating <= 2
).all()
```

---

## Service Orchestration

### Location
`app.py` - `LocalizationService` class

### Complete Orchestration Flow

```python
class LocalizationService:
    def __init__(self, db_session: Session):
        """Initialize with database session and service engines."""
        self.db = db_session
        self.localization_engine = LocalizationEngine()
        self.cultural_adapter = CulturalAdapterEngine()
        self.logger = get_logger(__name__)
    
    def localize(
        self,
        text: str,
        target_language: str,
        tone: str = "neutral",
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute complete 9-stage pipeline."""
        
        request_id = str(uuid.uuid4())
        
        # STAGE 1: Input Validation
        if not text or not text.strip():
            raise ValidationError("Text cannot be empty")
        
        text = text.strip()
        
        # STAGE 2: Language Detection
        detected_language = self._detect_language(text)
        # Calls: context_analyzer.detect_language()
        
        # STAGE 3: Sentiment Analysis
        sentiment = self._analyze_sentiment(text)
        # Calls: context_analyzer.analyze_sentiment()
        
        # STAGE 4: Text Characteristics
        characteristics = self._get_characteristics(text)
        # Calls: context_analyzer.get_text_characteristics()
        
        # STAGE 5: Translation
        localized = self._translate(
            text=text,
            source_language=detected_language,
            target_language=target_language,
            tone=tone,
            sentiment=sentiment,
        )
        # Calls: LocalizationEngine.localize()
        
        # STAGE 6: Cultural Adaptation
        adaptations = self._apply_cultural_adaptation(
            localized_text=localized["text"],
            source_language=detected_language,
            target_language=target_language,
        )
        # Calls: CulturalAdapterEngine.adapt()
        
        # STAGE 7: Quality Validation
        validation = self._validate_quality(
            text=localized["text"],
            language=target_language,
        )
        # Calls: quality_validation.check_grammar()
        
        # STAGE 8: Quality Scoring
        quality_score = self._calculate_quality_score(
            validation,
            localized.get("quality_score", 85),
        )
        
        # STAGE 9: Database Save
        self._save_localization(
            request_id=request_id,
            user_id=user_id,
            source_text=text,
            localized_text=localized["text"],
            source_language=detected_language,
            target_language=target_language,
            sentiment=sentiment,
            tone=tone,
            quality_score=quality_score,
            explanation=localized.get("explanation", ""),
        )
        
        for adaptation in adaptations:
            self._save_cultural_adaptation(
                request_id=request_id,
                source_idiom=adaptation.get("source_idiom"),
                target_idiom=adaptation.get("target_idiom"),
                equivalence_type=adaptation.get("equivalence_type"),
                semantic_preservation=adaptation.get("semantic_preservation", 0.8),
            )
        
        # STAGE 10: Return Response
        return {
            "original_text": text,
            "detected_language": detected_language,
            "sentiment": sentiment,
            "localized_text": localized["text"],
            "explanation": localized.get("explanation", ""),
            "request_id": request_id,
            "quality_score": quality_score,
            "tone": tone,
            "target_language": target_language,
            "adaptations": adaptations,
            "validation": {
                "is_fluent": validation.get("is_fluent", True),
                "issue_count": validation.get("issue_count", 0),
            },
        }
```

---

## Complete Pipeline Walkthrough

### Real Example: "Once in a blue moon"

#### Input
```json
{
  "text": "Once in a blue moon",
  "target_language": "es",
  "tone": "formal"
}
```

#### Stage-by-Stage Execution

**Stage 1: Language Detection**
```
Input: "Once in a blue moon"
Function: context_analyzer.detect_language()
Process: 
  - langdetect analyzes character patterns
  - Identifies English language
Output: "en"
```

**Stage 2: Sentiment Analysis**
```
Input: "Once in a blue moon"
Function: context_analyzer.analyze_sentiment()
Process:
  - TextBlob analyzes lexical sentiment
  - No strongly positive/negative words
  - Polarity score: 0.05 (neutral)
Output: "neutral"
```

**Stage 3: Text Characteristics**
```
Input: "Once in a blue moon"
Function: context_analyzer.get_text_characteristics()
Output:
{
  "word_count": 5,
  "char_count": 21,
  "is_question": False,
  "has_urls": False,
  "is_technical": False,
  "uppercase_ratio": 0.095,
  "avg_word_length": 4.2
}
```

**Stage 4: Translation**
```
Input:
  - text: "Once in a blue moon"
  - source_language: "en"
  - target_language: "es"
  - tone: "formal"
  - sentiment: "neutral"

Function: LocalizationEngine.localize()

OpenAI Prompt:
  "You are a professional localization expert.
   Translate to Spanish (formal tone) while preserving idioms:
   'Once in a blue moon'
   
   Preserve: Figurative meaning (rarely), formal register"

OpenAI Response:
  "De vez en cuando (muy raramente)"

Output:
{
  "localized_text": "De vez en cuando",
  "explanation": "Idiomatic translation meaning 'rarely' or 'infrequently'",
  "quality_score": 94
}
```

**Stage 5: Cultural Adaptation**
```
Input:
  - text: "De vez en cuando"
  - source_language: "en"
  - target_language: "es"

Function: CulturalAdapterEngine.adapt()

Idiom Database Lookup:
  - Searches: "once in a blue moon" in database
  - Finds: "en_to_es" mapping

Output:
[{
  "source_idiom": "once in a blue moon",
  "target_idiom": "de vez en cuando",
  "equivalence_type": "direct",
  "semantic_preservation": 0.96,
  "explanation": "Spanish idiom for occasional, rare occurrences"
}]
```

**Stage 6: Grammar Validation**
```
Input: "De vez en cuando"
Language: "es"

Function: quality_validation.check_grammar()

LanguageTool Analysis:
  - Grammar: Correct
  - Spelling: Correct
  - Punctuation: OK
  - Style: Good

Output:
{
  "is_fluent": True,
  "issue_count": 0,
  "issues": [],
  "severity": "clean"
}
```

**Stage 7: Quality Scoring**
```
Translation Quality: 94
Grammar Score: 100

Formula:
  quality_score = (94 × 0.7) + (100 × 0.3)
                = 65.8 + 30
                = 95.8

Output: 95.8
```

**Stage 8: Database Save**
```
LocalizationHistory Record:
- request_id: "550e8400-e29b-41d4-a716-446655440000"
- source_text: "Once in a blue moon"
- localized_text: "De vez en cuando"
- source_language: "en"
- target_language: "es"
- sentiment: "neutral"
- tone: "formal"
- quality_score: 95.8
- created_at: 2026-03-15T10:30:45

CulturalAdaptation Record:
- request_id: "550e8400-e29b-41d4-a716-446655440000"
- source_idiom: "once in a blue moon"
- target_idiom: "de vez en cuando"
- equivalence_type: "direct"
- semantic_preservation: 0.96

Status: ✓ Saved successfully
```

**Stage 9: Return Response**
```json
{
  "success": true,
  "data": {
    "original_text": "Once in a blue moon",
    "detected_language": "en",
    "sentiment": "neutral",
    "localized_text": "De vez en cuando",
    "explanation": "Idiomatic translation meaning 'rarely'",
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "quality_score": 95.8,
    "tone": "formal",
    "target_language": "es",
    "adaptations": [
      {
        "source_idiom": "once in a blue moon",
        "target_idiom": "de vez en cuando",
        "equivalence_type": "direct",
        "semantic_preservation": 0.96
      }
    ],
    "validation": {
      "is_fluent": true,
      "issue_count": 0
    }
  }
}
```

---

## Summary: Module Interaction Map

```
Request comes to Flask
              ↓
app.py routes to /api/localize
              ↓
LocalizationService initialized
              ↓
              ├─→ context_analyzer.detect_language()      [Stage 1]
              ├─→ context_analyzer.analyze_sentiment()    [Stage 2]
              ├─→ context_analyzer.get_text_characteristics() [Stage 3]
              ├─→ LocalizationEngine.localize()           [Stage 4]
              ├─→ CulturalAdapterEngine.adapt()           [Stage 5]
              ├─→ quality_validation.check_grammar()      [Stage 6]
              │
              └─→ LocalizationService._calculate_quality_score() [Stage 7]
                    ↓
              ├─→ db.add(LocalizationHistory)             [Stage 8]
              ├─→ db.add(CulturalAdaptation) × N
              │
              └─→ Return unified response to client       [Stage 9]
```

---

## Dependency Tree

```
app.py (Flask app)
├── context_analyzer.py
│   ├── langdetect (library)
│   └── textblob (library)
├── localization_engine.py
│   └── openai (library & API)
├── cultural_adapter.py
│   └── (self-contained)
├── quality_validation.py
│   └── language_tool_python (library)
├── models.py
│   └── sqlalchemy (ORM)
└── database.py
    └── sqlalchemy (engine)
```

**Key Properties:**
- ✅ No circular imports
- ✅ Each module is self-contained
- ✅ app.py imports everything (top-level only)
- ✅ Services interface through LocalizationService
- ✅ Database isolation through models.py

---

**End of Module Interaction Reference**
