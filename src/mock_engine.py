"""Offline pedagogical simulation engine for development and air-gapped testing."""

import re
import time
from typing import List, Tuple
from src.models import BloomsLevel, QuestionEvaluation

# Action verbs mapped to Revised Bloom's Taxonomy cognitive levels
VERB_TAXONOMY = {
    BloomsLevel.CREATE: [
        "design", "formulate", "construct", "develop", "invent", "compose", "propose",
        "generate", "plan", "author", "synthesize", "architect", "engineer", "devise"
    ],
    BloomsLevel.EVALUATE: [
        "evaluate", "critique", "justify", "defend", "judge", "appraise", "rate",
        "assess", "validate", "prioritize", "recommend", "argue", "weigh", "score"
    ],
    BloomsLevel.ANALYZE: [
        "analyze", "analyse", "compare", "contrast", "differentiate", "distinguish",
        "examine", "investigate", "categorize", "dissect", "inspect", "separate", "correlate"
    ],
    BloomsLevel.APPLY: [
        "calculate", "solve", "compute", "apply", "implement", "execute", "demonstrate",
        "operate", "determine", "derive", "translate", "modify", "use", "employ"
    ],
    BloomsLevel.UNDERSTAND: [
        "explain", "describe", "summarize", "discuss", "interpret", "clarify",
        "paraphrase", "outline", "classify", "rephrase", "illustrate", "infer"
    ],
    BloomsLevel.REMEMBER: [
        "define", "list", "name", "state", "identify", "recall", "recognize",
        "match", "label", "repeat", "quote", "who", "when", "where", "what is"
    ],
}

# Domain vocabulary detector for extracting keywords
STOP_WORDS = {
    "what", "is", "the", "a", "an", "and", "or", "to", "in", "of", "for", "with",
    "on", "at", "by", "from", "how", "why", "which", "when", "where", "who",
    "can", "you", "does", "do", "are", "be", "this", "that", "these", "those"
}


