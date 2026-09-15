"""Resilient JSON parsing and malformed output repair for LLM responses."""

import json
import logging
import re
from typing import Any, Dict, Optional
from src.models import BloomsLevel, QuestionEvaluation

logger = logging.getLogger(__name__)


def sanitize_extracted_question(raw_text: str) -> str:
    """
    Clean and normalize noisy text extracted from exam PDFs (via pdfplumber/pypdf).
    Handles:
    - Question numbering prefixes like 'Q1.', '1. (a)', 'Question 3:', '(b)'
    - Marks allocations like '[5 Marks]', '(10 pts)', '[3 marks]'
    - Broken inline newlines from narrow PDF text columns
    - Common unicode ligatures (fi, fl, smart quotes, em-dashes)
    - Stray headers/footers like 'Page 1 of 4' or 'Turn Over'
    """
    if not raw_text:
        return ""

    text = str(raw_text)

    # 1. Unicode ligature and punctuation normalization
    # Covers all Latin ligatures commonly produced by pdfplumber/pypdf from
    # Type1/OpenType PDF fonts used in university exam papers.
    ligatures = {
        # Standard Latin ligatures (most common in academic PDFs)
        "\ufb00": "ff",   # ﬀ  — 'effectiveness', 'different', 'coefficient'
        "\ufb01": "fi",   # ﬁ  — 'define', 'figure', 'first'
        "\ufb02": "fl",   # ﬂ  — 'flow', 'float'
        "\ufb03": "ffi",  # ﬃ  — 'efficient', 'official'
        "\ufb04": "ffl",  # ﬄ  — 'affluent', 'offline'
        "\ufb05": "st",   # ﬅ  — 'first', 'last'
        "\ufb06": "st",   # ﬆ  — alternate st ligature
        # Smart quotes and typographic punctuation
        "\u2019": "'",
        "\u2018": "'",
        "\u201c": '"',
        "\u201d": '"',
        # Dashes and special whitespace
        "\u2013": "-",   # en-dash
        "\u2014": "-",   # em-dash
        "\u2012": "-",   # figure dash
        "\u00a0": " ",   # non-breaking space
        "\u2009": " ",   # thin space
        "\u200b": "",    # zero-width space
    }
    for k, v in ligatures.items():
        text = text.replace(k, v)

    # 2. Strip pagination or exam booklet artifacts
    text = re.sub(r"(?i)\bPage\s+\d+\s+of\s+\d+\b", "", text)
    text = re.sub(r"(?i)\[\s*turn\s+over\s*\]|\(\s*turn\s+over\s*\)", "", text)
    text = re.sub(r"(?i)\b(?:PTO|Contd\.\.\.)\b", "", text)

    # 3. Strip marks/points allocations (e.g., [5 Marks], (10 points), [3 pts])
    text = re.sub(r"(?i)\[\s*\d+\s*(?:marks?|pts?|points?)\s*\]", "", text)
    text = re.sub(r"(?i)\(\s*\d+\s*(?:marks?|pts?|points?)\s*\)", "", text)

    # 4. Strip leading question numbers (e.g., '1.', 'Q1:', 'Question 4(a).', '(ii)')
    text = re.sub(
        r"^(?:\s*Q(?:uestion)?\s*\d+[\.\:\)]?\s*(?:\([a-zA-Z0-9]+\))?|\s*\d+[\.\:\)]\s*(?:\([a-zA-Z0-9]+\))?|\s*\([a-zA-Z0-9ivx]+\))\s*",
        "",
        text.strip(),
        flags=re.IGNORECASE,
    )

    # 5. Normalize broken single linebreaks from narrow PDF columns into single spaces
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    # Collapse multiple spaces into one
    text = re.sub(r"[ \t]+", " ", text).strip()

    return text


