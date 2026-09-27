#!/usr/bin/env python3
"""
Evidence-based re-ranking. Inputs:
  candidates.csv          (from the survey; judgement sub-scores kept for R, G, D, C, I, L)
  paper_usage.csv         (dataset,papers_total,papers_2023plus,paper_list)  built from the paper corpus
Adoption A is REPLACED by evidence:  A_ev = 5 * min(1, log1p(papers_total) / log1p(A_MAX))  with a recency bonus
  A = 0.7*A_ev + 0.3 * 5*min(1, papers_2023plus / R_MAX)       (A_MAX, R_MAX = 90th percentile counts in the corpus)
Datasets absent from the corpus get A = 0 unless introduced in 2025-26 (then A = 1: "too new to be cited").
Everything else (weights, coverage quotas, per-version rules) is identical to rank.py; outputs are written with the suffix _evidence.
"""
import csv, math, re
from collections import Counter
import importlib.util, sys
spec = importlib.util.spec_from_file_location("rank", "rank.py"); rank = importlib.util.module_from_spec(spec)
# rank.py runs on import; we only need its helper definitions, so exec a trimmed copy
src = open("rank.py").read().split("rows = list(csv.DictReader")[0]
ns = {}; exec(src, ns)
W, FAM_LABEL, cov_family = ns["W"], ns["FAM_LABEL"], ns["cov_family"]

def norm(s): return re.sub(r"[^a-z0-9]", "", s.lower())
ALIAS = {  # canonical corpus name -> substrings of candidate names
 "abtbuy": ["abt-buy"], "amazongoogle": ["amazon-google"], "dblpacm": ["dblp-acm"], "dblpscholar": ["dblp-scholar"], "walmartamazon": ["walmart-amazon"],
 "fodorszagats": ["fodors"], "itunesamazon": ["itunes"], "beer": ["beer ("], "company": ["company"], "wdclspc": ["wdc lspc"], "wdcproducts2024": ["wdc products 2024"],
 "machamp": ["machamp"], "alaska": ["alaska camera", "alaska monitor"], "alaskasm": ["alaska schema"], "musicbrainz": ["musicbrainz"], "ncvr": ["north carolina"], "febrl": ["febrl"], "cora": ["cora"],
 "valentine": ["valentine"], "magnetogdc": ["magneto"], "smat": ["smat"], "sotab": ["sotab"], "t2dv2": ["t2dv2"], "turlcta": ["turl"], "viznet": ["viznet"], "gittables": ["gittables"],
 "tus": ["tus small"], "santos": ["santos"], "lakebench": ["lakebench"], "rahacollection": ["raha"], "holocleancollection": ["holoclean"], "opensanctions": ["opensanctions"], "papadakisdn": ["papadakis"],
 "autojoin": ["auto-join"], "semtab": ["semtab"], "oaei": ["oaei 2025"], "jellyfish": ["jellyfish"], "emberdataset": ["ember"], "imdbtmdb": ["imdb-tmdb"], "crossdatasetem": ["cross-dataset"], "tpcdi": ["tpc-di"],
 "wtq": ["wikitablequestions"], "wikisql": ["wikisql"], "sqa": ["sqa"], "tabfact": ["tabfact"], "feverous": ["feverous"], "infotabs": ["infotabs"], "hybridqa": ["hybridqa"], "ottqa": ["ott-qa"], "fetaqa": ["fetaqa"],
 "totto": ["totto"], "hitab": ["hitab"], "aitqa": ["ait-qa"], "tatqa": ["tat-qa"], "tatdqa": ["tat-dqa"], "finqa": ["finqa"], "convfinqa": ["convfinqa"], "multihiertt": ["multihiertt"], "docfinqa": ["docfinqa"],
 "tabmwp": ["tabmwp"], "tablebench": ["tablebench"], "databench": ["databench"], "tableeval": ["tableeval"], "realhitbench": ["realhitbench"], "mimotable": ["mimotable"], "spider": ["spider 1.0"], "spider20": ["spider 2.0"],
 "bird": ["bird"], "scitab": ["scitab"], "robut": ["robut"], "crtqa": ["crt-qa"], "mmtu": ["mmtu"], "suc": ["suc ("], "tabis": ["tabis"], "temptabqa": ["temptabqa"], "pubhealthtab": ["pubhealthtab"], "mmqa": ["mmqa"],
 "financebench": ["financebench"], "officeqa": ["officeqa pro/full"], "officeqaprov2": ["officeqa pro v2"], "bizbench": ["bizbench"], "docmatheval": ["docmath"], "secque": ["secque"], "finder": ["finder"],
 "financeagentbenchmark": ["finance agent"], "edgarcorpus": ["edgar"], "financemath": ["financemath"], "fintagging": ["fintagging"], "finauditing": ["finauditing"], "mpdocvqa": ["mp-docvqa"], "chartqa": ["chartqa"],
 "gsm8k": ["gsm8k"], "drop": ["drop"], "boolq": ["boolq"], "squad": ["squad"], "triviaqa": ["triviaqa"], "qampari": ["qampari"], "narrativeqa": ["narrativeqa"], "vitaminc": ["vitaminc"], "mgsm": ["mgsm"],
 "tydiqa": ["tydi"], "opensanctions": ["opensanctions"], "ncvr": ["north carolina"], "officeqaprov2": ["officeqa pro v2"], "officeqa": ["officeqa pro/full"], "wdcproducts2024": ["wdc products 2024"], "wdclspc": ["wdc lspc"], "raha": ["raha"], "holoclean": ["holoclean"], "smat": ["smat"], "alaskasm": ["alaska schema"], "alaska": ["alaska camera", "alaska monitor"], "spider20": ["spider 2.0"], "spider": ["spider 1.0"], "true": ["true"], "wmtmqm": ["wmt mqm"], "crossdatasetem": ["cross-dataset"], "emberdataset": ["ember"], "mlqa": ["mlqa"], "summeval": ["summeval"], "true": ["true"], "wmtmqm": ["wmt mqm"], "judgebench": ["judgebench"], "llmbar": ["llmbar"], "multitabqa": ["multitabqa"], "lmdw": ["lm-dw"], "dabench": ["da-code"],
}
usage = {}
for r in csv.DictReader(open("paper_usage.csv")):
    usage[norm(r["dataset"])] = (int(r["papers_total"]), int(r["papers_2023plus"]), r.get("paper_list", ""), int(r.get("papers_core", r["papers_total"])))

