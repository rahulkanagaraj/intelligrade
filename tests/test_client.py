"""Unit tests for OllamaClient and MockEngine."""

import unittest
from src.mock_engine import mock_engine
from src.models import BloomsLevel, QuestionEvaluation
from src.ollama_client import OllamaClient


class TestClientAndMockEngine(unittest.TestCase):
    """Test suite for client operations and mock cognitive engine."""

    def setUp(self):
        self.client = OllamaClient()

    def test_mock_engine_remember(self):
        q = "Define what is an eigenvalue and state its algebraic definition."
        result = mock_engine.evaluate(q)
        self.assertIsInstance(result, QuestionEvaluation)
        self.assertEqual(result.blooms_level, BloomsLevel.REMEMBER)
        self.assertEqual(result.blooms_level_index, 1)
        self.assertLessEqual(result.difficulty_score, 5.0)

    def test_mock_engine_understand(self):
        q = "Explain the difference between synchronous and asynchronous execution in Python."
        result = mock_engine.evaluate(q)
        self.assertEqual(result.blooms_level, BloomsLevel.UNDERSTAND)
        self.assertEqual(result.blooms_level_index, 2)

    def test_mock_engine_apply(self):
        q = "Calculate the acceleration of a 5kg mass subjected to a net force of 25 Newtons."
        result = mock_engine.evaluate(q)
        self.assertEqual(result.blooms_level, BloomsLevel.APPLY)
        self.assertEqual(result.blooms_level_index, 3)

    def test_mock_engine_analyze(self):
        q = "Compare and contrast Monolithic and Microservice software architectures in terms of scalability and failure blast radius."
        result = mock_engine.evaluate(q)
        self.assertEqual(result.blooms_level, BloomsLevel.ANALYZE)
        self.assertEqual(result.blooms_level_index, 4)

    def test_mock_engine_evaluate(self):
        q = "Critique and judge the ethical implications of autonomous weapon systems in international law."
        result = mock_engine.evaluate(q)
        self.assertEqual(result.blooms_level, BloomsLevel.EVALUATE)
        self.assertEqual(result.blooms_level_index, 5)

    def test_mock_engine_create(self):
        q = "Design and formulate a real-time fault-tolerant distributed telemetry pipeline handling 100k events/sec."
        result = mock_engine.evaluate(q)
        self.assertEqual(result.blooms_level, BloomsLevel.CREATE)
        self.assertEqual(result.blooms_level_index, 6)
        self.assertGreaterEqual(result.difficulty_score, 8.0)

    def test_client_evaluate_single_question_in_mock_mode(self):
        q = "Solve for x in 2x + 7 = 19."
        res = self.client.evaluate_question(q, force_mock=True)
        self.assertIsInstance(res, QuestionEvaluation)
        self.assertEqual(res.blooms_level, BloomsLevel.APPLY)
        self.assertEqual(res.evaluation_source, "mock")

    def test_client_evaluate_batch(self):
        questions = [
            "What is Ohm's law?",
            "Calculate resistance when voltage is 10V and current is 2A.",
            "Design a bridge circuit that minimizes noise interference."
        ]
        batch_results = self.client.evaluate_batch(questions, force_mock=True)
        self.assertEqual(len(batch_results), 3)
        self.assertEqual(batch_results[0].blooms_level, BloomsLevel.REMEMBER)
        self.assertEqual(batch_results[1].blooms_level, BloomsLevel.APPLY)
        self.assertEqual(batch_results[2].blooms_level, BloomsLevel.CREATE)

    def test_mock_engine_generates_cognitive_elevations(self):
        q = "Define the speed of light in vacuum."
        res = mock_engine.evaluate(q)
        self.assertIsInstance(res.cognitive_elevations, dict)
        self.assertIn("Apply (Level 3)", res.cognitive_elevations)
        self.assertIn("Create (Level 6)", res.cognitive_elevations)

    def test_exam_balance_health_and_html_dossier(self):
        from src.ui_components import compute_exam_balance_health, generate_html_dossier
        questions = [
            "Define speed of light.",
            "Explain how refraction occurs.",
            "Calculate index of refraction given angle 30 degrees.",
            "Compare optical fiber vs copper wire signal loss.",
            "Critique the feasibility of quantum key distribution across satellites.",
            "Design an optical switching matrix for a petabit datacenter."
        ]
        results = self.client.evaluate_batch(questions, force_mock=True)
        score, status, color, critique = compute_exam_balance_health(results)
        self.assertIsInstance(score, int)
        self.assertGreaterEqual(score, 50)
        self.assertIsInstance(status, str)
        self.assertIsInstance(critique, str)

        html_out = generate_html_dossier(results, course_title="Physics 201 Exam")
        self.assertIn("IntelliGrade Pedagogical Audit Dossier", html_out)
        self.assertIn("Physics 201 Exam", html_out)
        self.assertIn("Exam Balance Index", html_out)


class TestWeightedKeywordFallback(unittest.TestCase):
    """Tests specifically targeting the Data Engineer (rahulkanagaraj) weighted keyword classifier.

    These questions deliberately avoid canonical Bloom's action verbs so that
    Pass 1 (verb taxonomy) finds nothing and Pass 2 (weighted scoring) takes over.
    """

    def test_weighted_fallback_investigate_maps_to_analyze(self):
        """'investigate' is a weighted keyword for Analyze — not in our verb taxonomy."""
        from src.mock_engine import _weighted_keyword_classify
        from src.models import BloomsLevel
        result = _weighted_keyword_classify("investigate the root cause of memory leaks in distributed systems")
        self.assertIsNotNone(result)
        level, keywords = result
        self.assertEqual(level, BloomsLevel.ANALYZE)
        self.assertIn("investigate", keywords)

    def test_weighted_fallback_propose_maps_to_create(self):
        """'propose' is in the Create weighted keywords but not the verb taxonomy."""
        from src.mock_engine import _weighted_keyword_classify
        from src.models import BloomsLevel
        result = _weighted_keyword_classify("propose a novel approach to optimise database index performance")
        self.assertIsNotNone(result)
        level, _ = result
        self.assertEqual(level, BloomsLevel.CREATE)

    def test_weighted_fallback_activates_in_full_evaluation(self):
        """End-to-end: question with only weighted keywords (no verb taxonomy match) still classifies correctly."""
        # 'discuss' is a weighted keyword for Understand but not in VERB_TAXONOMY
        q = "In your own words, summarize the meaning of Heisenberg's Uncertainty Principle."
        result = mock_engine.evaluate(q)
        self.assertIsInstance(result, QuestionEvaluation)
        # Should resolve to Understand via weighted keywords ('summarize', 'meaning of')
        self.assertEqual(result.blooms_level, BloomsLevel.UNDERSTAND)

    def test_weighted_fallback_returns_none_on_empty_text(self):
        """Weighted classifier should return None when no keywords match at all."""
        from src.mock_engine import _weighted_keyword_classify
        result = _weighted_keyword_classify("xyzzy quux lorem ipsum")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()

