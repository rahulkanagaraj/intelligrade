"""Data models and schemas for IntelliGrade cognitive evaluation."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class BloomsLevel(str, Enum):
    """Revised Bloom's Taxonomy 6 Cognitive Levels."""
    REMEMBER = "Remember"
    UNDERSTAND = "Understand"
    APPLY = "Apply"
    ANALYZE = "Analyze"
    EVALUATE = "Evaluate"
    CREATE = "Create"


BLOOMS_ORDER = [
    BloomsLevel.REMEMBER,
    BloomsLevel.UNDERSTAND,
    BloomsLevel.APPLY,
    BloomsLevel.ANALYZE,
    BloomsLevel.EVALUATE,
    BloomsLevel.CREATE,
]

BLOOMS_COLORS = {
    BloomsLevel.REMEMBER: "#3b82f6",     # Vibrant Blue
    BloomsLevel.UNDERSTAND: "#06b6d4",   # Cyan
    BloomsLevel.APPLY: "#10b981",        # Emerald Green
    BloomsLevel.ANALYZE: "#f59e0b",      # Amber / Yellow
    BloomsLevel.EVALUATE: "#f97316",     # Orange
    BloomsLevel.CREATE: "#a855f7",       # Purple
}

BLOOMS_DESCRIPTIONS = {
    BloomsLevel.REMEMBER: "Recalling facts, terms, basic concepts, and retrieval of stored knowledge.",
    BloomsLevel.UNDERSTAND: "Demonstrating comprehension by explaining ideas, interpreting, classifying, and summarizing.",
    BloomsLevel.APPLY: "Executing or implementing procedures, solving problems in novel contexts or practical scenarios.",
    BloomsLevel.ANALYZE: "Breaking material into constituent parts, examining relationships, comparing, and distinguishing.",
    BloomsLevel.EVALUATE: "Making judgments based on criteria and standards, critiquing, defending, and appraising.",
    BloomsLevel.CREATE: "Putting elements together to form a novel, coherent whole, designing, inventing, and constructing.",
}


class QuestionEvaluation(BaseModel):
    """Pedagogical evaluation result for a single examination question."""
    question: str = Field(..., description="Original exam question evaluated")
    blooms_level: BloomsLevel = Field(..., description="Assigned Revised Bloom's Taxonomy cognitive level")
    blooms_level_index: int = Field(..., ge=1, le=6, description="Ordinal index 1-6 of Bloom's tier")
    difficulty_score: float = Field(..., ge=1.0, le=10.0, description="Objective difficulty score from 1.0 to 10.0")
    pedagogical_reasoning: str = Field(..., description="Pedagogical justification for classification and difficulty")
    improvement_suggestions: str = Field(..., description="Actionable advice to rebalance or elevate the question")
    action_verbs: List[str] = Field(default_factory=list, description="Primary cognitive action verbs detected")
    keywords_identified: List[str] = Field(default_factory=list, description="Key domain concepts identified")
    evaluation_source: str = Field(default="ollama", description="'ollama' or 'mock'")
    latency_seconds: Optional[float] = Field(default=None, description="Response latency in seconds")
    error_message: Optional[str] = Field(default=None, description="Error diagnostics if degraded")
    cognitive_elevations: dict = Field(default_factory=dict, description="Suggested question revisions for different Bloom levels")

    @field_validator("difficulty_score", mode="before")
    @classmethod
    def clamp_difficulty(cls, v):
        try:
            val = float(v)
            return round(max(1.0, min(10.0, val)), 1)
        except (ValueError, TypeError):
            return 5.0

    @field_validator("blooms_level_index", mode="before")
    @classmethod
    def compute_or_validate_index(cls, v, info):
        try:
            val = int(v)
            if 1 <= val <= 6:
                return val
        except (ValueError, TypeError):
            pass
        return 1


class BatchEvaluationSummary(BaseModel):
    """Aggregate statistics for a collection of evaluated questions."""
    total_questions: int
    average_difficulty: float
    level_counts: dict
    evaluations: List[QuestionEvaluation]
