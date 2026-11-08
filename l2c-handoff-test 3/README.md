# Lead-to-Cash Handoff Diagnostic: Vague vs Structured Prompt Test

Where do closed-won deals lose time before the customer is live, and can an AI find it reliably?

This is a small, scored experiment on **synthetic data**. Ridgeline Distribution Co. is fictional. No real company, employee, customer, or system data is used anywhere in this repo.

## The setup

- 300 synthetic deals with the date each handoff was completed: order review, legal (only when terms are nonstandard), credit check, booking, invoicing, kickoff.
- Planted in the data: a bottleneck, stuck deals, deals sitting exactly at an SLA (decoys), out-of-order dates, high-friction deals with an amount just under the cutoff (decoy), skipped steps, and a blank amount.
- An answer key, plus a separate verification script that recomputes everything from the CSV and confirms the key.
- Two prompts. **A** is one vague sentence. **B** gives SLAs, rules, and an output format.
- Each prompt run in fresh chats, with only the CSV attached.

## The trap

Legal has the highest breach rate (37.9%). Credit check loses the most days (268 vs 88). A reader who ranks by breach rate fixes the wrong step.

## Results

| | Vague prompt (3 runs) | Structured prompt (3 valid runs) |
|---|---|---|
| Scorecard numbers checkable against SLAs | None | 30 of 30 cells, every run |
| Named credit check as the bottleneck by days lost | No. Ranked by raw elapsed time, kickoff first | Yes, every run |
| Stuck deals found (of 5) | 2 to 3 | 5, every run |
| High-friction deals found (of 10) | 0 | 10, every run |
| Human-look items found (of 7) | 1 to 4 | 7, every run |
| Projected savings claims | 2 of 3 runs | 0 |

The vague prompt found a real pattern (large deals are slow at credit check) and wrote a plausible story each time. It never produced a number anyone could audit, and what it found around the edges changed from run to run.

Full outputs are in `results/`. Scoring detail is in `results/summary.md`.

## Limits, stated plainly

- Synthetic data. The patterns were designed to be findable. This tests whether a method finds planted problems, not whether it would work on a messy real system.
- Three runs per prompt shows consistency, not statistical proof.
- The structured prompt still slipped once: in one run an explanation sentence said legal's misses were small and credit check's were long. The data says the opposite. The rules protected the math, not the wording. Read the "why" sentences.
- One structured run was excluded because the model could see the reference answers. It is kept in `results/` and labeled.
- The data has no closings between Oct 1 and Oct 19. This is an artifact of how it was built, and the vague runs flagged it.
- Calendar days, not business days.
- Outputs were copied from the chat window into text files. Tables were reformatted. Wording is unchanged.
- The experiment diagnoses handoffs. It does not redesign the process or prove a fix would work.

## What this means in practice

If you want an AI to analyze operations data you can trust, give it the rules and the output format, make it show counts, and have a person check the reasoning. Put the exact rules in code where you can, and use the model for the judgment and the write-up.

## Run it yourself

1. Open a fresh chat. Attach only `deal_handoffs.csv`.
2. Paste Prompt A or Prompt B from `prompts.md`.
3. Compare the output to `scoring.md` and `keys/`. Do not attach those files to a test chat.
4. To confirm the key is correct: `python3 scripts/verify_l2c.py` from the repo root.

`scripts/generate_l2c.py` rebuilds the dataset (seed 21). Run it in an empty folder, then move the three CSVs it writes into place.

## Files

- `deal_handoffs.csv`: the test data
- `prompts.md`: Prompt A and Prompt B
- `scoring.md`: scoring table, traps, reference answers (do not attach)
- `keys/`: answer key and expected metrics (do not attach)
- `scripts/`: generator and verifier
- `results/`: all runs and the scored summary
