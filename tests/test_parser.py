"""Unit tests for JSON parser, repair routines, and Bloom's classification."""

import unittest
from src.models import BloomsLevel, QuestionEvaluation
from src.parser import (
    clean_markdown_fences,
    extract_json_substring,
    repair_json_string,
    normalize_blooms_level,
    parse_evaluation_response,
)


class TestParser(unittest.TestCase):
    """Test suite for resilient parsing of model outputs."""

    def test_clean_markdown_fences_simple(self):
        sample = "```json\n{\"test\": 123}\n```"
        cleaned = clean_markdown_fences(sample)
        self.assertEqual(cleaned, '{"test": 123}')

    def test_clean_markdown_fences_without_json_tag(self):
        sample = "```\n{\"test\": 456}\n```"
        cleaned = clean_markdown_fences(sample)
        self.assertEqual(cleaned, '{"test": 456}')

    def test_extract_json_substring_with_conversational_text(self):
        sample = (
            "Here is the evaluation you requested:\n"
            "{\n"
            '  "blooms_level": "Apply",\n'
            '  "difficulty_score": 6.5\n'
            "}\n"
            "I hope this helps your pedagogical review!"
        )
        extracted = extract_json_substring(sample)
        self.assertTrue(extracted.startswith("{"))
        self.assertTrue(extracted.endswith("}"))
        self.assertIn('"blooms_level": "Apply"', extracted)

    def test_repair_trailing_commas(self):
        sample = '{"items": [1, 2, 3,], "name": "test",}'
        repaired = repair_json_string(sample)
        self.assertEqual(repaired, '{"items": [1, 2, 3], "name": "test"}')

    def test_normalize_blooms_level(self):
        self.assertEqual(normalize_blooms_level("remember"), BloomsLevel.REMEMBER)
        self.assertEqual(normalize_blooms_level("Remembering"), BloomsLevel.REMEMBER)
        self.assertEqual(normalize_blooms_level("UNDERSTAND"), BloomsLevel.UNDERSTAND)
        self.assertEqual(normalize_blooms_level("comprehension"), BloomsLevel.UNDERSTAND)
        self.assertEqual(normalize_blooms_level("application"), BloomsLevel.APPLY)
        self.assertEqual(normalize_blooms_level("Analysis"), BloomsLevel.ANALYZE)
        self.assertEqual(normalize_blooms_level("evaluation"), BloomsLevel.EVALUATE)
        self.assertEqual(normalize_blooms_level("Creation"), BloomsLevel.CREATE)
        self.assertEqual(normalize_blooms_level("unknown"), BloomsLevel.UNDERSTAND)

    def test_parse_valid_json_response(self):
        raw = (
            "```json\n"
            "{\n"
            '  "question": "Calculate the terminal velocity of a falling sphere in water.",\n'
            '  "blooms_level": "Apply",\n'
            '  "blooms_level_index": 3,\n'
            '  "difficulty_score": 6.2,\n'
            '  "pedagogical_reasoning": "Requires procedural execution of Stokes law.",\n'
            '  "improvement_suggestions": "Add turbulent flow constraints to elevate to Analyze.",\n'
            '  "action_verbs": ["calculate"],\n'
            '  "keywords_identified": ["terminal velocity", "sphere", "water"]\n'
            "}\n"
            "```"
        )
        res = parse_evaluation_response(raw, original_question="Calculate terminal velocity")
        self.assertIsInstance(res, QuestionEvaluation)
        self.assertEqual(res.blooms_level, BloomsLevel.APPLY)
        self.assertEqual(res.blooms_level_index, 3)
        self.assertEqual(res.difficulty_score, 6.2)
        self.assertIn("calculate", res.action_verbs)

    def test_parse_noisy_markdown_response(self):
        raw = (
            "Certainly! As an academic psychometrician, here is my review:\n\n"
            "```json\n"
            "{\n"
            '  "question": "Design a fault-tolerant distributed cache.",\n'
            '  "blooms_level": "Create",\n'
            '  "blooms_level_index": 6,\n'
            '  "difficulty_score": 9.2,\n'
            '  "pedagogical_reasoning": "Demands architectural synthesis.",\n'
            '  "improvement_suggestions": "Add latency budget constraints.",\n'
            '  "action_verbs": ["design"],\n'
            '  "keywords_identified": ["cache", "distributed", "fault-tolerant"],\n'
            "}\n"
            "```\n"
            "Feel free to ask for revisions."
        )
        res = parse_evaluation_response(raw, original_question="Design a cache")
        self.assertIsInstance(res, QuestionEvaluation)
        self.assertEqual(res.blooms_level, BloomsLevel.CREATE)
        self.assertEqual(res.blooms_level_index, 6)
        self.assertEqual(res.difficulty_score, 9.2)

    def test_parse_empty_or_malformed_string_does_not_crash(self):
        res_empty = parse_evaluation_response("", original_question="Test Q")
        self.assertIsInstance(res_empty, QuestionEvaluation)
        self.assertIsNotNone(res_empty.error_message)

        res_garbage = parse_evaluation_response(
            "This is an unparseable response with no brackets at all", original_question="Test Q"
        )
        self.assertIsInstance(res_garbage, QuestionEvaluation)
        self.assertEqual(res_garbage.question, "Test Q")


if __name__ == "__main__":
    unittest.main()
