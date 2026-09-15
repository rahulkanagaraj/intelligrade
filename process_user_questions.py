"""
process_user_questions.py
-------------------------
Parses the user's raw input exam text (50 questions), strips formatting headers,
isolates question statements and options into clean text, saves to CSV,
and runs through the Bulk Processing AI pipeline.
"""

import os
import re
import pandas as pd
from bulk_processor import BulkQuestionProcessor

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
INPUT_TXT = os.path.join(DATA_DIR, "user_exam_questions.txt")
OUTPUT_CSV = os.path.join(DATA_DIR, "extracted_user_questions.csv")

def parse_user_questions():
    with open(INPUT_TXT, "r", encoding="utf-8") as f:
        raw_content = f.read()

    # Split by separator or Question header
    blocks = re.split(r"--------------------------|===\s*Question\s+\d+\s+of\s+\d+\s*===", raw_content)
    
    extracted = []
    q_index = 1

    for block in blocks:
        block = block.strip()
        if not block:
            continue
            
        # Parse statement/prompt and options
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        
        # Remove any lingering header line
        lines = [l for l in lines if not re.match(r"^===\s*Question", l, re.IGNORECASE)]
        
        if not lines:
            continue
            
        # Extract main text vs options
        main_text_parts = []
        options_parts = []
        
        for line in lines:
            if re.match(r"^[A-D]\)", line):
                options_parts.append(line)
            else:
                # Remove "Statement: " prefix if present
                clean_line = re.sub(r"^Statement:\s*", "", line, flags=re.IGNORECASE)
                main_text_parts.append(clean_line)

        question_stem = " ".join(main_text_parts).strip()
        options_text = " | ".join(options_parts).strip()
        
        full_clean_question = f"{question_stem} Options: {options_text}" if options_text else question_stem

        extracted.append({
            "question_id": f"USER_Q{q_index:03d}",
            "question_number": f"Q{q_index}",
            "question_stem": question_stem,
            "options": options_text,
            "question_text": full_clean_question
        })
        q_index += 1

    df = pd.DataFrame(extracted)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Extracted {len(df)} questions saved cleanly to '{OUTPUT_CSV}'")
    return df

def main():
    df_questions = parse_user_questions()
    
    print("\n--- RUNNING BULK AI ANALYSIS ON 50 USER QUESTIONS ---")
    processor = BulkQuestionProcessor()
    summary = processor.process_batch(df_questions.to_dict(orient="records"))
    
    print(f"Total Questions Analyzed: {summary['total_questions']}")
    print(f"Success Count: {summary['successful_questions']}")
    print(f"Latency: {summary['elapsed_time_seconds']} sec ({summary['questions_per_second']} QPS)")
    print(f"Average Confidence: {summary['average_confidence']}")
    print(f"Bloom's Distribution: {summary['blooms_distribution']}")
    print(f"Difficulty Breakdown: {summary['difficulty_distribution']}")

if __name__ == "__main__":
    main()
