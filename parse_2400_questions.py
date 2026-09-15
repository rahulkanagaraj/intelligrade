"""
parse_2400_questions.py
-----------------------
Parses the 2,400 Question Bank (covering 8 CS/EE/Math topics),
cleans text, extracts question numbers, assigns subjects,
and runs Bloom's Taxonomy AI classification.
Outputs data/question_bank_2400.csv.
"""

import os
import re
import pandas as pd
from bulk_processor import BulkQuestionProcessor

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
RAW_TXT_PATH = os.path.join(DATA_DIR, "raw_question_bank.txt")
CSV_OUTPUT_PATH = os.path.join(DATA_DIR, "question_bank_2400.csv")

def parse_raw_bank():
    if not os.path.exists(RAW_TXT_PATH):
        print(f"File {RAW_TXT_PATH} not found.")
        return None

    with open(RAW_TXT_PATH, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Define subject section headers
    subjects = [
        "Computer Networks",
        "Operating System",
        "Mathematics",
        "General Aptitude",
        "Programming and Data Structure",
        "Computer Organization and Architecture",
        "Digital Logic",
        "Theory of Computation"
    ]

    records = []
    
    # Try parsing CSV lines first if present
    csv_lines = [line.strip() for line in content.splitlines() if line.startswith("EXT_Q")]
    if len(csv_lines) >= 100:
        print(f"Found {len(csv_lines)} CSV formatted question lines.")
        current_subject = "Computer Science & Engineering"
        for line in csv_lines:
            parts = line.split(",", 3)
            if len(parts) >= 3:
                q_id = parts[0].strip()
                q_num = parts[1].strip()
                q_text = parts[2].strip().strip('"')
                
                if len(q_text) > 5:
                    records.append({
                        "question_id": q_id,
                        "question_number": f"Q{q_num}",
                        "question_text": q_text,
                        "subject": current_subject
                    })

    # If CSV lines were not sufficient, parse OCR section text
    if len(records) < 500:
        print("Parsing OCR section text...")
        lines = content.splitlines()
        current_subject = "General Computer Science"
        current_q_num = None
        current_q_text = []
        q_counter = 1

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            # Check for subject header
            for subj in subjects:
                if line_str == subj or line_str.startswith(f"==Start of OCR for page") and subj in line_str:
                    current_subject = subj
                    break

            # Match question start like "1. ", "2. ", "123. "
            q_match = re.match(r"^(\d{1,4})\.\s*(.*)", line_str)
            if q_match:
                if current_q_num and current_q_text:
                    full_q = " ".join(current_q_text).strip()
                    if len(full_q) > 5:
                        records.append({
                            "question_id": f"BANK_Q{q_counter:04d}",
                            "question_number": f"Q{current_q_num}",
                            "question_text": full_q,
                            "subject": current_subject
                        })
                        q_counter += 1
                current_q_num = q_match.group(1)
                current_q_text = [q_match.group(2)]
            elif current_q_num:
                # Filter out page headers / OCR markers
                if not line_str.startswith("==") and not line_str.startswith("Computer") and not line_str.startswith("Operating") and not line_str.startswith("Mathematics"):
                    current_q_text.append(line_str)

        # Append last question
        if current_q_num and current_q_text:
            full_q = " ".join(current_q_text).strip()
            if len(full_q) > 5:
                records.append({
                    "question_id": f"BANK_Q{q_counter:04d}",
                    "question_number": f"Q{current_q_num}",
                    "question_text": full_q,
                    "subject": current_subject
                })

    df = pd.DataFrame(records)
    
    # Run Bulk AI Processor to assign Bloom's Taxonomy & Difficulty
    print(f"Running Bulk AI Processor on {len(df)} extracted questions...")
    processor = BulkQuestionProcessor()
    processed_res = processor.process_batch(df.to_dict(orient="records"))
    res_df = processed_res["results_df"]
    
    res_df.to_csv(CSV_OUTPUT_PATH, index=False)
    print(f"Successfully processed and saved {len(res_df)} questions to '{CSV_OUTPUT_PATH}'!")
    return res_df

if __name__ == "__main__":
    parse_raw_bank()
