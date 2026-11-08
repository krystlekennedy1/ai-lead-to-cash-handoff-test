# Prompts

Use a fresh chat for every run. Attach only `deal_handoffs.csv`. Do not attach anything from `keys/` or `scoring.md`.

## Prompt A (vague)

```
Here is our deal handoff data from closed-won to kickoff. Where are we losing time and what should we fix?
```

## Prompt B (structured)

```
You are an operations analyst advising the revenue operations leader of a mid-sized sales organization. The attached CSV has one row per closed-won deal and the date each handoff step was completed. Diagnose where deals lose time, using only the rules below. Today is 2026-11-07.

HANDOFF STEPS AND SLAs (calendar days)

Each handoff is measured from the previous required step date to its own date. The first step is measured from closed_won_date.

- order_review (column order_review_date): SLA 1 day
- legal (column legal_date): SLA 3 days, required only when nonstandard_terms = Y
- credit_check (column credit_check_date): SLA 2 days
- booking (column booked_date): SLA 1 day
- invoicing (column invoice_date): SLA 2 days
- kickoff (column kickoff_date): SLA 5 days

RULES

1. A handoff is measured only when both its own date and the previous required step date exist.
2. A breach is a duration strictly greater than the SLA. Exactly at the SLA is not a breach.
3. Excess days = max(0, duration minus SLA).
4. A negative duration is not measured. Flag the deal as SEQUENCE_ISSUE.
5. OPEN_BREACH: the next required step is blank, no later step is dated, and today minus the last completed date is greater than that step's SLA. Exactly at the SLA is not a breach.
6. HIGH_FRICTION: rework_count is 2 or more AND amount is 100000 or more.
7. MISSING_STEP (needs a human look): a required step is blank but a later step is dated.
8. A blank amount goes under "Needs a human look". Do not guess a value.
9. Never invent fields or numbers. Only give counts you actually computed. Do not estimate dollar savings.

OUTPUT FORMAT

1. Headline (2 sentences max): the single most important finding for the revenue operations leader.
2. Handoff scorecard: a table with, for each step, deals measured, breaches, breach rate, total excess days, rank by excess days.
3. Bottleneck: name the step with the most total excess days. State whether it differs from the step with the highest breach rate, and why that matters.
4. Where the bottleneck concentrates: break the bottleneck step down by deal size (amount 150000 or more vs under) and by segment, with measured, breaches, and excess days for each.
5. Stuck right now: list OPEN_BREACH deals with the step waiting and days waiting.
6. Data problems: SEQUENCE_ISSUE deals.
7. High-friction deals: list HIGH_FRICTION deals.
8. Needs a human look: items with the reason, or "None."
9. Recommendations (3 max): each tied to a specific number above. No invented savings.

Keep prose short. Plain language for an executive audience.
```