rows = list(csv.DictReader(open("candidates.csv")))
counts = [v[0] for v in usage.values()] or [1]; rec = [v[1] for v in usage.values()] or [1]
import statistics
A_MAX = max(3, sorted(counts)[int(0.9 * (len(counts) - 1))]); R_MAX = max(2, sorted(rec)[int(0.9 * (len(rec) - 1))])
def lookup(name):
    n = name.lower()
    for key, subs in ALIAS.items():
        if any(s in n for s in subs) and key in usage:
            return key, usage[key]
    return None, None
for r in rows:
    key, u = lookup(r["name"])
    r["A_judgement"] = r["A"]
    yr = re.findall(r"20\d\d", r["year"]); newest = max(int(y) for y in yr) if yr else 0
    r["papers_core"] = 0
    if r["family"] == "ANC":  # general-purpose anchors: the corpus (matching / tables / finance / LLM-evaluation) is not where they are cited, so evidence would be a false zero
        r["papers_total"], r["papers_2023plus"] = (u[0], u[1]) if u else (0, 0); r["paper_list"] = "anchor: A kept from judgement (corpus out of scope)"
    elif u and u[0] > 0:
        tot, rc, plist, r["papers_core"] = u
        a_ev = 5 * min(1.0, math.log1p(tot) / math.log1p(A_MAX)); a_rc = 5 * min(1.0, rc / R_MAX)
        r["A"] = str(round(0.7 * a_ev + 0.3 * a_rc, 2)); r["papers_total"], r["papers_2023plus"], r["paper_list"] = tot, rc, plist
    else:
        r["A"] = "1" if newest >= 2025 else "0"; r["papers_total"], r["papers_2023plus"], r["paper_list"] = 0, 0, "not in corpus"
    r["importance"] = round(100 * sum(W[k] * float(r[k]) / 5 for k in W), 1); r["cov"] = cov_family(r); r["multilingual"] = int(r["I"]) >= 4
