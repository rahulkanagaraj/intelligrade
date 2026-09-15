"""
pdf_extractor.py
----------------
Extracts clean, unformatted question text from standard university exam PDFs.
Uses pdfplumber with pypdf fallback.
Filters out university headers, page numbers, instructions, and section titles,
isolating questions into a clean structured list or CSV.
"""

import os
import re
import pandas as pd

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    try:
        import PyPDF2 as pypdf
        HAS_PYPDF = True
    except ImportError:
        HAS_PYPDF = False

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DEFAULT_OUTPUT_CSV = os.path.join(DATA_DIR, "extracted_questions.csv")

class ExamPDFExtractor:
    """Extracts questions from university exam PDFs."""

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found at '{pdf_path}'")

    def extract_raw_text(self) -> str:
        """Extract all raw text using pdfplumber (preferred) or pypdf (fallback)."""
        full_text = []

        if HAS_PDFPLUMBER:
            try:
                with pdfplumber.open(self.pdf_path) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text(layout=False) or ""
                        full_text.append(text)
                return "\n".join(full_text)
            except Exception as e:
                print(f"pdfplumber extraction failed ({e}), falling back to pypdf...")

        if HAS_PYPDF:
            reader = pypdf.PdfReader(self.pdf_path)
            for page in reader.pages:
                text = page.extract_text() or ""
                full_text.append(text)
            return "\n".join(full_text)

        raise RuntimeError("Neither pdfplumber nor pypdf/PyPDF2 is available in the Python environment.")

    def clean_and_parse_questions(self, raw_text: str) -> list:
        """
        Strips non-question boilerplate (headers, footers, general instructions)
        and parses individual questions.
        """
        lines = raw_text.splitlines()
        filtered_lines = []

        # Regex patterns to ignore boilerplate lines
        ignore_patterns = [
            r"DEPARTMENT OF", r"UNIVERSITY", r"INSTITUTE OF", r"EXAMINATION",
            r"Course:", r"Time Allowed:", r"Maximum Marks:", r"General Instructions:",
            r"Confidential Document", r"Answer all questions", r"scientific calculators",
            r"SECTION [A-Z]:", r"Page \d+ of \d+", r"^\s*-\s*\d+\s*-\s*$",
            r"^\d+\.\s*(Answer|Write|Non-programmable|Confidential|Calculators|Show all)"
        ]

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            # Check if line matches any noise pattern
            is_noise = any(re.search(pat, stripped, re.IGNORECASE) for pat in ignore_patterns)
            if is_noise:
                continue

            filtered_lines.append(stripped)

        cleaned_text = "\n".join(filtered_lines)

        # Pattern matching question headers: e.g. Q1., 1., Q12., Question 1:, 1.1, (a), (b)
        q_pattern = r"(?m)^(Q\d+[\.\:]?|\d+[\.\:]|\(?[a-z]\)\s+|Question\s+\d+[\.\:]?)"
        
        # Split text into chunks based on question identifiers
        matches = list(re.finditer(q_pattern, cleaned_text, re.MULTILINE))

        questions = []
        if not matches:
            # Fallback if no explicit numbered questions found: split by double line breaks
            chunks = [c.strip() for c in cleaned_text.split("\n\n") if len(c.strip()) > 15]
            for idx, chunk in enumerate(chunks, 1):
                questions.append({
                    "question_id": f"EXT_Q{idx:03d}",
                    "question_number": f"Q{idx}",
                    "question_text": self._sanitize_question_text(chunk),
                    "marks": self._extract_marks(chunk)
                })
            return questions

        for i in range(len(matches)):
            start_idx = matches[i].start()
            end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(cleaned_text)
            
            q_block = cleaned_text[start_idx:end_idx].strip()
            
            # Extract question identifier and content
            q_id_match = re.match(q_pattern, q_block)
            q_num = q_id_match.group(0).strip() if q_id_match else f"Q{i+1}"
            
            raw_q_text = q_block[len(q_num):].strip() if q_id_match else q_block
            clean_q_text = self._sanitize_question_text(raw_q_text)
            marks = self._extract_marks(q_block)

            if len(clean_q_text) > 5:
                questions.append({
                    "question_id": f"EXT_Q{i+1:03d}",
                    "question_number": q_num,
                    "question_text": clean_q_text,
                    "marks": marks
                })

        return questions

    def _sanitize_question_text(self, text: str) -> str:
        """Strips mark tags like [5 Marks] or (15 Marks) and cleans whitespace."""
        # Strip marks annotation
        text = re.sub(r"\[\d+\s*Marks\]", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\(\d+\s*Marks\)", "", text, flags=re.IGNORECASE)
        # Clean inline HTML breaks if present
        text = re.sub(r"<br\s*/?>", " ", text, flags=re.IGNORECASE)
        # Collapse multiple spaces and newlines
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _extract_marks(self, text: str) -> str:
        """Extracts mark count if specified, e.g., '[5 Marks]' -> '5'."""
        match = re.search(r"\[(\d+)\s*Marks\]", text, re.IGNORECASE) or re.search(r"\((\d+)\s*Marks\)", text, re.IGNORECASE)
        return match.group(1) if match else "N/A"

    def extract_to_dataframe(self) -> pd.DataFrame:
        raw_text = self.extract_raw_text()
        questions = self.clean_and_parse_questions(raw_text)
        return pd.DataFrame(questions)

def extract_questions_from_pdf(pdf_path: str, output_csv: str = DEFAULT_OUTPUT_CSV) -> pd.DataFrame:
    """High level function to extract questions from PDF and save as CSV."""
    extractor = ExamPDFExtractor(pdf_path)
    raw_text = extractor.extract_raw_text()
    questions = extractor.clean_and_parse_questions(raw_text)
    
    df = pd.DataFrame(questions)
    
    if output_csv:
        out_dir = os.path.dirname(output_csv)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        df.to_csv(output_csv, index=False)
        print(f"Extracted {len(df)} questions saved to '{output_csv}'")
        
    return df

if __name__ == "__main__":
    sample_pdf = os.path.join(DATA_DIR, "sample_university_exam.pdf")
    if os.path.exists(sample_pdf):
        print(f"Testing PDF Extraction on '{sample_pdf}'...")
        df_res = extract_questions_from_pdf(sample_pdf)
        print(df_res[["question_id", "question_number", "question_text", "marks"]].to_string())
    else:
        print(f"Sample PDF not found at {sample_pdf}. Run generate_sample_pdf.py first.")
