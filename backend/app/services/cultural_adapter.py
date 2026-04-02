"""
Cultural Adaptation Module - NLP Idiom & Metaphor Replacement

Advanced idiom detection, cultural mapping, and context-aware replacement
for semantic localization across multiple languages and cultures.

Features:
- Multi-language idiom database
- Pattern-based idiom detection
- Context analysis
- Cultural equivalence mapping
- Semantic similarity scoring
- Fallback strategies

Author: NLP Research Team
Version: 1.0.0
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set
from enum import Enum
import re
import json
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# DATA STRUCTURES
# ============================================================================

class IdiomCategory(Enum):
    """Classification of idiom types"""
    METAPHOR = "metaphor"
    SIMILE = "simile"
    IDIOM = "idiom"
    COLLOQUIALISM = "colloquialism"
    PROVERB = "proverb"
    SLANG = "slang"
    CULTURAL_REFERENCE = "cultural_reference"


class SentimentType(Enum):
    """Sentiment classification"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


@dataclass
class IdiomMetadata:
    """Rich metadata for idiom entries"""
    source_idiom: str
    source_language: str
    literal_meaning: str
    semantic_meaning: str
    category: IdiomCategory
    sentiment: SentimentType
    intensity: str  # weak, medium, strong
    register: str  # formal, casual, slang, technical
    age_of_idiom: str  # ancient, medieval, modern, contemporary
    geographic_origin: str
    cultural_context: str
    usage_frequency: int  # 1-10 scale
    example_sentence: str


@dataclass
class CulturalEquivalent:
    """Target language equivalent for an idiom"""
    target_language: str
    target_idiom: str
    equivalence_type: str  # direct, partial, conceptual, none
    explanation: str
    cultural_context: str
    semantic_preservation: float  # 0-1 score
    intensity_match: bool
    example_sentence: str


@dataclass
class DetectedIdiom:
    """Idiom detected in text"""
    text: str
    start_pos: int
    end_pos: int
    confidence: float  # 0-1
    category: IdiomCategory
    metadata: Optional[IdiomMetadata] = None
    possible_equivalents: List[CulturalEquivalent] = field(default_factory=list)


# ============================================================================
# COMPREHENSIVE CULTURAL DATABASE
# ============================================================================

