import csv, itertools, random
from datetime import date, timedelta

random.seed(21)
AS_OF = date(2026, 11, 7)

SLA = {"order_review": 1, "legal": 3, "credit_check": 2, "booking": 1, "invoicing": 2, "kickoff": 5}
COL = {"order_review": "order_review_date", "legal": "legal_date", "credit_check": "credit_check_date",
       "booking": "booked_date", "invoicing": "invoice_date", "kickoff": "kickoff_date"}

prefixes = ["Northwind", "Bluepeak", "Harbor", "Summit", "Cedar", "Ironwood", "Lumen", "Pioneer", "Redwood",
            "Silverline", "Tidewater", "Vantage", "Westbrook", "Zenith", "Alder", "Beacon", "Crestview",
            "Driftwood", "Evergreen", "Foxglove", "Granite", "Halcyon", "Juniper", "Keystone", "Larkspur", "Meridian"]
suffixes = ["Logistics", "Health", "Foods", "Systems", "Retail", "Energy", "Media", "Labs", "Supply",
            "Partners", "Industries", "Works"]
accounts = [f"{p} {s}" for p, s in itertools.product(prefixes, suffixes)]
random.shuffle(accounts)

def steps_for(nonstd):
    return ["order_review"] + (["legal"] if nonstd else []) + ["credit_check", "booking", "invoicing", "kickoff"]

def sample_dur(step, seg, amount):
    c = random.choices
    if step == "order_review":
        return c([0, 1, 2, 3], [40, 52, 5, 3])[0]
    if step == "legal":
        return random.randint(1, 3) if random.random() < 0.6 else random.randint(4, 9)
    if step == "credit_check":
        if seg != "SMB" and amount >= 150000 and random.random() < 0.85:
            return random.randint(3, 9)
        return c([0, 1, 2, 3, 4], [10, 45, 35, 6, 4])[0]
    if step == "booking":
        return c([0, 1, 2, 3], [50, 42, 5, 3])[0]
    if step == "invoicing":
        return c([0, 1, 2, 3, 4], [20, 35, 30, 10, 5])[0]
    if step == "kickoff":
        return random.randint(2, 5) if random.random() < 0.88 else random.randint(6, 10)

def new_deal(seg=None, amount=None, nonstd=None):
    seg = seg or random.choices(["SMB", "Commercial", "Enterprise"], [50, 35, 15])[0]
    if amount is None:
        amount = random.choice({"SMB": [8000, 12000, 18000, 24000, 35000, 48000, 60000],
                                "Commercial": [40000, 65000, 90000, 120000, 160000, 200000, 250000],
                                "Enterprise": [120000, 180000, 260000, 340000, 500000, 900000]}[seg])
    if nonstd is None:
        nonstd = random.random() < {"SMB": 0.08, "Commercial": 0.25, "Enterprise": 0.45}[seg]
    rework = 1 if random.random() < 0.15 else 0
    return dict(segment=seg, amount=amount, nonstd="Y" if nonstd else "N", rework=rework)

def build(deal, reached=None, closed=None, last_date=None):
    steps = steps_for(deal["nonstd"] == "Y")
    reached = len(steps) if reached is None else reached
    durs = [sample_dur(s, deal["segment"], deal["amount"]) for s in steps[:reached]]
    if closed is None:
        closed = last_date - timedelta(days=sum(durs))
    deal["closed_won_date"] = closed
    for s in COL.values():
        deal[s] = None
    cur = closed
    for s, d in zip(steps[:reached], durs):
        cur = cur + timedelta(days=d)
        deal[COL[s]] = cur
    return deal

deals, key = [], []
def add_key(d, category, action, note):
    key.append((d, category, action, note))

# ---------- Completed deals (closed Jul 1 to Sep 30) ----------
comp = []
for _ in range(280):
    d = new_deal()
    build(d, closed=date(2026, 7, 1) + timedelta(days=random.randint(0, 91)))
    comp.append(d)
deals += comp
used = set()
def pick(pool, cond=lambda d: True):
    for d in pool:
        if id(d) not in used and cond(d):
            used.add(id(d)); return d
    raise RuntimeError("pool exhausted")
random.shuffle(comp)

# ---------- In-flight and recent deals ----------
STEP_ORDER_NAMES = {"order_review": "order review", "legal": "legal review", "credit_check": "credit check",
                    "booking": "booking", "invoicing": "invoicing", "kickoff": "customer kickoff"}
