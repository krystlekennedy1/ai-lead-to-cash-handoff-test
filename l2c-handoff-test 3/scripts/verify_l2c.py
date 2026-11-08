"""Recompute every handoff metric and row-level finding from deal_handoffs.csv.

Usage (from the repo root): python3 scripts/verify_l2c.py
Compares the results to expected_metrics.csv and answer_key.csv.
A clean run means the key matches the rules exactly.
"""
import csv
from datetime import date

AS_OF = date(2026, 11, 7)
SLA = {"order_review": 1, "legal": 3, "credit_check": 2, "booking": 1, "invoicing": 2, "kickoff": 5}
COLUMN = {"order_review": "order_review_date", "legal": "legal_date", "credit_check": "credit_check_date",
          "booking": "booked_date", "invoicing": "invoice_date", "kickoff": "kickoff_date"}

def parse(s):
    return date.fromisoformat(s) if s else None

deals = list(csv.DictReader(open("deal_handoffs.csv")))
key = list(csv.DictReader(open("keys/answer_key.csv")))

measured = {h: [] for h in SLA}      # (deal, days)
found = {"FLAG": set(), "NHL": set()}

for d in deals:
    required = ["order_review"] + (["legal"] if d["nonstandard_terms"] == "Y" else []) + \
               ["credit_check", "booking", "invoicing", "kickoff"]
    dates = [parse(d["closed_won_date"])] + [parse(d[COLUMN[s]]) for s in required]
    names = ["closed_won"] + required

    # handoff measurements
    for i in range(1, len(dates)):
        if dates[i] is not None and dates[i - 1] is not None:
            days = (dates[i] - dates[i - 1]).days
            if days < 0:
                found["FLAG"].add((d["deal_id"], "SEQUENCE_ISSUE"))
            else:
                measured[names[i]].append((d, days))

    # stuck right now: first blank step with nothing dated after it
    blank_positions = [i for i in range(1, len(dates)) if dates[i] is None]
    if blank_positions:
        first = blank_positions[0]
        later_dated = any(dates[j] is not None for j in range(first + 1, len(dates)))
        if not later_dated:
            if (AS_OF - dates[first - 1]).days > SLA[names[first]]:
                found["FLAG"].add((d["deal_id"], "OPEN_BREACH"))
        else:
            found["NHL"].add((d["deal_id"], "MISSING_STEP"))

    if d["amount"] == "":
        found["NHL"].add((d["deal_id"], "AMOUNT_BLANK"))
    elif int(d["rework_count"]) >= 2 and int(d["amount"]) >= 100000:
        found["FLAG"].add((d["deal_id"], "HIGH_FRICTION"))

key_flag = {(k["deal_id"], k["category"]) for k in key if k["expected_action"] == "FLAG"}
key_nhl = {(k["deal_id"], k["category"]) for k in key if k["expected_action"] == "NEEDS_HUMAN_LOOK"}
key_dnf = {(k["deal_id"], k["category"]) for k in key if k["expected_action"] == "DO_NOT_FLAG"}

print("Row-level findings")
print("  Flags in key but not found:", sorted(key_flag - found["FLAG"]) or "none")
print("  Flags found but not in key:", sorted(found["FLAG"] - key_flag) or "none")
print("  Human-look in key but not found:", sorted(key_nhl - found["NHL"]) or "none")
print("  Human-look found but not in key:", sorted(found["NHL"] - key_nhl) or "none")
print("  Decoys that trigger a rule:", sorted(key_dnf & (found["FLAG"] | found["NHL"])) or "none")

# metrics
def summarize(rows, sla):
    breaches = [days - sla for _, days in rows if days > sla]
    return len(rows), len(breaches), sum(breaches)

problems = []
expected = list(csv.DictReader(open("keys/expected_metrics.csv")))
excess_by_handoff = {h: summarize(measured[h], SLA[h])[2] for h in SLA}
top = max(excess_by_handoff, key=excess_by_handoff.get)
for e in expected:
    if e["section"] == "handoff":
        n, b, x = summarize(measured[e["label"]], SLA[e["label"]])
        rate = round(100 * b / n, 1)
        got = (n, b, rate, x)
        want = (int(e["measured"]), int(e["breaches"]), float(e["breach_rate_pct"]), int(e["total_excess_days"]))
        if got != want:
            problems.append((e["label"], "got", got, "want", want))
    else:
        label = e["label"]
        if label.startswith("amount 150000 or more"):
            rows = [r for r in measured[top] if r[0]["amount"] != "" and int(r[0]["amount"]) >= 150000]
        elif label.startswith("amount under"):
            rows = [r for r in measured[top] if r[0]["amount"] != "" and int(r[0]["amount"]) < 150000]
        else:
            seg = label.replace("segment ", "")
            rows = [r for r in measured[top] if r[0]["segment"] == seg]
        n, b, x = summarize(rows, SLA[top])
        want = (int(e["measured"]), int(e["breaches"]), int(e["total_excess_days"]))
        if (n, b, x) != want:
            problems.append((label, "got", (n, b, x), "want", want))

by_excess = sorted(SLA, key=lambda h: -excess_by_handoff[h])
rates = {h: summarize(measured[h], SLA[h])[1] / len(measured[h]) for h in SLA}
by_rate = sorted(SLA, key=lambda h: -rates[h])
print("Metrics")
print("  Largest total excess days:", by_excess[0], "| highest breach rate:", by_rate[0])
print("  Metric mismatches:", problems or "none")