class MockPedagogicalEngine:
    """Intelligent rule-based evaluator providing authentic pedagogical analysis offline."""

    def evaluate(self, question: str) -> QuestionEvaluation:
        """Analyze question text using cognitive linguistic heuristics."""
        start_time = time.time()
        text = question.strip()
        text_lower = text.lower()

        detected_level, matched_verbs = self._classify_blooms_level(text_lower)
        keywords = self._extract_keywords(text)
        difficulty = self._compute_difficulty(text, detected_level)

        level_to_index = {
            BloomsLevel.REMEMBER: 1,
            BloomsLevel.UNDERSTAND: 2,
            BloomsLevel.APPLY: 3,
            BloomsLevel.ANALYZE: 4,
            BloomsLevel.EVALUATE: 5,
            BloomsLevel.CREATE: 6,
        }
        level_index = level_to_index[detected_level]

        reasoning = self._generate_reasoning(detected_level, matched_verbs, difficulty, text)
        suggestions = self._generate_suggestions(detected_level, matched_verbs)
        elevations = self._generate_elevations(text, detected_level, keywords)

        elapsed = round(time.time() - start_time, 3)

        return QuestionEvaluation(
            question=question,
            blooms_level=detected_level,
            blooms_level_index=level_index,
            difficulty_score=difficulty,
            pedagogical_reasoning=reasoning,
            improvement_suggestions=suggestions,
            action_verbs=matched_verbs,
            keywords_identified=keywords,
            evaluation_source="mock",
            latency_seconds=elapsed,
            cognitive_elevations=elevations,
        )

    def _classify_blooms_level(self, text_lower: str) -> Tuple[BloomsLevel, List[str]]:
        """Identify highest matching cognitive level based on action verb taxonomy."""
        # Prioritize higher-order thinking skills top-down
        for level in [
            BloomsLevel.CREATE,
            BloomsLevel.EVALUATE,
            BloomsLevel.ANALYZE,
            BloomsLevel.APPLY,
            BloomsLevel.UNDERSTAND,
            BloomsLevel.REMEMBER,
        ]:
            matched = [
                verb for verb in VERB_TAXONOMY[level]
                if re.search(r"\b" + re.escape(verb) + r"\b", text_lower)
            ]
            if matched:
                return level, matched

        # Heuristics based on question structure
        if text_lower.startswith("why ") or text_lower.startswith("how does ") or "explain" in text_lower:
            return BloomsLevel.UNDERSTAND, ["explain"]
        if text_lower.startswith("what is ") or text_lower.startswith("define ") or text_lower.startswith("name "):
            return BloomsLevel.REMEMBER, ["define"]
        if "calculate" in text_lower or "find " in text_lower or "value of" in text_lower:
            return BloomsLevel.APPLY, ["calculate"]

        # Default fallback level
        return BloomsLevel.UNDERSTAND, ["comprehend"]

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract domain-relevant nouns and technical terms."""
        words = re.findall(r"\b[A-Za-z0-9_-]{3,}\b", text)
        filtered = [
            w for w in words
            if w.lower() not in STOP_WORDS and not w.lower() in [
                v for verbs in VERB_TAXONOMY.values() for v in verbs
            ]
        ]
        # Return top 5 unique keywords maintaining order
        seen = set()
        result = []
        for w in filtered:
            wl = w.lower()
            if wl not in seen:
                seen.add(wl)
                result.append(w)
            if len(result) >= 5:
                break
        return result

    def _compute_difficulty(self, text: str, level: BloomsLevel) -> float:
        """Calculate calibrated difficulty score between 1.0 and 10.0."""
        # Base difficulty anchored on cognitive tier
        tier_bases = {
            BloomsLevel.REMEMBER: 2.0,
            BloomsLevel.UNDERSTAND: 3.5,
            BloomsLevel.APPLY: 5.2,
            BloomsLevel.ANALYZE: 6.8,
            BloomsLevel.EVALUATE: 8.0,
            BloomsLevel.CREATE: 8.8,
        }
        score = tier_bases.get(level, 4.0)

        # Length and multi-step indicators
        word_count = len(text.split())
        if word_count > 30:
            score += 0.8
        elif word_count > 15:
            score += 0.4

        # Numerical / mathematical complexity indicators
        if any(char in text for char in ["=", "+", "-", "*", "/", "%", "^", "√", "θ", "π"]):
            score += 0.6

        # Multi-variable or conditional qualifiers
        if any(w in text.lower() for w in ["given that", "assuming", "if and only if", "whereas", "constraint"]):
            score += 0.7

        return round(max(1.0, min(10.0, score)), 1)

    def _generate_reasoning(
        self, level: BloomsLevel, verbs: List[str], difficulty: float, text: str
    ) -> str:
        """Produce pedagogical justification."""
        verb_str = ", ".join(f"'{v}'" for v in verbs) if verbs else "explicit cognitive directives"

        level_rationales = {
            BloomsLevel.REMEMBER: (
                f"Targets Level 1 (Remembering) as it requires rote retrieval of factual terminology "
                f"or declarative knowledge via {verb_str} without procedural synthesis."
            ),
            BloomsLevel.UNDERSTAND: (
                f"Classified under Level 2 (Understanding) because students must demonstrate conceptual "
                f"comprehension and articulate meaning using {verb_str} rather than purely recalling isolated terms."
            ),
            BloomsLevel.APPLY: (
                f"Mapped to Level 3 (Applying) as the prompt challenges learners to apply theoretical principles, "
                f"formulaic derivations, or operational rules using {verb_str} to reach a concrete solution."
            ),
            BloomsLevel.ANALYZE: (
                f"Assigned to Level 4 (Analyzing) requiring learners to deconstruct multidimensional concepts, "
                f"distinguish variables, and investigate systemic trade-offs via {verb_str}."
            ),
            BloomsLevel.EVALUATE: (
                f"Designated Level 5 (Evaluating) due to requiring critical judgment, methodological defense, "
                f"and qualitative appraisal using {verb_str} against explicit benchmark criteria."
            ),
            BloomsLevel.CREATE: (
                f"Positioned at Level 6 (Creating) as it tasks the student with holistic synthesis, original "
                f"system architectural design, or formulating novel solutions utilizing {verb_str}."
            ),
        }

        diff_note = (
            f" Difficulty calibrated at {difficulty}/10 based on structural depth and problem constraints."
        )
        return level_rationales.get(level, "Standard pedagogical evaluation.") + diff_note

    def _generate_suggestions(self, level: BloomsLevel, verbs: List[str]) -> str:
        """Provide concrete advice to adjust cognitive difficulty."""
        suggestions_map = {
            BloomsLevel.REMEMBER: (
                "To elevate to Apply or Analyze: Replace direct recall requests with a scenario requiring "
                "the student to diagnose an edge case or calculate an outcome based on these definitions."
            ),
            BloomsLevel.UNDERSTAND: (
                "To deepen cognitive engagement: Ask students to compare this concept against an opposing "
                "paradigm (Analyze) or critique common misconceptions in real-world implementations (Evaluate)."
            ),
            BloomsLevel.APPLY: (
                "To enhance rigorous evaluation: Add non-ideal boundary conditions or require students to justify "
                "why their selected computational algorithm is optimal over alternatives (Evaluate)."
            ),
            BloomsLevel.ANALYZE: (
                "To advance to Create: Ask learners to synthesize their analytical findings to design a modified, "
                "fault-tolerant architecture that resolves the identified shortcomings."
            ),
            BloomsLevel.EVALUATE: (
                "To assess synthesis (Create): Require students to not only critique existing frameworks but also "
                "propose a novel specification overcoming the critiqued limitations."
            ),
            BloomsLevel.CREATE: (
                "To ground creative design: Ensure rubric specifies clear verification metrics, budgetary/time "
                "constraints, and performance criteria so evaluation remains objectively scorable."
            ),
        }
        return suggestions_map.get(
            level, "Ensure question rubric clearly articulates grading benchmarks and expected work."
        )

    def _generate_elevations(
        self, text: str, current_level: BloomsLevel, keywords: List[str]
    ) -> dict:
        """Produce concrete re-phrasings of the question for higher cognitive levels."""
        topic = ", ".join(keywords[:2]) if keywords else "the core topic"
        elevations = {}

        if current_level != BloomsLevel.UNDERSTAND and current_level == BloomsLevel.REMEMBER:
            elevations["Understand (Level 2)"] = (
                f"Explain the conceptual mechanisms underlying {topic} and summarize its key operational principles."
            )

        if current_level.value in ["Remember", "Understand"]:
            elevations["Apply (Level 3)"] = (
                f"Given a concrete practical scenario involving {topic}, demonstrate how to calculate or implement the solution."
            )

        if current_level.value in ["Remember", "Understand", "Apply"]:
            elevations["Analyze (Level 4)"] = (
                f"Compare and contrast the behavior of {topic} against alternative paradigms under constrained resource conditions."
            )

        if current_level.value in ["Remember", "Understand", "Apply", "Analyze"]:
            elevations["Evaluate (Level 5)"] = (
                f"Critique the efficacy, safety implications, and theoretical limitations of relying on {topic} in production environments."
            )

        if current_level != BloomsLevel.CREATE:
            elevations["Create (Level 6)"] = (
                f"Design an innovative, fault-tolerant system architecture or novel experiment that incorporates {topic} to solve a real-world problem."
            )

        return elevations


# Global singleton mock engine
mock_engine = MockPedagogicalEngine()