class CulturalDatabase:
    """
    Multi-language idiom database with cultural mappings.
    
    Structure:
    - Indexed by source idiom for fast lookup
    - Contains metadata for linguistic analysis
    - Mappings to target equivalents across languages
    """

    def __init__(self):
        self.idioms: Dict[str, IdiomMetadata] = {}
        self.equivalents: Dict[str, List[CulturalEquivalent]] = defaultdict(list)
        self.language_pairs: Set[Tuple[str, str]] = set()
        self._initialize_database()

    def _initialize_database(self):
        """Initialize comprehensive idiom database"""
        
        # English Idioms Database
        english_idioms = [
            {
                "source": "break the ice",
                "literal": "physically break ice",
                "semantic": "initiate conversation in awkward situation",
                "category": IdiomCategory.IDIOM,
                "sentiment": SentimentType.POSITIVE,
                "intensity": "medium",
                "register": "casual",
                "age": "modern",
                "origin": "European",
                "context": "Social interaction, meeting new people",
                "frequency": 9,
                "example": "We broke the ice with a joke at the party."
            },
            {
                "source": "piece of cake",
                "literal": "a portion of baked cake",
                "semantic": "something very easy to do",
                "category": IdiomCategory.IDIOM,
                "sentiment": SentimentType.POSITIVE,
                "intensity": "strong",
                "register": "casual",
                "age": "contemporary",
                "origin": "American",
                "context": "Task difficulty, simplicity",
                "frequency": 10,
                "example": "The exam was a piece of cake for Sarah."
            },
            {
                "source": "it's raining cats and dogs",
                "literal": "animals falling from sky",
                "semantic": "heavy rainfall, downpour",
                "category": IdiomCategory.IDIOM,
                "sentiment": SentimentType.NEUTRAL,
                "intensity": "strong",
                "register": "informal",
                "age": "medieval",
                "origin": "European",
                "context": "Weather description",
                "frequency": 8,
                "example": "It's raining cats and dogs outside!"
            },
            {
                "source": "throw in the towel",
                "literal": "throw cloth into ring",
                "semantic": "give up, surrender, admit defeat",
                "category": IdiomCategory.IDIOM,
                "sentiment": SentimentType.NEGATIVE,
                "intensity": "strong",
                "register": "formal",
                "age": "modern",
                "origin": "Boxing/Sports",
                "context": "Competition, struggle, persistence",
                "frequency": 8,
                "example": "After hours of trying, he threw in the towel."
            },
            {
                "source": "barking up the wrong tree",
                "literal": "dog barks at empty tree",
                "semantic": "pursuing wrong approach, mistaken strategy",
                "category": IdiomCategory.IDIOM,
                "sentiment": SentimentType.NEGATIVE,
                "intensity": "medium",
                "register": "casual",
                "age": "modern",
                "origin": "American/Hunting",
                "context": "Problem-solving, strategy",
                "frequency": 7,
                "example": "You're barking up the wrong tree about this problem."
            },
            {
                "source": "bite the bullet",
                "literal": "teeth clamp on metal",
                "semantic": "face difficult situation bravely",
                "category": IdiomCategory.IDIOM,
                "sentiment": SentimentType.MIXED,
                "intensity": "strong",
                "register": "formal",
                "age": "military",
                "origin": "Military/Surgery",
                "context": "Courage, difficult decisions",
                "frequency": 8,
                "example": "We'll have to bite the bullet and accept the terms."
            },
            {
                "source": "cry over spilled milk",
                "literal": "emotional response to spilled liquid",
                "semantic": "regret something that cannot be changed",
                "category": IdiomCategory.IDIOM,
                "sentiment": SentimentType.NEGATIVE,
                "intensity": "medium",
                "register": "casual",
                "age": "ancient",
                "origin": "Classical",
                "context": "Regret, past actions",
                "frequency": 7,
                "example": "Stop crying over spilled milk; focus on the future."
            },
            {
                "source": "under the weather",
                "literal": "physically below weather",
                "semantic": "feeling sick or unwell",
                "category": IdiomCategory.IDIOM,
                "sentiment": SentimentType.NEGATIVE,
                "intensity": "medium",
                "register": "casual",
                "age": "nautical",
                "origin": "Nautical",
                "context": "Health, wellness",
                "frequency": 8,
                "example": "I'm feeling a bit under the weather today."
            },
            {
                "source": "hit the nail on the head",
                "literal": "accurately strike nail",
                "semantic": "describe something precisely, identify core issue",
                "category": IdiomCategory.IDIOM,
                "sentiment": SentimentType.POSITIVE,
                "intensity": "strong",
                "register": "formal",
                "age": "ancient",
                "origin": "Carpentry",
                "context": "Accuracy, correctness",
                "frequency": 9,
                "example": "You hit the nail on the head with that analysis."
            },
            {
                "source": "let the cat out of the bag",
                "literal": "release feline from container",
                "semantic": "reveal secret, disclose confidential info",
                "category": IdiomCategory.IDIOM,
                "sentiment": SentimentType.NEGATIVE,
                "intensity": "medium",
                "register": "casual",
                "age": "medieval",
                "origin": "Market fraud",
                "context": "Secrets, revelation",
                "frequency": 8,
                "example": "I accidentally let the cat out of the bag about the surprise."
            }
        ]

        # Store English idioms
        for idiom_data in english_idioms:
            metadata = IdiomMetadata(
                source_idiom=idiom_data["source"],
                source_language="en",
                literal_meaning=idiom_data["literal"],
                semantic_meaning=idiom_data["semantic"],
                category=idiom_data["category"],
                sentiment=idiom_data["sentiment"],
                intensity=idiom_data["intensity"],
                register=idiom_data["register"],
                age_of_idiom=idiom_data["age"],
                geographic_origin=idiom_data["origin"],
                cultural_context=idiom_data["context"],
                usage_frequency=idiom_data["frequency"],
                example_sentence=idiom_data["example"]
            )
            self.idioms[idiom_data["source"]] = metadata

        # Define cross-language mappings
        self._add_english_to_spanish_mappings()
        self._add_english_to_hindi_mappings()
        self._add_english_to_french_mappings()
        self._add_english_to_german_mappings()

    def _add_english_to_spanish_mappings(self):
        """English → Spanish idiom mappings"""
        mappings = {
            "break the ice": [
                CulturalEquivalent(
                    target_language="es",
                    target_idiom="romper el hielo",
                    equivalence_type="direct",
                    explanation="Literal translation - exact cultural equivalent",
                    cultural_context="Social interaction - direct mapping",
                    semantic_preservation=0.95,
                    intensity_match=True,
                    example_sentence="Rompimos el hielo con una broma."
                ),
                CulturalEquivalent(
                    target_language="es",
                    target_idiom="comenzar la conversación",
                    equivalence_type="conceptual",
                    explanation="Descriptive alternative when literal doesn't fit",
                    cultural_context="Direct description of action",
                    semantic_preservation=0.85,
                    intensity_match=True,
                    example_sentence="Comenzamos la conversación de manera fácil."
                )
            ],
            "piece of cake": [
                CulturalEquivalent(
                    target_language="es",
                    target_idiom="pan comido",
                    equivalence_type="direct",
                    explanation="Spanish idiom with same meaning",
                    cultural_context="Task simplicity - food-based",
                    semantic_preservation=0.92,
                    intensity_match=True,
                    example_sentence="El examen fue pan comido para María."
                ),
                CulturalEquivalent(
                    target_language="es",
                    target_idiom="coser y cantar",
                    equivalence_type="partial",
                    explanation="Implies easy & straightforward",
                    cultural_context="Spanish idiom - sewing metaphor",
                    semantic_preservation=0.88,
                    intensity_match=True,
                    example_sentence="La tarea es coser y cantar."
                )
            ],
            "it's raining cats and dogs": [
                CulturalEquivalent(
                    target_language="es",
                    target_idiom="llueve a cántaros",
                    equivalence_type="direct",
                    explanation="Spanish idiom for heavy rain ('raining by jugs')",
                    cultural_context="Weather description - volume metaphor",
                    semantic_preservation=0.94,
                    intensity_match=True,
                    example_sentence="¡Llueve a cántaros afuera!"
                ),
                CulturalEquivalent(
                    target_language="es",
                    target_idiom="llueve copiosamente",
                    equivalence_type="conceptual",
                    explanation="Descriptive term for heavy rain",
                    cultural_context="Direct description",
                    semantic_preservation=0.80,
                    intensity_match=False,
                    example_sentence="Llueve copiosamente hoy."
                )
            ],
            "throw in the towel": [
                CulturalEquivalent(
                    target_language="es",
                    target_idiom="tirar la toalla",
                    equivalence_type="direct",
                    explanation="Boxing metaphor - direct translation",
                    cultural_context="Competition/surrender - direct mapping",
                    semantic_preservation=0.96,
                    intensity_match=True,
                    example_sentence="Decidió tirar la toalla después de intentar tanto."
                ),
                CulturalEquivalent(
                    target_language="es",
                    target_idiom="rendirse",
                    equivalence_type="conceptual",
                    explanation="Simple verb meaning to surrender",
                    cultural_context="Literal meaning without metaphor",
                    semantic_preservation=0.85,
                    intensity_match=True,
                    example_sentence="Se rindió después de muchos intentos."
                )
            ]
        }
        for source, targets in mappings.items():
            self.equivalents[source].extend(targets)
            for target in targets:
                self.language_pairs.add(("en", target.target_language))

    def _add_english_to_hindi_mappings(self):
        """English → Hindi idiom mappings"""
        mappings = {
            "break the ice": [
                CulturalEquivalent(
                    target_language="hi",
                    target_idiom="बातचीत की शुरुआत करना",
                    equivalence_type="conceptual",
                    explanation="Hindi phrase - initiate conversation (literal meaning)",
                    cultural_context="Social interaction - descriptive phrase",
                    semantic_preservation=0.90,
                    intensity_match=True,
                    example_sentence="हमने एक मजाक से बातचीत की शुरुआत की।"
                ),
                CulturalEquivalent(
                    target_language="hi",
                    target_idiom="गौर से बात करना",
                    equivalence_type="partial",
                    explanation="Begin careful conversation",
                    cultural_context="Hindi phrase",
                    semantic_preservation=0.82,
                    intensity_match=True,
                    example_sentence="हमने गौर से बात करना शुरू किया।"
                )
            ],
            "piece of cake": [
                CulturalEquivalent(
                    target_language="hi",
                    target_idiom="खेल हुआ",
                    equivalence_type="direct",
                    explanation="Hindi slang - means 'it's done/easy' (lit: became a game)",
                    cultural_context="Colloquialism - game/joke reference",
                    semantic_preservation=0.88,
                    intensity_match=True,
                    example_sentence="परीक्षा खेल हुई सारा के लिए।"
                ),
                CulturalEquivalent(
                    target_language="hi",
                    target_idiom="बहुत आसान",
                    equivalence_type="conceptual",
                    explanation="Direct translation - very easy",
                    cultural_context="Literal description",
                    semantic_preservation=0.80,
                    intensity_match=True,
                    example_sentence="यह काम बहुत आसान है।"
                )
            ],
            "it's raining cats and dogs": [
                CulturalEquivalent(
                    target_language="hi",
                    target_idiom="बहुत तेज बारिश हो रही है",
                    equivalence_type="conceptual",
                    explanation="Hindi phrase - heavy rain (literal meaning preserved)",
                    cultural_context="Weather description - direct",
                    semantic_preservation=0.92,
                    intensity_match=True,
                    example_sentence="बहुत तेज बारिश हो रही है बाहर!"
                ),
                CulturalEquivalent(
                    target_language="hi",
                    target_idiom="धारा-सार बारिश",
                    equivalence_type="direct",
                    explanation="Hindi idiom - torrential rain (stream-like rain)",
                    cultural_context="Weather - river metaphor",
                    semantic_preservation=0.94,
                    intensity_match=True,
                    example_sentence="धारा-सार बारिश हो रही है।"
                )
            ],
            "throw in the towel": [
                CulturalEquivalent(
                    target_language="hi",
                    target_idiom="हार मान जाना",
                    equivalence_type="conceptual",
                    explanation="Hindi phrase - admit defeat (lit: accept defeat)",
                    cultural_context="Struggle/surrender - direct phrase",
                    semantic_preservation=0.88,
                    intensity_match=True,
                    example_sentence="कई कोशिशों के बाद उसने हार मान दी।"
                ),
                CulturalEquivalent(
                    target_language="hi",
                    target_idiom="तौलिया फेंक देना",
                    equivalence_type="direct",
                    explanation="Hindi literal translation of English idiom",
                    cultural_context="Direct translation (adopted expression)",
                    semantic_preservation=0.85,
                    intensity_match=True,
                    example_sentence="उसने तौलिया फेंक दिया।"
                )
            ]
        }
        for source, targets in mappings.items():
            self.equivalents[source].extend(targets)
            for target in targets:
                self.language_pairs.add(("en", target.target_language))

    def _add_english_to_french_mappings(self):
        """English → French idiom mappings"""
        mappings = {
            "break the ice": [
                CulturalEquivalent(
                    target_language="fr",
                    target_idiom="briser la glace",
                    equivalence_type="direct",
                    explanation="French literal - direct equivalent",
                    cultural_context="Social interaction - direct mapping",
                    semantic_preservation=0.96,
                    intensity_match=True,
                    example_sentence="Nous avons brisé la glace avec une blague."
                )
            ],
            "piece of cake": [
                CulturalEquivalent(
                    target_language="fr",
                    target_idiom="c'est du gâteau",
                    equivalence_type="direct",
                    explanation="French idiom - it's cake (same food metaphor)",
                    cultural_context="Task difficulty - pastry reference",
                    semantic_preservation=0.94,
                    intensity_match=True,
                    example_sentence="L'examen était du gâteau pour Sarah."
                )
            ],
            "it's raining cats and dogs": [
                CulturalEquivalent(
                    target_language="fr",
                    target_idiom="il pleut des cordes",
                    equivalence_type="direct",
                    explanation="French idiom - raining ropes (volume ref)",
                    cultural_context="Weather - rope metaphor",
                    semantic_preservation=0.93,
                    intensity_match=True,
                    example_sentence="Il pleut des cordes dehors!"
                )
            ]
        }
        for source, targets in mappings.items():
            self.equivalents[source].extend(targets)
            for target in targets:
                self.language_pairs.add(("en", target.target_language))

    def _add_english_to_german_mappings(self):
        """English → German idiom mappings"""
        mappings = {
            "piece of cake": [
                CulturalEquivalent(
                    target_language="de",
                    target_idiom="ein Kinderspiel",
                    equivalence_type="direct",
                    explanation="German - a child's game (easy game ref)",
                    cultural_context="Task difficulty - play reference",
                    semantic_preservation=0.90,
                    intensity_match=True,
                    example_sentence="Die Prüfung war ein Kinderspiel für Sarah."
                )
            ],
            "it's raining cats and dogs": [
                CulturalEquivalent(
                    target_language="de",
                    target_idiom="Es regnet in Strömen",
                    equivalence_type="direct",
                    explanation="German - raining in streams",
                    cultural_context="Weather - stream/flow metaphor",
                    semantic_preservation=0.94,
                    intensity_match=True,
                    example_sentence="Es regnet in Strömen draußen!"
                )
            ]
        }
        for source, targets in mappings.items():
            self.equivalents[source].extend(targets)
            for target in targets:
                self.language_pairs.add(("en", target.target_language))

    def get_idiom(self, text: str) -> Optional[IdiomMetadata]:
        """Get idiom metadata by exact text match"""
        return self.idioms.get(text.lower())

    def get_equivalents(
        self, 
        source_idiom: str, 
        target_language: str
    ) -> List[CulturalEquivalent]:
        """Get target language equivalents for source idiom"""
        equivalents = self.equivalents.get(source_idiom.lower(), [])
        return [e for e in equivalents if e.target_language == target_language]

    def get_all_idioms_for_language(self, language: str) -> List[IdiomMetadata]:
        """Get all idioms for a specific language"""
        return [idiom for idiom in self.idioms.values() if idiom.source_language == language]


