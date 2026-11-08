# Results

Seven runs were made: three of Prompt A, four of Prompt B. Each was a fresh chat with only `deal_handoffs.csv` attached.

| File | Prompt | Status |
|---|---|---|
| A1.txt | A (vague) | Valid |
| A2.txt | A (vague) | Valid |
| A3.txt | A (vague) | Valid |
| B1_EXCLUDED.txt | B (structured) | Excluded. The model referred to "the reference table in your prompt file", so the answer table was visible to it. |
| B2.txt | B (structured) | Valid |
| B3.txt | B (structured) | Valid |
| B4.txt | B (structured) | Valid |

Note: the outputs were copied from the chat window into text files. Tables were reformatted as plain text or markdown. The wording is unchanged. Scoring is in `summary.md`.
