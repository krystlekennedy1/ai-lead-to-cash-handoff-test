# Results summary

Scored against `keys/answer_key.csv` and `keys/expected_metrics.csv`. B1 is excluded (the model could see the reference table).

| Measure | A1 | A2 | A3 | B2 | B3 | B4 |
|---|---|---|---|---|---|---|
| Scorecard cells correct (of 30) | not scoreable | not scoreable | not scoreable | 30 | 30 | 30 |
| Bottleneck (credit check, by excess days) | Partial | Partial | Partial | Yes | Yes | Yes |
| Concentration rows correct (of 5) | Partial | Partial | Partial | 5 | 5 | 5 |
| Stuck deals named (of 5) | 3 | 3 | 2 | 5 | 5 | 5 |
| Decoys wrongly flagged (of 3) | unclear | 1 implied | 0 | 0 | 0 | 0 |
| Sequence issues (of 6) | count only | 6 IDs | 6 IDs | 6 | 6 | 6 |
| High-friction deals (of 10) | 0 | 0 | 0 | 10 | 10 | 10 |
| Human-look items (of 7) | 1 | 4 | 4 | 7 | 7 | 7 |
| Projected savings claims | 0 | 2 | 3 | 0 | 0 | 0 |

## Findings

1. The vague prompt found a real pattern every time: large deals are slow at credit check. It did not produce a number that can be checked against an SLA.
2. All three vague runs ranked kickoff wait as the biggest delay by raw elapsed time. Against the 5-day SLA, kickoff is fourth in excess days. Credit check is first.
3. No vague run found the 10 high-friction deals. All three said rework does not matter, which is true for elapsed time and misses the cost.
4. Which stuck deals, missing steps and data problems the vague prompt found changed from run to run.
5. Two of three vague runs (A2, A3) included percentage "savings" the data cannot prove. The structured prompt forbids this and none appeared.
6. The structured prompt matched the key on every measured item in all three valid runs, including the rate-versus-days trap (legal has the highest breach rate, credit check loses the most days) and the four decoys.
7. Structured does not mean error-free. In B4, one sentence of explanation said legal's misses are small and credit check's are long. The data says the reverse: legal averages 4.0 excess days per breach, credit check 3.3. Credit check wins on volume. The rules locked the math, not the prose. A human or a self-check should read the "why" sentences.
8. All three vague runs flagged a gap of no closings between Oct 1 and Oct 19. That gap comes from how the synthetic data was built, not from any business reality.
