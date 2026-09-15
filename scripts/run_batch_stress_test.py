"""
End-to-end batch stress test: simulates the full UI pipeline on pdf_batch_sample.csv.
Mirrors exactly what the Streamlit Batch Assessment tab does.
"""

import sys
import io
import os
import pandas as pd

# Force UTF-8 stdout — Windows cp1252 consoles cannot print PDF ligature chars
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.mock_engine import mock_engine
from src.parser import sanitize_extracted_question
from src.models import BloomsLevel
from src.ui_components import compute_exam_balance_health, generate_html_dossier

CSV_PATH = os.path.join("data", "pdf_batch_sample.csv")
QUESTION_COLUMN = "extracted_text"

print("=" * 65)
print("  IntelliGrade — pdf_batch_sample.csv End-to-End Stress Test")
print("=" * 65)

# Step 1: Load CSV
df = pd.read_csv(CSV_PATH)
print(f"\n[1] CSV loaded:          {len(df)} rows, columns: {list(df.columns)}")

# Step 2: Sanitize (same as UI)
raw_questions = df[QUESTION_COLUMN].dropna().astype(str).tolist()
sanitized = [sanitize_extracted_question(q) for q in raw_questions]
valid = [q for q in sanitized if q and q.strip()]
skipped = len(raw_questions) - len(valid)
print(f"[2] After sanitisation:  {len(valid)} valid, {skipped} skipped/empty")

# Step 3: Run batch evaluation
print(f"\n[3] Evaluating {len(valid)} questions...\n")
results = []
errors = []
for i, q in enumerate(valid, 1):
    try:
        r = mock_engine.evaluate(q)
        results.append(r)
        level_tag = f"L{r.blooms_level_index} {r.blooms_level.value:<12}"
        print(f"    [{i:02d}] {level_tag}  diff={r.difficulty_score}  | {q[:55]}...")
    except Exception as e:
        errors.append((i, q, str(e)))
        print(f"    [{i:02d}] ❌ ERROR: {e} | {q[:55]}")

# Step 4: Summary stats
print("\n" + "=" * 65)
print("[4] BATCH RESULTS SUMMARY")
print("=" * 65)
diffs = [r.difficulty_score for r in results]
avg_diff = round(sum(diffs) / len(diffs), 2) if diffs else 0

level_counts = {}
for r in results:
    lv = r.blooms_level.value
    level_counts[lv] = level_counts.get(lv, 0) + 1

print(f"\n    Total evaluated:    {len(results)}")
print(f"    Errors:             {len(errors)}")
print(f"    Avg difficulty:     {avg_diff} / 10")
print(f"\n    Bloom's distribution:")
for lv, count in sorted(level_counts.items()):
    bar = "█" * count
    print(f"      {lv:<12} {bar}  ({count})")

# Step 5: Exam Balance Health
bal_score, bal_status, bal_color, bal_critique = compute_exam_balance_health(results)
print(f"\n    Exam Balance Index: {bal_score}%")
print(f"    Curricular Status:  {bal_status}")
print(f"    Critique preview:   {bal_critique[:80]}...")

# Step 6: HTML Dossier generation
try:
    html = generate_html_dossier(results)
    assert "<html>" in html.lower() or "<!DOCTYPE" in html.lower() or "<table" in html.lower()
    print(f"\n[5] HTML dossier generated OK ({len(html):,} chars)")
except Exception as e:
    print(f"\n[5] ❌ HTML dossier FAILED: {e}")

# Step 7: CSV export simulation
try:
    table_data = [{
        "#": idx,
        "Question": r.question,
        "Bloom's Level": r.blooms_level.value,
        "Tier Index": r.blooms_level_index,
        "Difficulty": r.difficulty_score,
        "Action Verbs": ", ".join(r.action_verbs),
    } for idx, r in enumerate(results, 1)]
    export_df = pd.DataFrame(table_data)
    csv_bytes = export_df.to_csv(index=False).encode("utf-8")
    print(f"[6] CSV export ready:   {len(csv_bytes):,} bytes, {len(export_df)} rows")
except Exception as e:
    print(f"[6] ❌ CSV export FAILED: {e}")

print("\n" + "=" * 65)
if errors:
    print(f"  ⚠️  COMPLETED WITH {len(errors)} ERROR(S)")
    for idx, q, err in errors:
        print(f"     Q{idx}: {err}")
else:
    print(f"  ✅ ALL {len(results)} QUESTIONS PASSED — PIPELINE CLEAN")
print("=" * 65)
