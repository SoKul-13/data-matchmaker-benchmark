#!/usr/bin/env python3
"""Score candidates.csv with the rubric in 00_SCORING_RUBRIC.md, keep the top 100, build coverage-constrained
top-k lists (5,10,20,25,30,40,50) and per-version fits. Writes 05_RANKED_100.md, 06_GROUPINGS.md, 07_PER_VERSION_FIT.md, ranked_100.csv."""
import csv
from collections import Counter, defaultdict

W = {"R": .25, "A": .15, "G": .15, "D": .15, "C": .10, "I": .10, "L": .10}
FAM_LABEL = {"EM": "entity matching", "DI": "schema / data integration", "TQA": "table QA & understanding",
             "FIN": "financial document QA", "ANC": "answer-type anchor", "META": "human-label meta-evaluation"}
# coverage families used for the constrained lists (finer than the 6 families)
def cov_family(r):
    f, at, name, dom = r["family"], r["answer_type"], r["name"], r["domain"].lower()
    if f == "EM":
        if "mixed" in dom or ("products" in dom and "bibliographic" in dom): return "EM-other"
        if "people" in dom or "person" in dom or "organisation" in dom: return "EM-people/org"
        if "bibliographic" in dom or "citation" in dom: return "EM-bibliographic"
        if "product" in dom or "spec" in dom or "electronics" in dom or "software" in dom: return "EM-products"
        return "EM-other"
    if f == "DI":
        if "schema" in dom or "column" in at or "attribute" in dom or "harmonisation" in dom or "join" in dom or "xbrl" in dom or "concept" in dom: return "DI-schema/join"
        if "annotation" in dom or "label" == at: return "DI-annotation"
        if "union" in dom or "lake" in dom: return "DI-discovery"
        if "error" in dom or "clean" in dom or "hospital" in dom: return "DI-cleaning"
        return "DI-other"
    if f == "TQA":
        if "boolean" in at or "3-way" in at: return "TQA-verification"
        if "free-form" in at or "sentence" in at: return "TQA-freeform"
        if "SQL" in at: return "TQA-sql"
        if "hierarch" in dom or "statistical" in dom or "spreadsheet" in dom or "multi-table" in dom or "multi-sheet" in dom: return "TQA-hierarchical/multi"
        if "financ" in dom or "10-k" in dom or "sec" in dom: return "TQA-financial"
        return "TQA-general"
    if f == "FIN": return "FIN-document"
    if f == "ANC":
        if "number" in at or "float" in at: return "ANC-numeric"
        if "boolean" in at or "3-way" in at: return "ANC-boolean"
        if "multilingual" in dom or "languages" in dom: return "ANC-multilingual"
        if "list" in at or "table" == at: return "ANC-list/table"
        return "ANC-span/freeform"
    return "META"

rows = list(csv.DictReader(open("candidates.csv")))
for r in rows:
    r["importance"] = round(100 * sum(W[k] * int(r[k]) / 5 for k in W), 1)
    r["cov"] = cov_family(r)
    r["multilingual"] = int(r["I"]) >= 4
rows.sort(key=lambda r: (-r["importance"], -int(r["R"]), -int(r["D"]), r["name"]))
dropped = rows[100:]; rows = rows[:100]
for i, r in enumerate(rows, 1): r["rank"] = i