def inflight(reached, wait, seg=None, amount=None, nonstd=None):
    d = new_deal(seg, amount, nonstd)
    steps = steps_for(d["nonstd"] == "Y")
    build(d, reached=reached, last_date=AS_OF - timedelta(days=wait))
    deals.append(d)
    return d, steps[reached]

# planted stuck deals (open breaches)
d, s = inflight(1, 8, "Enterprise", 340000, False)
add_key(d, "OPEN_BREACH", "FLAG", f"Waiting 8 days on {STEP_ORDER_NAMES[s]}, SLA is {SLA[s]}")
d, s = inflight(1, 6, "Commercial", 200000, False)
add_key(d, "OPEN_BREACH", "FLAG", f"Waiting 6 days on {STEP_ORDER_NAMES[s]}, SLA is {SLA[s]}")
d, s = inflight(1, 4, "Commercial", 90000, False)
add_key(d, "OPEN_BREACH", "FLAG", f"Waiting 4 days on {STEP_ORDER_NAMES[s]}, SLA is {SLA[s]}")
d, s = inflight(1, 9, "Enterprise", 260000, True)
add_key(d, "OPEN_BREACH", "FLAG", f"Waiting 9 days on {STEP_ORDER_NAMES[s]}, SLA is {SLA[s]}")
d, s = inflight(4, 12, "SMB", 24000, False)
add_key(d, "OPEN_BREACH", "FLAG", f"Waiting 12 days on {STEP_ORDER_NAMES[s]}, SLA is {SLA[s]}")

# decoys: waiting exactly the SLA, not a breach
d, s = inflight(0, 1, "SMB", 18000, False)
add_key(d, "OPEN_BREACH", "DO_NOT_FLAG", f"Waiting exactly 1 day on {STEP_ORDER_NAMES[s]}, breach needs more than the 1 day SLA")
d, s = inflight(1, 2, "Commercial", 120000, False)
add_key(d, "OPEN_BREACH", "DO_NOT_FLAG", f"Waiting exactly 2 days on {STEP_ORDER_NAMES[s]}, breach needs more than the 2 day SLA")
d, s = inflight(2, 1, "SMB", 35000, False)
add_key(d, "OPEN_BREACH", "DO_NOT_FLAG", f"Waiting exactly 1 day on {STEP_ORDER_NAMES[s]}, breach needs more than the 1 day SLA")

# baseline in-flight within SLA (not flagged, not individually keyed)
for _ in range(8):
    probe = new_deal()
    steps = steps_for(probe["nonstd"] == "Y")
    reached = random.randint(1, len(steps) - 1)
    inflight(reached, random.randint(0, SLA[steps[reached]]), probe["segment"], probe["amount"], probe["nonstd"] == "Y")
# recent, fully processed
for _ in range(4):
    d = new_deal()
    build(d, last_date=AS_OF - timedelta(days=random.randint(1, 8)))
    deals.append(d)

# ---------- Planted issues on completed deals ----------
# High friction deals (rework 2+ and amount 100,000 or more)
for i in range(10):
    d = pick(comp, lambda x: x["amount"] >= 100000)
    d["rework"] = random.randint(2, 4)
    note = "Rework count %d on a $%s deal" % (d["rework"], format(d["amount"], ","))
    if i == 0:
        d["amount"] = 100000; d["rework"] = 2
        note = "Rework count 2 on a deal of exactly $100,000, boundary case that counts"
    add_key(d, "HIGH_FRICTION", "FLAG", note)
d = pick(comp, lambda x: x["amount"] < 150000)
d["amount"] = 99999; d["rework"] = 3
add_key(d, "HIGH_FRICTION", "DO_NOT_FLAG", "Rework count 3 but amount is $99,999, under the $100,000 minimum")

# Sequence issues
for _ in range(3):
    d = pick(comp)
    d["booked_date"] = d["credit_check_date"] - timedelta(days=2)
    add_key(d, "SEQUENCE_ISSUE", "FLAG", "Booked 2 days before credit check was completed")
for _ in range(2):
    d = pick(comp)
    d["invoice_date"] = d["booked_date"] - timedelta(days=1)
    add_key(d, "SEQUENCE_ISSUE", "FLAG", "Invoice dated 1 day before booking")
d = pick(comp)
d["kickoff_date"] = d["invoice_date"] - timedelta(days=3)
add_key(d, "SEQUENCE_ISSUE", "FLAG", "Kickoff dated 3 days before invoice")