# ============================================================================
# IDIOM DETECTION ENGINE
# ============================================================================

class IdiomDetector:
    """
    Detects idioms in text using multiple strategies:
    1. Exact phrase matching
    2. Fuzzy matching (handles variations)
    3. Semantic similarity (context-based)
    """

    def __init__(self, database: CulturalDatabase):
        self.db = database
        self.max_phrase_length = 8  # Max words in an idiom
        self.fuzzy_threshold = 0.85  # Fuzzy matching threshold

    def detect_idioms(self, text: str, language: str = "en") -> List[DetectedIdiom]:
        """
        Detect all idioms in text.
        
        Algorithm:
        1. Normalize text
        2. Split into n-grams (up to max_phrase_length)
        3. For each n-gram:
           - Try exact match
           - Try fuzzy match
           - Check semantic similarity
        4. Sort by confidence
        5. Remove overlaps (priority by confidence)
        6. Return detected idioms
        """
        detected = []
        
        # Normalize text
        normalized_text = text.lower().strip()
        words = normalized_text.split()

        # Try different phrase lengths (longest first - greedy matching)
        for phrase_length in range(self.max_phrase_length, 0, -1):
            for i in range(len(words) - phrase_length + 1):
                phrase = " ".join(words[i:i + phrase_length])
                
                # Try exact match
                idiom_metadata = self.db.get_idiom(phrase)
                if idiom_metadata:
                    start_pos = text.lower().find(phrase)
                    detected.append(DetectedIdiom(
                        text=phrase,
                        start_pos=start_pos,
                        end_pos=start_pos + len(phrase),
                        confidence=1.0,
                        category=idiom_metadata.category,
                        metadata=idiom_metadata
                    ))
                    continue

                # Try fuzzy match
                fuzzy_match = self._fuzzy_match_idiom(phrase)
                if fuzzy_match and fuzzy_match[1] >= self.fuzzy_threshold:
                    matched_idiom, confidence = fuzzy_match
                    metadata = self.db.get_idiom(matched_idiom)
                    start_pos = text.lower().find(phrase)
                    detected.append(DetectedIdiom(
                        text=phrase,
                        start_pos=start_pos,
                        end_pos=start_pos + len(phrase),
                        confidence=confidence,
                        category=metadata.category,
                        metadata=metadata
                    ))

        # Remove overlaps (keep highest confidence)
        detected = self._remove_overlapping_idioms(detected)
        
        # Sort by position
        detected.sort(key=lambda x: x.start_pos)
        
        return detected

    def _fuzzy_match_idiom(self, phrase: str) -> Optional[Tuple[str, float]]:
        """
        Find fuzzy match for phrase in idiom database.
        Uses Levenshtein distance similarity.
        """
        best_match = None
        best_score = self.fuzzy_threshold

        idioms = self.db.idioms.keys()
        
        for idiom in idioms:
            score = self._similarity_score(phrase, idiom)
            if score > best_score:
                best_score = score
                best_match = idiom

        return (best_match, best_score) if best_match else None

    def _similarity_score(self, s1: str, s2: str) -> float:
        """Calculate Levenshtein distance-based similarity (0-1)"""
        if not s1 or not s2:
            return 0.0
        
        max_len = max(len(s1), len(s2))
        distance = self._levenshtein_distance(s1, s2)
        similarity = 1 - (distance / max_len)
        return max(0.0, min(1.0, similarity))

    @staticmethod
    def _levenshtein_distance(s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return IdiomDetector._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    @staticmethod
    def _remove_overlapping_idioms(
        detected: List[DetectedIdiom]
    ) -> List[DetectedIdiom]:
        """Remove overlapping idiom detections, keeping highest confidence"""
        if not detected:
            return detected

        detected.sort(key=lambda x: x.confidence, reverse=True)
        
        kept = []
        for idiom in detected:
            overlaps = any(
                not (idiom.end_pos <= k.start_pos or idiom.start_pos >= k.end_pos)
                for k in kept
            )
            if not overlaps:
                kept.append(idiom)

        return kept


# ============================================================================
# CONTEXT ANALYZER
# ============================================================================

class ContextAnalyzer:
    """
    Analyzes context around detected idioms for:
    - Tone/sentiment matching
    - Register preservation
    - Cultural appropriateness
    - Emotional intensity
    """

    def __init__(self):
        self.context_window = 5  # Words before and after idiom

    def analyze_context(
        self,
        text: str,
        detected_idiom: DetectedIdiom
    ) -> Dict:
        """
        Analyze context around idiom.
        
        Returns:
        {
            'surrounding_text': str,
            'tone': str,
            'formality': str,
            'emotional_intensity': float,
            'cultural_marks': list,
            'context_keywords': list
        }
        """
        words = text.split()
        idiom_words = detected_idiom.text.split()

        # Find context words
        start_idx = max(0, detected_idiom.start_pos - self.context_window)
        end_idx = min(len(text), detected_idiom.end_pos + self.context_window)
        surrounding_text = text[start_idx:end_idx]

        # Analyze tone/formality
        tone = self._detect_tone(surrounding_text)
        formality = self._detect_formality(surrounding_text)
        emotional_intensity = self._calculate_emotional_intensity(surrounding_text)
        cultural_marks = self._find_cultural_markers(surrounding_text)
        context_keywords = self._extract_context_keywords(surrounding_text)

        return {
            "surrounding_text": surrounding_text,
            "tone": tone,
            "formality": formality,
            "emotional_intensity": emotional_intensity,
            "cultural_marks": cultural_marks,
            "context_keywords": context_keywords,
            "idiom_would_fit": self._would_idiom_fit(detected_idiom, tone, formality)
        }

    def _detect_tone(self, text: str) -> str:
        """Detect tone: positive, negative, neutral, mixed"""
        positive_keywords = ["good", "great", "wonderful", "excellent", "happy", "glad"]
        negative_keywords = ["bad", "terrible", "awful", "sad", "angry", "upset"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_keywords if word in text_lower)
        negative_count = sum(1 for word in negative_keywords if word in text_lower)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        return "neutral"

    def _detect_formality(self, text: str) -> str:
        """Detect register: formal, casual, slang"""
        formal_indicators = ["therefore", "furthermore", "regarding", "however", "indeed"]
        casual_indicators = ["gonna", "wanna", "kinda", "sorta", "pretty much"]
        slang_indicators = ["yo", "sup", "cool", "dude", "gonna", "ain't"]

        text_lower = text.lower()
        formal_score = sum(1 for word in formal_indicators if word in text_lower)
        casual_score = sum(1 for word in casual_indicators if word in text_lower)
        slang_score = sum(1 for word in slang_indicators if word in text_lower)

        if slang_score > casual_score and slang_score > formal_score:
            return "slang"
        elif casual_score > formal_score:
            return "casual"
        return "formal"

    def _calculate_emotional_intensity(self, text: str) -> float:
        """Calculate emotional intensity 0-1"""
        exclamation_count = text.count("!")
        question_count = text.count("?")
        all_caps_words = sum(1 for word in text.split() if word.isupper() and len(word) > 1)
        
        intensity = (exclamation_count * 0.3 + question_count * 0.1 + all_caps_words * 0.2) / 3
        return min(1.0, intensity)

    def _find_cultural_markers(self, text: str) -> List[str]:
        """Find cultural or regional markers"""
        markers = []
        cultural_words = {
            "holiday": ["christmas", "diwali", "eid", "hanukkah"],
            "food": ["pizza", "sushi", "curry", "tacos"],
            "sport": ["cricket", "baseball", "football", "rugby"],
            "title": ["mr", "miss", "señor", "frau", "san"]
        }
        
        text_lower = text.lower()
        for category, words in cultural_words.items():
            if any(word in text_lower for word in words):
                markers.append(category)
        
        return markers

    def _extract_context_keywords(self, text: str) -> List[str]:
        """Extract key semantic concepts from context"""
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "of", "to", "is", "was"}
        words = [w.lower().strip(".,!?") for w in text.split()]
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        return list(set(keywords))[:5]

    def _would_idiom_fit(
        self,
        idiom: DetectedIdiom,
        tone: str,
        formality: str
    ) -> bool:
        """Check if idiom's characteristics fit the context"""
        if not idiom.metadata:
            return True

        # Rough heuristic: check basic compatibility
        idiom_register = idiom.metadata.register
        
        register_map = {
            "formal": ["formal"],
            "casual": ["casual", "informal"],
            "slang": ["slang", "casual"],
            "technical": ["formal"]
        }

        compatible_registers = register_map.get(formality, ["casual", "formal"])
        return idiom_register in compatible_registers