def clean_markdown_fences(text: str) -> str:
    """Strip markdown code fences such as ```json ... ``` or ``` ... ```."""
    text = text.strip()
    # Match ```json or ``` at beginning
    fence_pattern = r"^```(?:json|JSON)?\s*\n?(.*?)\n?```$"
    match = re.search(fence_pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Sometimes markdown fences have text before/after
    inner_match = re.search(r"```(?:json|JSON)?\s*(.*?)\s*```", text, re.DOTALL)
    if inner_match:
        return inner_match.group(1).strip()

    return text


def extract_json_substring(text: str) -> str:
    """Extract outermost JSON object delimited by { and }."""
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return text[first_brace : last_brace + 1].strip()
    return text


def repair_json_string(text: str) -> str:
    """Repair common LLM JSON syntax artifacts like trailing commas or single quotes."""
    cleaned = text

    # Remove trailing commas before closing braces or brackets: , } -> }
    cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)

    # Replace Python True/False/None if present
    cleaned = re.sub(r"\bTrue\b", "true", cleaned)
    cleaned = re.sub(r"\bFalse\b", "false", cleaned)
    cleaned = re.sub(r"\bNone\b", "null", cleaned)

    return cleaned


def extract_heuristic_field(text: str, pattern: str, default: Any = None) -> Any:
    """Extract a field using regex fallback if JSON cannot be parsed."""
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return default


def normalize_blooms_level(level_str: Optional[str]) -> BloomsLevel:
    """Safely map raw string to valid BloomsLevel enum."""
    if not level_str:
        return BloomsLevel.UNDERSTAND

    norm = level_str.strip().title()
    for member in BloomsLevel:
        if member.value.lower() == norm.lower():
            return member

    # Common synonyms / fallbacks
    if "remember" in norm.lower() or "recall" in norm.lower() or "knowledge" in norm.lower():
        return BloomsLevel.REMEMBER
    if "comprehen" in norm.lower() or "understand" in norm.lower():
        return BloomsLevel.UNDERSTAND
    if "appli" in norm.lower() or "solve" in norm.lower():
        return BloomsLevel.APPLY
    if "analy" in norm.lower():
        return BloomsLevel.ANALYZE
    if "eval" in norm.lower() or "critiq" in norm.lower():
        return BloomsLevel.EVALUATE
    if "creat" in norm.lower() or "design" in norm.lower() or "synthe" in norm.lower():
        return BloomsLevel.CREATE

    return BloomsLevel.UNDERSTAND