# Missing required steps and blank amount (human look)
for _ in range(3):
    d = pick(comp)
    d["credit_check_date"] = None
    add_key(d, "MISSING_STEP", "NEEDS_HUMAN_LOOK", "Credit check date is blank but booking and later steps are dated")
for _ in range(3):
    d = pick(comp, lambda x: x["nonstd"] == "Y")
    d["legal_date"] = None
    add_key(d, "MISSING_STEP", "NEEDS_HUMAN_LOOK", "Nonstandard terms but legal date is blank while later steps are dated")
d = pick(comp)
d["amount"] = None
add_key(d, "AMOUNT_BLANK", "NEEDS_HUMAN_LOOK", "Amount is blank, cannot assign an amount band or friction check")

# ---------- IDs and write ----------
deals.sort(key=lambda d: d["closed_won_date"])
for i, d in enumerate(deals):
    d["deal_id"] = f"DEAL-{5001 + i}"
    d["account"] = accounts[i]

fmt = lambda v: "" if v is None else (v.isoformat() if isinstance(v, date) else v)
fields = ["deal_id", "account", "segment", "amount", "nonstandard_terms", "rework_count", "closed_won_date",
          "order_review_date", "legal_date", "credit_check_date", "booked_date", "invoice_date", "kickoff_date"]
with open("deal_handoffs.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(fields)
    for d in deals:
        w.writerow([d["deal_id"], d["account"], d["segment"], fmt(d["amount"]), d["nonstd"], d["rework"],
                    fmt(d["closed_won_date"])] + [fmt(d[COL[s]]) for s in COL])

with open("answer_key.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["deal_id", "category", "expected_action", "note"])
    for d, cat, act, note in sorted(key, key=lambda k: (k[0]["deal_id"], k[1])):
        w.writerow([d["deal_id"], cat, act, note])

# ---------- Expected metrics (written by the generator's own logic) ----------
def handoff_rows():
    out = {h: [] for h in SLA}
    for d in deals:
        steps = steps_for(d["nonstd"] == "Y")
        prev_date = d["closed_won_date"]
        for s in steps:
            cur = d[COL[s]]
            if prev_date is not None and cur is not None:
                dur = (cur - prev_date).days
                if dur >= 0:
                    out[s].append((d, dur))
            prev_date = cur
    return out

hr = handoff_rows()
metrics = []
for h in SLA:
    rows = hr[h]
    breaches = [x for x in rows if x[1] > SLA[h]]
    excess = sum(x[1] - SLA[h] for x in breaches)
    metrics.append(dict(handoff=h, sla=SLA[h], measured=len(rows), breaches=len(breaches),
                        rate=round(100 * len(breaches) / len(rows), 1), excess=excess))
for rank, m in enumerate(sorted(metrics, key=lambda m: -m["excess"]), 1):
    m["excess_rank"] = rank
for rank, m in enumerate(sorted(metrics, key=lambda m: -m["rate"]), 1):
    m["rate_rank"] = rank

top = max(metrics, key=lambda m: m["excess"])["handoff"]
with open("expected_metrics.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["section", "label", "sla_days", "measured", "breaches", "breach_rate_pct", "total_excess_days", "excess_rank", "breach_rate_rank"])
    for m in metrics:
        w.writerow(["handoff", m["handoff"], m["sla"], m["measured"], m["breaches"], m["rate"], m["excess"], m["excess_rank"], m["rate_rank"]])
    def conc(label, cond):
        rows = [x for x in hr[top] if cond(x[0])]
        b = [x for x in rows if x[1] > SLA[top]]
        w.writerow([f"concentration:{top}", label, SLA[top], len(rows), len(b),
                    round(100 * len(b) / len(rows), 1) if rows else "", sum(x[1] - SLA[top] for x in b), "", ""])
    conc("amount 150000 or more", lambda d: d["amount"] is not None and d["amount"] >= 150000)
    conc("amount under 150000", lambda d: d["amount"] is not None and d["amount"] < 150000)
    for seg in ("SMB", "Commercial", "Enterprise"):
        conc("segment " + seg, lambda d, seg=seg: d["segment"] == seg)

print(len(deals), "deals")
print([(m["handoff"], m["measured"], m["breaches"], m["rate"], m["excess"], m["excess_rank"], m["rate_rank"]) for m in metrics])
print("top by excess:", top)
from collections import Counter
print(Counter((k[1], k[2]) for k in key))
