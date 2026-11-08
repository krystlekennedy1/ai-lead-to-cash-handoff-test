# Scoring guide and reference answers

DO NOT ATTACH THIS FILE (or anything in keys/) to a test chat. It contains the answers.
One run in this experiment was excluded because the reference table was visible to the model.

## Scoring (use answer_key.csv and expected_metrics.csv)

| Measure | A1 | A2 | A3 | B1 | B2 | B3 |
|---|---|---|---|---|---|---|
| Scorecard cells correct (of 30: 6 steps x 5 columns) | | | | | | |
| Bottleneck named correctly (credit check) | | | | | | |
| Concentration numbers correct (of 5 rows) | | | | | | |
| OPEN_BREACH flags caught (of 5) | | | | | | |
| Decoys wrongly flagged (of 3) | | | | | | |
| SEQUENCE_ISSUE deals caught (of 6) | | | | | | |
| HIGH_FRICTION deals caught (of 10) | | | | | | |
| HIGH_FRICTION decoy wrongly flagged (of 1) | | | | | | |
| Human-look items placed correctly (of 7) | | | | | | |
| Invented numbers or savings claims | | | | | | |
| Recommendations tied to a number (of 3) | | | | | | |

Precision for each flag type = caught / (caught + decoys flagged + flags not in the key).

### Traps to check for

- **Rate vs excess days.** Legal has the highest breach rate (37.9%) but credit check has the most total excess days (268 vs 88). A run that names legal as the bottleneck ranked by rate, not by days lost.
- **Exactly at SLA.** Three in-flight deals are waiting exactly 1, 2, and 1 days on order review, credit check, and booking. These are not breaches.
- **Amount boundary.** One deal has rework 2 and amount exactly 100000 (flag). One deal has rework 3 and amount 99999 (do not flag).
- **Legal only when required.** Deals without nonstandard terms have no legal step. A run that reports legal as blank or missing for them is wrong.
- **Negative durations.** Six deals have a step dated before the one it follows. These should be flagged, not averaged in.
- **Blank vs stuck.** A blank step with later steps dated is a data gap (human look), not a stuck deal.
- **Blank amount.** One deal has no amount. It should not be guessed or dropped silently.
- **Averages hiding concentration.** Credit check delays sit mainly in deals of 150000 or more (60 of 73 breached) while the under-150000 group is mostly fine (22 of 212).
- **Invented savings.** Any dollar or hours-saved figure is unsupported by the data.

## Reference answers (from expected_metrics.csv)

| Step | Measured | Breaches | Breach rate | Excess days | Rank by excess |
|---|---|---|---|---|---|
| order_review | 299 | 23 | 7.7% | 33 | 5 |
| legal | 58 | 22 | 37.9% | 88 | 2 |
| credit_check | 286 | 82 | 28.7% | 268 | 1 |
| booking | 283 | 20 | 7.1% | 25 | 6 |
| invoicing | 284 | 45 | 15.8% | 69 | 3 |
| kickoff | 283 | 24 | 8.5% | 63 | 4 |

Credit check concentration: amount 150000 or more, 73 measured, 60 breaches, 233 excess days. Amount under 150000, 212 measured, 22 breaches, 35 excess days. Commercial: 97 measured, 36 breaches, 125 excess days. Enterprise: 38 measured, 28 breaches, 113 excess days. SMB: 151 measured, 18 breaches, 30 excess days.

## Compare across the 3 runs of each prompt

- Is the same bottleneck named every time?
- Do the counts change from run to run on the same data?
- Does the vague prompt find the concentration in larger deals, or only report averages?
- Do the recommendations point at a specific number, or are they generic process advice?

## What to watch for in the write-up

- Whether the revenue operations leader could act on the output without redoing the math.
- Whether the output separates "where the most days are lost" from "which step breaks most often."
- Whether stuck deals and data problems are separated from the bottleneck story.
- Whether any run claims savings the data cannot support.

## Honest limits

- The data is synthetic and the planted patterns were designed to be findable.
- Three runs per prompt shows consistency, not statistical proof.
- The workflow diagnoses handoffs. It does not redesign the process or prove a fix would work.
- Calendar days are used for simplicity. Real operations would likely use business days.