# ============================================================================
# CULTURAL REPLACEMENT ENGINE
# ============================================================================

class CulturalReplacementEngine:
    """
    Main engine for idiom detection, context analysis, and replacement.
    """

    def __init__(self, database: CulturalDatabase):
        self.db = database
        self.detector = IdiomDetector(database)
        self.context_analyzer = ContextAnalyzer()

    def replace_idioms(
        self,
        text: str,
        source_language: str,
        target_language: str,
        preserve_intensity: bool = True,
        prefer_direct: bool = True
    ) -> Dict:
        """
        Replace idioms in text with target language equivalents.
        
        Algorithm:
        1. Detect idioms in source text
        2. Analyze context for each idiom
        3. Find best target equivalents based on:
           - Equivalence type (prefer direct)
           - Semantic preservation score
           - Context compatibility
           - Intensity matching
        4. Replace idioms in text
        5. Return replacement mapping and modified text
        
        Args:
            text: Source text
            source_language: Source language code
            target_language: Target language code
            preserve_intensity: Match emotional intensity
            prefer_direct: Prefer direct equivalents over conceptual
        
        Returns:
            {
                'original_text': str,
                'modified_text': str,
                'replacements': [
                    {
                        'source_idiom': str,
                        'target_idiom': str,
                        'position': (start, end),
                        'confidence': float,
                        'equivalence_type': str
                    }
                ],
                'unchanged_idioms': list,
                'quality_score': float
            }
        """
        
        # Step 1: Detect idioms
        detected_idioms = self.detector.detect_idioms(text, source_language)
        
        if not detected_idioms:
            return {
                'original_text': text,
                'modified_text': text,
                'replacements': [],
                'unchanged_idioms': [],
                'quality_score': 1.0
            }

        replacements = []
        unchanged_idioms = []
        modified_text = text

        # Step 2 & 3: Analyze context and find best replacement
        offset = 0  # Track position changes due to replacements

        for idiom in detected_idioms:
            # Analyze context
            context = self.context_analyzer.analyze_context(text, idiom)

            # Find best target equivalent
            target_equivalents = self.db.get_equivalents(idiom.text, target_language)

            if not target_equivalents:
                unchanged_idioms.append({
                    'source_idiom': idiom.text,
                    'reason': 'No translation available'
                })
                continue

            # Select best equivalent
            best_equivalent = self._select_best_equivalent(
                target_equivalents,
                context,
                preserve_intensity,
                prefer_direct
            )

            if best_equivalent:
                # Step 4: Replace in text
                old_start = idiom.start_pos + offset
                old_end = idiom.end_pos + offset

                modified_text = (
                    modified_text[:old_start] +
                    best_equivalent.target_idiom +
                    modified_text[old_end:]
                )

                # Track replacement
                offset += len(best_equivalent.target_idiom) - (idiom.end_pos - idiom.start_pos)

                replacements.append({
                    'source_idiom': idiom.text,
                    'target_idiom': best_equivalent.target_idiom,
                    'position': (idiom.start_pos, idiom.end_pos),
                    'confidence': idiom.confidence,
                    'equivalence_type': best_equivalent.equivalence_type,
                    'semantic_preservation': best_equivalent.semantic_preservation,
                    'intensity_match': best_equivalent.intensity_match,
                    'explanation': best_equivalent.explanation
                })
            else:
                unchanged_idioms.append({
                    'source_idiom': idiom.text,
                    'reason': 'No suitable replacement found'
                })

        # Calculate quality score
        quality_score = self._calculate_quality_score(replacements, unchanged_idioms)

        return {
            'original_text': text,
            'modified_text': modified_text,
            'replacements': replacements,
            'unchanged_idioms': unchanged_idioms,
            'quality_score': quality_score
        }

    def _select_best_equivalent(
        self,
        equivalents: List[CulturalEquivalent],
        context: Dict,
        preserve_intensity: bool,
        prefer_direct: bool
    ) -> Optional[CulturalEquivalent]:
        """
        Select best target equivalent using multi-criteria ranking.
        
        Criteria (weighted):
        - Equivalence type match: 35%
        - Semantic preservation: 30%
        - Intensity match: 20%
        - Context compatibility: 15%
        """
        
        if not equivalents:
            return None

        # Score each equivalent
        scores = []
        for equiv in equivalents:
            score = 0.0

            # Equivalence type preference (35%)
            if prefer_direct:
                type_scores = {
                    "direct": 1.0,
                    "partial": 0.7,
                    "conceptual": 0.5,
                    "none": 0.0
                }
            else:
                type_scores = {
                    "direct": 0.95,
                    "partial": 0.85,
                    "conceptual": 0.9,
                    "none": 0.0
                }
            
            score += type_scores.get(equiv.equivalence_type, 0.5) * 0.35

            # Semantic preservation (30%)
            score += equiv.semantic_preservation * 0.30

            # Intensity matching (20%)
            if preserve_intensity:
                intensity_bonus = 1.0 if equiv.intensity_match else 0.6
                score += intensity_bonus * 0.20
            else:
                score += 0.20  # Fixed score if not preserving

            # Context compatibility (15%)
            context_bonus = 1.0 if equiv.equivalence_type != "none" else 0.5
            score += context_bonus * 0.15

            scores.append((equiv, score))

        # Return highest scoring equivalent
        best = max(scores, key=lambda x: x[1])
        return best[0] if best[1] > 0.3 else None

    def _calculate_quality_score(
        self,
        replacements: List[Dict],
        unchanged: List[Dict]
    ) -> float:
        """
        Calculate overall replacement quality (0-1).
        
        Factors:
        - Average semantic preservation
        - Replacement success rate
        - Confidence in detections
        """
        
        if not replacements and not unchanged:
            return 1.0

        total_idioms = len(replacements) + len(unchanged)
        
        # Replacement rate
        replacement_rate = len(replacements) / total_idioms if total_idioms > 0 else 0

        # Average semantic preservation
        avg_preservation = (
            sum(r['semantic_preservation'] for r in replacements) / len(replacements)
            if replacements else 0.8
        )

        # Average confidence
        avg_confidence = (
            sum(r['confidence'] for r in replacements) / len(replacements)
            if replacements else 1.0
        )

        # Combined score
        quality = (
            replacement_rate * 0.4 +
            avg_preservation * 0.35 +
            avg_confidence * 0.25
        )

        return min(1.0, max(0.0, quality))