rows.sort(key=lambda r: (-r["importance"], -int(r["R"]), -int(r["D"]), r["name"]))
dropped = rows[100:]; rows = rows[:100]
for i, r in enumerate(rows, 1): r["rank"] = i
with open("ranked_100_evidence.csv", "w", newline="") as f:
    fn = ["rank", "name", "family", "cov", "domain", "answer_type", "year", "licence", "download", "papers_core", "papers_total", "papers_2023plus", "A", "A_judgement", "R", "G", "D", "C", "I", "L", "importance", "paper_list", "note"]
    w = csv.DictWriter(f, fieldnames=fn); w.writeheader(); [w.writerow({k: r[k] for k in fn}) for r in rows]

L = ["# Evidence-based ranking: the 100 datasets ranked by usage in the top-cited literature\n",
     f"Adoption (A) is now computed from the paper corpus (`paper_usage.csv`, built from `10_PAPER_CORPUS.md`): A = 0.7·5·min(1, ln(1+n)/ln(1+{A_MAX})) + 0.3·5·min(1, n₂₀₂₃₊/{R_MAX}), where n = number of corpus papers (core + supplementary, see `10_PAPER_CORPUS.md`) evaluating on the dataset and n₂₀₂₃₊ those from 2023 on; {A_MAX} and {R_MAX} are the corpus 90th percentiles. Datasets absent from the corpus get A = 0 (or 1 if introduced 2025–26). General-purpose anchor sets (family ANC) keep the judgement A because the corpus was built around matching, tables, finance and LLM evaluation, not general QA; their corpus counts are still shown. Other criteria and weights unchanged from `00_SCORING_RUBRIC.md`. Dropped to reach 100: " + ", ".join(d["name"] for d in dropped) + ".\n",
     "| # | Dataset | Coverage family | Papers core+supp (2023+) | A (was) | Imp. | R | G | D | C | I | L | Licence | Cited by (short names) |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    L.append(f"| {r['rank']} | {r['name']} | {r['cov']} | {r['papers_core']}+{r['papers_total']-r['papers_core']} ({r['papers_2023plus']}) | {r['A']} ({r['A_judgement']}) | **{r['importance']}** | {r['R']} | {r['G']} | {r['D']} | {r['C']} | {r['I']} | {r['L']} | {r['licence']} | {str(r['paper_list'])[:160]} |")
open("05_RANKED_100_evidence.md", "w").write("\n".join(L) + "\n")


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

G = ["# Coverage-constrained groupings (evidence-based adoption): the 5, 10, 20, 25, 30, 40 and 50 most important datasets\n",
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
open("06_GROUPINGS_evidence.md", "w").write("\n".join(G) + "\n")

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
P = ["# Per-version fit (evidence-based adoption): which datasets each version can use, and the recommended groups of 5/10/20/25/30/40/50 per version\n",
     "Rule: a dataset 'fits' a version if the version's scorer can consume its gold format without new code (stated per version). Within the fitting set, groups are built with the same three-pass procedure (top half by importance, then coverage quotas, then importance) as `06_GROUPINGS_evidence.md`, restricted to fitting datasets. If a quota family has no fitting member it is skipped.\n"]
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
open("07_PER_VERSION_FIT_evidence.md", "w").write("\n".join(P) + "\n")
print("top 20:"); [print(r["rank"], r["importance"], r["name"], "|", r["cov"]) for r in rows[:20]]
print("dropped:", [d["name"] for d in dropped])