with open("ranked_100.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["rank", "name", "family", "cov", "domain", "answer_type", "year", "licence", "download", "R", "A", "G", "D", "C", "I", "L", "importance", "note"])
    w.writeheader(); [w.writerow({k: r[k] for k in w.fieldnames}) for r in rows]

# ---------- 05 ranked list
L = ["# The 100 datasets, ranked 1–100 by importance for an LLM data-matching benchmark\n",
     "Importance = 100 × Σ weight × sub-score/5 with weights R .25 (relevance), A .15 (adoption), G .15 (generalisation), D .15 (discriminative today), "
     "C .10 (gold/metric clarity), I .10 (inclusivity), L .10 (licence/access). Sub-scores 0–5 are in `ranked_100.csv`; rubric in `00_SCORING_RUBRIC.md`. "
     f"111 candidates were scored; the 11 lowest were dropped ({', '.join(d['name'] for d in dropped)}).\n",
     "| # | Dataset | Family | Coverage family | Domain | Answer type | Licence | Imp. | R | A | G | D | C | I | L | Why here |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    L.append(f"| {r['rank']} | {r['name']} | {FAM_LABEL[r['family']]} | {r['cov']} | {r['domain']} | {r['answer_type']} | {r['licence']} | **{r['importance']}** | {r['R']} | {r['A']} | {r['G']} | {r['D']} | {r['C']} | {r['I']} | {r['L']} | {r['note']} |")
fam_counts = Counter(r["family"] for r in rows)
L += ["", "Family counts in the 100: " + ", ".join(f"{FAM_LABEL[k]} {v}" for k, v in fam_counts.items()) + ".",
      "", "Reading the scores: R dominates by design (a dataset that is not about matching or reading structured data cannot rank high however famous); "
      "A rewards canon status; G rewards a new domain/modality/answer type; D penalises saturated sets (WikiSQL, Spider 1.0, TabMWP, DBLP-ACM) and floor sets; "
      "I lifts multilingual or non-Western sources (TableEval, MiMoTable, OpenSanctions, MGSM, TyDi); L penalises gated, NC or unlocated data (OfficeQA, FinanceBench, RealHiTBench data, MMQA)."]
open("05_RANKED_100.md", "w").write("\n".join(L) + "\n")

# ---------- 06 coverage-constrained groups
CORE = ["EM-products", "EM-bibliographic", "EM-people/org", "DI-schema/join", "DI-annotation", "TQA-general", "TQA-hierarchical/multi", "TQA-financial", "TQA-verification", "TQA-freeform", "FIN-document", "ANC-numeric", "ANC-boolean", "ANC-multilingual", "TQA-sql", "DI-cleaning", "DI-discovery", "META", "ANC-list/table", "ANC-span/freeform", "EM-other", "DI-other"]
# minimum coverage quotas per k: (family -> min count)
QUOTA = {
    5:  {"DI-schema/join": 2, "EM-products": 1, "TQA-hierarchical/multi": 1, "TQA-general": 1},
    10: {"DI-schema/join": 2, "EM-products": 3, "EM-bibliographic": 1, "TQA-hierarchical/multi": 1, "TQA-general": 1, "FIN-document": 1, "TQA-financial": 1},
    20: {"EM-products": 3, "EM-bibliographic": 1, "EM-people/org": 1, "DI-schema/join": 2, "DI-annotation": 1, "TQA-hierarchical/multi": 2, "TQA-general": 2, "TQA-financial": 1, "TQA-verification": 1, "TQA-freeform": 1, "FIN-document": 2, "ANC-numeric": 1, "ANC-multilingual": 1},
    25: {"EM-products": 3, "EM-bibliographic": 1, "EM-people/org": 1, "EM-other": 1, "DI-schema/join": 2, "DI-annotation": 1, "TQA-hierarchical/multi": 2, "TQA-general": 2, "TQA-financial": 2, "TQA-verification": 1, "TQA-freeform": 1, "FIN-document": 2, "ANC-numeric": 1, "ANC-boolean": 1, "ANC-multilingual": 1, "TQA-sql": 1},
    30: {"EM-products": 4, "EM-bibliographic": 1, "EM-people/org": 1, "EM-other": 1, "DI-schema/join": 3, "DI-annotation": 1, "DI-cleaning": 1, "TQA-hierarchical/multi": 3, "TQA-general": 2, "TQA-financial": 2, "TQA-verification": 1, "TQA-freeform": 1, "FIN-document": 2, "ANC-numeric": 1, "ANC-boolean": 1, "ANC-multilingual": 1, "TQA-sql": 1, "META": 1},
    40: {"EM-products": 5, "EM-bibliographic": 2, "EM-people/org": 1, "EM-other": 2, "DI-schema/join": 3, "DI-annotation": 2, "DI-cleaning": 1, "DI-discovery": 1, "TQA-hierarchical/multi": 3, "TQA-general": 3, "TQA-financial": 3, "TQA-verification": 2, "TQA-freeform": 1, "FIN-document": 3, "ANC-numeric": 2, "ANC-boolean": 1, "ANC-multilingual": 2, "ANC-list/table": 1, "TQA-sql": 1, "META": 2},
    50: {"EM-products": 6, "EM-bibliographic": 2, "EM-people/org": 2, "EM-other": 3, "DI-schema/join": 4, "DI-annotation": 2, "DI-cleaning": 1, "DI-discovery": 1, "TQA-hierarchical/multi": 4, "TQA-general": 3, "TQA-financial": 3, "TQA-verification": 2, "TQA-freeform": 2, "FIN-document": 4, "ANC-numeric": 2, "ANC-boolean": 1, "ANC-multilingual": 3, "ANC-list/table": 1, "ANC-span/freeform": 1, "TQA-sql": 2, "META": 2},
}
def select(k):
    quota = dict(QUOTA[k]); chosen = []; have = Counter()
    # pass 0: the top ceil(k/2) by importance are always in (so no highly ranked dataset is crowded out by quotas)
    for r in rows[: (k + 1) // 2]:
        chosen.append(r); have[r["cov"]] += 1
    # pass 1: fill quotas by importance within each family
    for fam, need in quota.items():
        for r in rows:
            if have[fam] >= need: break
            if r["cov"] == fam and r not in chosen:
                chosen.append(r); have[fam] += 1
    # pass 2: fill the rest by global importance
    for r in rows:
        if len(chosen) >= k: break
        if r not in chosen: chosen.append(r)
    chosen = chosen[:k]
    return sorted(chosen, key=lambda r: r["rank"])

G = ["# Coverage-constrained groupings: the 5, 10, 20, 25, 30, 40 and 50 most important datasets\n",
     "Each list is built in three passes: (0) the top ⌈k/2⌉ datasets by importance are always included; (1) fill a coverage quota per family (entity matching by domain, schema/join, annotation, table QA by kind, financial documents, anchors by answer type, multilingual, meta-evaluation) with the highest-ranked members of that family; (2) fill the remaining slots by global importance. Pass 0 guarantees that no dataset ranked in the top half of a list's size can be crowded out by quotas (without it, quota sums close to k made the 40- and 50-lists almost entirely quota-driven). "
     "So a lower-ranked dataset can enter a list ahead of a higher-ranked one when it is the only representative of a family the list must cover (inclusivity / representation); this is stated per list as 'quota entries'. The quotas grow with k so that small lists stay focused on the benchmark's core (matching, schema, tables, financial documents) and larger lists add anchors, multilingual sets and human-label meta-evaluation.\n"]
prev = []
for k in [5, 10, 20, 25, 30, 40, 50]:
    sel = select(k)
    quota_entries = [r for r in sel if r["rank"] > k]
    G += [f"## Top {k}\n", "| # | Dataset | Coverage family | Imp. | Role in the group |", "|---|---|---|---|---|"]
    for r in sel:
        role = "quota entry (covers " + r["cov"] + ")" if r in quota_entries else "by importance"
        if r["multilingual"]: role += "; inclusivity"
        G.append(f"| {r['rank']} | {r['name']} | {r['cov']} | {r['importance']} | {role} |")
    fams = Counter(r["cov"] for r in sel)
    G += ["", f"Coverage: " + ", ".join(f"{f} {n}" for f, n in sorted(fams.items())) + ".",
          f"Multilingual / non-English members: {sum(r['multilingual'] for r in sel)}. Gated or NC licences to note: " + (", ".join(r['name'] for r in sel if any(t in r['licence'].lower() for t in ['gated', 'nc', 'unknown', 'not located'])) or "none") + ".",
          f"Added relative to the previous list: " + (", ".join(r['name'] for r in sel if r not in prev) if prev else "—") + ".", ""]
    prev = sel
open("06_GROUPINGS.md", "w").write("\n".join(G) + "\n")

# ---------- 07 per-version fit
VERS = {
 "v1 (original judge: TPC-DI rubric + hand-set composite)": dict(want=lambda r: r["family"] in ("TQA", "FIN") and r["cov"] not in ("TQA-sql",) or r["name"].startswith("TPC-DI"),
    why="v1 grades short QA answers with a fixed composite and scores the TPC-DI join task; it can only consume short-answer table/document QA and its own task. Entity matching and schema sets have no path into v1."),
 "v2 (grid over v1's four weights)": dict(want=lambda r: r["family"] in ("TQA", "FIN") and r["cov"] not in ("TQA-sql",) or r["name"].startswith("TPC-DI"),
    why="same scorer as v1; needs short golds where F1 / precision / recall / numeric decay are meaningful; boolean sets are fine but uninformative for the four weights; free-form sets stress the weights most."),
 "v3 (native metric per dataset + literature aggregation views)": dict(want=lambda r: r["family"] != "META" and int(r["C"]) >= 3,
    why="v3 uses each dataset's official metric, so any dataset with a clear metric fits, including entity matching (accuracy/F1), schema matching (F1, MRR) and SQL (execution accuracy); it rewards many items per dataset (Bradley–Terry and IRT need pairs) and penalises sets without an official metric."),
 "v4 (9-metric composite, random search, rank agreement)": dict(want=lambda r: r["family"] in ("EM", "TQA", "FIN") and r["cov"] not in ("TQA-sql",),
    why="v4 scores answer text with the 9-component composite, so it needs QA-style golds (numbers, spans, lists, sentences, yes/no); entity-matching sets work as yes/no items; schema and SQL sets do not fit without a wrapper. Its objective needs several datasets that genuinely rank models differently."),
 "v5 (100-metric library + anchors + weight ensemble)": dict(want=lambda r: r["family"] in ("EM", "TQA", "FIN", "ANC", "META") and r["cov"] not in ("TQA-sql",),
    why="v5 needs alias-derivable golds of diverse answer types (its anchors are generated per gold) and benefits from every answer-type anchor and multilingual set; meta-evaluation sets (SummEval, TRUE, JudgeBench) are the human-label validation the paper still lacks."),
}
P = ["# Per-version fit: which datasets each version can use, and the recommended groups of 5/10/20/25/30/40/50 per version\n",
     "Rule: a dataset 'fits' a version if the version's scorer can consume its gold format without new code (stated per version). Within the fitting set, groups are built with the same three-pass procedure (top half by importance, then coverage quotas, then importance) as `06_GROUPINGS.md`, restricted to fitting datasets. If a quota family has no fitting member it is skipped.\n"]
for vname, spec in VERS.items():
    fit = [r for r in rows if spec["want"](r)]
    P += [f"## {vname}\n", spec["why"], "", f"Fitting datasets: {len(fit)} of 100. Not fitting (top examples): " + ", ".join(r['name'] for r in rows if r not in fit)[:600] + ".", ""]
    def sel_v(k):
        quota = dict(QUOTA[k]); chosen = []; have = Counter()
        for r in fit[: (k + 1) // 2]:
            chosen.append(r); have[r["cov"]] += 1
        for fam, need in quota.items():
            for r in fit:
                if have[fam] >= need: break
                if r["cov"] == fam and r not in chosen: chosen.append(r); have[fam] += 1
        for r in fit:
            if len(chosen) >= k: break
            if r not in chosen: chosen.append(r)
        return sorted(chosen[:k], key=lambda r: r["rank"])
    for k in [5, 10, 20, 25, 30, 40, 50]:
        s = sel_v(k)
        if len(s) < k:
            P.append(f"**Top {k}:** only {len(s)} fitting datasets exist; list = all of them.")
        P.append(f"**Top {k}:** " + "; ".join(f"{r['rank']}. {r['name']}" for r in s) + "\n")
    P.append("")
open("07_PER_VERSION_FIT.md", "w").write("\n".join(P) + "\n")
print("top 20:"); [print(r["rank"], r["importance"], r["name"], "|", r["cov"]) for r in rows[:20]]
print("dropped:", [d["name"] for d in dropped])
