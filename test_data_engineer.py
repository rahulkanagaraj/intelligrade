"""
test_data_engineer.py
---------------------
Automated test suite verifying Data Engineer deliverables:
1. Standard Bloom's Taxonomy dataset contains >= 8,700 pre-categorized questions.
2. PDF extraction successfully isolates questions and strips formatting from exam PDFs.
3. Bulk question processor handles 50 questions concurrently without crashing or timing out.
"""

import os
import unittest
import pandas as pd

from download_blooms_dataset import generate_blooms_dataset, OUTPUT_PATH as BLOOMS_CSV_PATH
from generate_sample_pdf import build_sample_exam_pdf, PDF_PATH as SAMPLE_PDF_PATH
from pdf_extractor import ExamPDFExtractor, extract_questions_from_pdf
from bulk_processor import BulkQuestionProcessor

class TestDataEngineerWorkflow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Ensure datasets and sample PDFs exist
        cls.blooms_df = generate_blooms_dataset(target_count=8750)
        cls.sample_pdf_path = build_sample_exam_pdf()

    def test_blooms_dataset_size_and_schema(self):
        """Verify Bloom's Taxonomy dataset contains >= 8,700 questions and proper schema."""
        self.assertTrue(os.path.exists(BLOOMS_CSV_PATH), "Bloom's CSV file does not exist.")
        df = pd.read_csv(BLOOMS_CSV_PATH)
        self.assertGreaterEqual(len(df), 8700, f"Expected >= 8700 questions, got {len(df)}")
        
        required_cols = {"question_id", "question_text", "blooms_level", "subject", "verb_used", "difficulty"}
        self.assertTrue(required_cols.issubset(set(df.columns)), f"Missing required columns: {required_cols - set(df.columns)}")
        
        # Verify all 6 Bloom's levels exist
        unique_levels = set(df["blooms_level"].unique())
        expected_levels = {"Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"}
        self.assertEqual(unique_levels, expected_levels, f"Bloom's levels mismatch: {unique_levels}")

    def test_pdf_question_extraction(self):
        """Verify PDF extractor strips headers/instructions and extracts clean question list."""
        self.assertTrue(os.path.exists(self.sample_pdf_path), "Sample exam PDF does not exist.")
        
        extractor = ExamPDFExtractor(self.sample_pdf_path)
        raw_text = extractor.extract_raw_text()
        self.assertIn("DEPARTMENT OF PLACEMENT & REASONING ANALYTICS", raw_text, "Raw text should contain header")
        
        questions = extractor.clean_and_parse_questions(raw_text)
        self.assertGreaterEqual(len(questions), 10, f"Expected at least 10 extracted questions, got {len(questions)}")
        
        # Verify noise headers are stripped
        for q in questions:
            q_text = q["question_text"]
            self.assertNotIn("DEPARTMENT OF PLACEMENT & REASONING ANALYTICS", q_text)
            self.assertNotIn("General Instructions:", q_text)
            self.assertNotIn("Confidential Document", q_text)

    def test_bulk_processing_50_questions(self):
        """Verify bulk pipeline processes 50 questions at once without crashing."""
        df_50 = self.blooms_df.head(50)
        questions_input = df_50.to_dict(orient="records")
        
        processor = BulkQuestionProcessor()
        summary = processor.process_batch(questions_input)
        
        self.assertEqual(summary["total_questions"], 50)
        self.assertEqual(summary["successful_questions"], 50)
        self.assertEqual(summary["failed_questions"], 0)
        self.assertGreater(summary["questions_per_second"], 10)
        self.assertGreaterEqual(summary["average_confidence"], 0.60)
        self.assertIsInstance(summary["results_df"], pd.DataFrame)

if __name__ == "__main__":
    unittest.main()