# ============================================================================
# SINGLETON INSTANCE FOR MODULE USAGE
# ============================================================================

_cultural_adapter_instance = None

def get_cultural_adapter() -> CulturalReplacementEngine:
    """Get singleton instance of cultural replacement engine"""
    global _cultural_adapter_instance
    if _cultural_adapter_instance is None:
        db = CulturalDatabase()
        _cultural_adapter_instance = CulturalReplacementEngine(db)
    return _cultural_adapter_instance


def adapt_cultural_content(
    text: str,
    target_language: str,
    preserve_intensity: bool = True
) -> Dict:
    """
    Convenience function for cultural adaptation.
    
    Usage:
        result = adapt_cultural_content(
            "It's raining cats and dogs!",
            "es", 
            preserve_intensity=True
        )
    """
    adapter = get_cultural_adapter()
    return adapter.replace_idioms(
        text,
        source_language="en",
        target_language=target_language,
        preserve_intensity=preserve_intensity,
        prefer_direct=True
    )

# ============================================================================
# CULTURAL ADAPTER ENGINE
# ============================================================================

class CulturalAdapterEngine:
    """Main engine for cultural adaptation"""
    
    def __init__(self):
        """Initialize the cultural adapter"""
        self.logger = logging.getLogger(__name__)
    
    def adapt_cultural_references(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Adapt cultural references in text for target language.
        
        Args:
            text: Text to adapt
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Adapted text
        """
        try:
            # Use CulturalReplacementEngine if available
            detector = IdiomDetector()
            contextual_analyzer = ContextAnalyzer()
            replacement_engine = CulturalReplacementEngine()
            
            # Detect idioms
            detected = detector.detect(text)
            
            if detected.found:
                # Replace with cultural equivalents
                adapted = replacement_engine.replace_all(text, source_lang, target_lang)
                return adapted
            
            return text
        except Exception as e:
            self.logger.error(f"Cultural adaptation failed: {str(e)}")
            return text
