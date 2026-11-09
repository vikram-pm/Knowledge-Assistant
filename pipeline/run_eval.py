"""Step 3c: run all 25 test questions and write results into the test-set workbook.

Fills in "Actual tier" and puts the answer and cited sources in "Notes".
You still score correctness, claims and citations by hand: that human check
is what makes the hallucination and citation metrics credible.

Run:  python run_eval.py
"""
import time
from openpyxl import load_workbook
from assistant import ask

SRC = "P02_evaluation_test_set.xlsx"
OUT = "P02_evaluation_results.xlsx"

wb = load_workbook(SRC)
ws = wb["Test set"]
for row in range(2, ws.max_row + 1):
    q = ws[f"D{row}"].value
    if not q:
        continue
    r = ask(q)
    sources = ", ".join(c["doc_id"] for c in r["citations"]) or "none"
    ws[f"H{row}"] = r["tier"]
    ws[f"M{row}"] = f'{r["answer"] or "(escalated)"} | Sources: {sources} | {r["tier_reason"]}'
    print(f'{ws[f"A{row}"].value}: expected {ws[f"B{row}"].value}, got {r["tier"]} ({sources})')
    time.sleep(1)   # stay well inside free-tier rate limits

wb.save(OUT)
print(f"\nSaved {OUT}. Open it, score columns I–L, and check the Scorecard sheet.")
