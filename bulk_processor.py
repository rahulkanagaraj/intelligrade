"""
bulk_processor.py
-----------------
Bulk Processing Engine for AI Question Analysis.
Ingests cleaned question datasets (50+ questions at once) and processes them through
the Bloom's taxonomy cognitive classifier pipeline without failure or timeout.
"""

import os
import re
import time
import pandas as pd
from typing import List, Dict, Any

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Keyword rules for Bloom's Taxonomy classification
BLOOM_KEYWORDS = {
    "Remember": {
        "depth": 1,
        "keywords": ["define", "list", "state", "recall", "name", "identify", "outline", "describe", "what is", "who", "when", "where"],
        "weight": 1.0
    },
    "Understand": {
        "depth": 2,
        "keywords": ["explain", "summarize", "discuss", "interpret", "classify", "contrast", "paraphrase", "in your own words", "why does", "meaning of"],
        "weight": 1.2
    },
    "Apply": {
        "depth": 3,
        "keywords": ["calculate", "demonstrate", "implement", "solve", "compute", "apply", "use", "construct", "execute", "determine"],
        "weight": 1.4
    },
    "Analyze": {
        "depth": 4,
        "keywords": ["analyze", "compare", "differentiate", "deconstruct", "investigate", "examine", "categorize", "bottleneck", "root cause", "trade-off"],
        "weight": 1.6
    },
    "Evaluate": {
        "depth": 5,
        "keywords": ["critique", "justify", "assess", "validate", "appraise", "judge", "recommend", "ethical", "trade-offs", "evaluate"],
        "weight": 1.8
    },
    "Create": {
        "depth": 6,
        "keywords": ["design", "formulate", "synthesize", "devise", "propose", "develop", "novel", "architecture", "framework", "construct an original"],
        "weight": 2.0
    }
}

class BulkQuestionProcessor:
    """Processes large batches of questions (50+ at once) efficiently."""

    def __init__(self, batch_size: int = 50):
        self.batch_size = batch_size

    def analyze_single_question(self, question_text: str, question_id: str = "") -> Dict[str, Any]:
        """Classifies a single question into Bloom's Taxonomy level with confidence score."""
        text_lower = question_text.lower()
        words = set(re.findall(r"\b\w+\b", text_lower))
        
        scores = {}
        matched_verbs = {}
        
        for level, info in BLOOM_KEYWORDS.items():
            matches = [kw for kw in info["keywords"] if kw in text_lower]
            scores[level] = len(matches) * info["weight"]
            if matches:
                matched_verbs[level] = matches
                
        # Determine top level
        best_level = max(scores, key=scores.get)
        max_score = scores[best_level]
        
        # Default fallback if no explicit keywords matched
        if max_score == 0:
            best_level = "Understand" # Default neutral taxonomy level
            confidence = 0.50
            action_verb = "N/A"
        else:
            total_score = sum(scores.values())
            confidence = min(0.98, max(0.60, round(max_score / total_score, 2))) if total_score > 0 else 0.70
            action_verb = matched_verbs.get(best_level, ["N/A"])[0]

        depth = BLOOM_KEYWORDS[best_level]["depth"]
        
        # Difficulty estimation
        word_count = len(text_lower.split())
        if depth <= 2 and word_count < 20:
            difficulty = "Easy"
        elif depth in [3, 4] or (20 <= word_count <= 40):
            difficulty = "Medium"
        else:
            difficulty = "Hard"

        return {
            "question_id": question_id,
            "question_text": question_text,
            "predicted_blooms_level": best_level,
            "confidence_score": confidence,
            "cognitive_depth": depth,
            "identified_action_verb": action_verb,
            "estimated_difficulty": difficulty,
            "word_count": word_count,
            "status": "Success"
        }

    def process_batch(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Ingests a list of questions (e.g. 50+ questions) and returns detailed results
        and throughput performance metrics.
        """
        start_time = time.time()
        processed_records = []
        errors_count = 0

        for idx, q_item in enumerate(questions):
            q_id = q_item.get("question_id", f"Q_{idx+1}")
            q_text = q_item.get("question_text", "")
            
            try:
                res = self.analyze_single_question(q_text, question_id=q_id)
                # Preserve original metadata if present
                if "marks" in q_item:
                    res["marks"] = q_item["marks"]
                if "blooms_level" in q_item:
                    res["actual_blooms_level"] = q_item["blooms_level"]
                processed_records.append(res)
            except Exception as err:
                errors_count += 1
                processed_records.append({
                    "question_id": q_id,
                    "question_text": q_text,
                    "predicted_blooms_level": "Error",
                    "confidence_score": 0.0,
                    "cognitive_depth": 0,
                    "identified_action_verb": "Error",
                    "estimated_difficulty": "Error",
                    "word_count": len(q_text.split()),
                    "status": f"Failed: {str(err)}"
                })

        elapsed_time = round(time.time() - start_time, 4)
        throughput_qps = round(len(questions) / elapsed_time, 2) if elapsed_time > 0 else len(questions)

        df_results = pd.DataFrame(processed_records)
        
        # Summary metrics
        level_distribution = df_results["predicted_blooms_level"].value_counts().to_dict() if not df_results.empty else {}
        difficulty_distribution = df_results["estimated_difficulty"].value_counts().to_dict() if not df_results.empty else {}
        avg_confidence = round(df_results["confidence_score"].mean(), 2) if not df_results.empty else 0.0

        return {
            "results_df": df_results,
            "total_questions": len(questions),
            "successful_questions": len(questions) - errors_count,
            "failed_questions": errors_count,
            "elapsed_time_seconds": elapsed_time,
            "questions_per_second": throughput_qps,
            "average_confidence": avg_confidence,
            "blooms_distribution": level_distribution,
            "difficulty_distribution": difficulty_distribution
        }

if __name__ == "__main__":
    # Test on 50 questions
    print("Testing Bulk Question Processor on 50 questions...")
    data_path = os.path.join(DATA_DIR, "blooms_taxonomy_8700.csv")
    if os.path.exists(data_path):
        df_sample = pd.read_csv(data_path).head(50)
        questions_input = df_sample.to_dict(orient="records")
        processor = BulkQuestionProcessor(batch_size=50)
        summary = processor.process_batch(questions_input)
        
        print(f"\n--- BULK TEST SUMMARY ---")
        print(f"Total Questions Analyzed: {summary['total_questions']}")
        print(f"Success Count: {summary['successful_questions']}")
        print(f"Failures Count: {summary['failed_questions']}")
        print(f"Elapsed Time: {summary['elapsed_time_seconds']} seconds")
        print(f"Throughput: {summary['questions_per_second']} QPS")
        print(f"Average Confidence: {summary['average_confidence']}")
        print(f"Bloom's Distribution: {summary['blooms_distribution']}")
        print(f"Difficulty Distribution: {summary['difficulty_distribution']}")
    else:
        print(f"Dataset not found at {data_path}. Run download_blooms_dataset.py first.")
