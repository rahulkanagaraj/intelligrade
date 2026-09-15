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


if __name__ == "__main__":
    unittest.main()