def parse_evaluation_response(
    raw_response: str,
    original_question: str = "",
    latency_seconds: Optional[float] = None,
    evaluation_source: str = "ollama",
) -> QuestionEvaluation:
    """
    Resiliently parse model response into QuestionEvaluation model.
    Applies multi-stage repair and fallback to guarantee zero unhandled exceptions.
    """
    if not raw_response or not raw_response.strip():
        return QuestionEvaluation(
            question=original_question,
            blooms_level=BloomsLevel.UNDERSTAND,
            blooms_level_index=2,
            difficulty_score=5.0,
            pedagogical_reasoning="Unable to evaluate: empty response received from model endpoint.",
            improvement_suggestions="Verify Ollama model status and resubmit.",
            evaluation_source=evaluation_source,
            latency_seconds=latency_seconds,
            error_message="Empty model response",
        )

    # Pipeline stages of cleaning
    candidates = [
        raw_response,
        clean_markdown_fences(raw_response),
        extract_json_substring(raw_response),
        extract_json_substring(clean_markdown_fences(raw_response)),
        repair_json_string(extract_json_substring(clean_markdown_fences(raw_response))),
    ]

    parsed_dict: Optional[Dict[str, Any]] = None
    parse_error: Optional[str] = None

    for candidate in candidates:
        try:
            candidate_cleaned = candidate.strip()
            if candidate_cleaned.startswith("{") and candidate_cleaned.endswith("}"):
                data = json.loads(candidate_cleaned)
                if isinstance(data, dict):
                    parsed_dict = data
                    break
        except Exception as e:
            parse_error = str(e)
            continue

    # If standard parsing succeeded
    if parsed_dict:
        try:
            blooms_lvl = normalize_blooms_level(str(parsed_dict.get("blooms_level", "")))
            
            # Compute index from level if missing or inconsistent
            level_to_index = {
                BloomsLevel.REMEMBER: 1,
                BloomsLevel.UNDERSTAND: 2,
                BloomsLevel.APPLY: 3,
                BloomsLevel.ANALYZE: 4,
                BloomsLevel.EVALUATE: 5,
                BloomsLevel.CREATE: 6,
            }
            derived_index = level_to_index.get(blooms_lvl, 2)
            raw_index = parsed_dict.get("blooms_level_index")
            try:
                final_index = int(raw_index) if raw_index is not None and 1 <= int(raw_index) <= 6 else derived_index
            except (ValueError, TypeError):
                final_index = derived_index

            raw_diff = parsed_dict.get("difficulty_score", 5.0)
            try:
                difficulty = round(float(raw_diff), 1)
            except (ValueError, TypeError):
                difficulty = 5.0

            action_verbs = parsed_dict.get("action_verbs", [])
            if not isinstance(action_verbs, list):
                action_verbs = [str(action_verbs)] if action_verbs else []

            keywords = parsed_dict.get("keywords_identified", [])
            if not isinstance(keywords, list):
                keywords = [str(keywords)] if keywords else []

            elevations = parsed_dict.get("cognitive_elevations")
            if not isinstance(elevations, dict) or not elevations:
                from src.mock_engine import mock_engine
                elevations = mock_engine._generate_elevations(original_question, blooms_lvl, keywords)

            return QuestionEvaluation(
                question=str(parsed_dict.get("question", original_question) or original_question),
                blooms_level=blooms_lvl,
                blooms_level_index=final_index,
                difficulty_score=difficulty,
                pedagogical_reasoning=str(
                    parsed_dict.get("pedagogical_reasoning", "Pedagogical analysis generated by engine.")
                ),
                improvement_suggestions=str(
                    parsed_dict.get(
                        "improvement_suggestions", "Consider specifying contextual constraints to refine depth."
                    )
                ),
                action_verbs=action_verbs,
                keywords_identified=keywords,
                evaluation_source=evaluation_source,
                latency_seconds=latency_seconds,
                cognitive_elevations=elevations,
            )
        except Exception as e:
            logger.warning(f"Error mapping parsed JSON to QuestionEvaluation: {e}")

    # Heuristic fallback if JSON was severely malformed
    logger.info("Engaging heuristic regex fallback parser for malformed output.")
    matched_level = extract_heuristic_field(
        raw_response, r'"blooms_level"\s*:\s*"([^"]+)"', default="Understand"
    )
    blooms_lvl = normalize_blooms_level(matched_level)

    matched_diff = extract_heuristic_field(
        raw_response, r'"difficulty_score"\s*:\s*([0-9.]+)', default="5.0"
    )
    try:
        difficulty = float(matched_diff)
    except ValueError:
        difficulty = 5.0

    reasoning = extract_heuristic_field(
        raw_response,
        r'"pedagogical_reasoning"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"',
        default="Recovered via heuristic parser from unstructured response.",
    )

    suggestions = extract_heuristic_field(
        raw_response,
        r'"improvement_suggestions"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"',
        default="Review question alignment with specified cognitive objective.",
    )

    level_to_index = {
        BloomsLevel.REMEMBER: 1,
        BloomsLevel.UNDERSTAND: 2,
        BloomsLevel.APPLY: 3,
        BloomsLevel.ANALYZE: 4,
        BloomsLevel.EVALUATE: 5,
        BloomsLevel.CREATE: 6,
    }

    return QuestionEvaluation(
        question=original_question,
        blooms_level=blooms_lvl,
        blooms_level_index=level_to_index.get(blooms_lvl, 2),
        difficulty_score=round(max(1.0, min(10.0, difficulty)), 1),
        pedagogical_reasoning=reasoning,
        improvement_suggestions=suggestions,
        action_verbs=[],
        keywords_identified=[],
        evaluation_source=evaluation_source,
        latency_seconds=latency_seconds,
        error_message=f"Output required heuristic recovery: {parse_error}" if parse_error else None,
    )
