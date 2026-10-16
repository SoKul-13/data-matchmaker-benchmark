"""Render paper/v2/DETAILED_ANALYSIS.md as a self-contained HTML report (figures embedded as data URIs).
Run from FINAL_v2:  uv run python paper/scripts/md_to_html_report.py
"""
from __future__ import annotations
import base64, html, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "paper" / "v2" / "DETAILED_ANALYSIS.md"; DST = ROOT / "paper" / "v2" / "DETAILED_ANALYSIS.html"; FIGDIR = ROOT / "paper" / "v2"


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    return t


def img_uri(rel):
    p = FIGDIR / rel
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode() if p.exists() else ""


lines = SRC.read_text().splitlines()
out, toc = [], []
i = 0; sec = 0
while i < len(lines):
    ln = lines[i]
    if ln.startswith("# "):
        out.append(f"<header class='masthead'><p class='eyebrow'>FINAL_v2 · v2_gridsearch/output</p><h1>{inline(ln[2:])}</h1>"); i += 1
        # the generated line follows
        while i < len(lines) and not lines[i].strip(): i += 1
        if i < len(lines) and not lines[i].startswith("#"):
            out.append(f"<p class='lede'>{inline(lines[i])}</p>"); i += 1
        out.append("</header>"); continue
    if ln.startswith("## "):
        title = ln[3:].strip(); sid = "s" + re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        if title == "Contents":
            # skip the markdown contents block; we build our own nav
            i += 1
            while i < len(lines) and not lines[i].startswith("## "): i += 1
            continue
        if sec: out.append("</section>")
        sec += 1; toc.append((sid, title)); out.append(f"<section id='{sid}'><h2>{inline(title)}</h2>"); i += 1; continue
    if ln.startswith("|"):
        rows = []
        while i < len(lines) and lines[i].startswith("|"):
            rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
        rows = [r for r in rows if not all(set(c) <= set("-: ") for c in r)]
        head, body = rows[0], rows[1:]
        num = lambda c: bool(re.fullmatch(r"[+\-–]?\d[\d,\.]*(e[+-]?\d+)?( %)?|\[.*\]|–|yes|no", c))
        th = "".join(f"<th>{inline(c)}</th>" for c in head)
        tb = "".join("<tr>" + "".join(f"<td class='{'n' if num(c) else 't'}'>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
        out.append(f"<div class='tbl'><table><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>"); continue
    m = re.match(r"!\[(.*?)\]\((.*?)\)", ln.strip())
    if m:
        cap, rel = m.group(1), m.group(2); uri = img_uri(rel)
        out.append(f"<figure><img src='{uri}' alt='{html.escape(cap)}' loading='lazy'><figcaption>{inline(cap)}</figcaption></figure>"); i += 1
        # skip the italic caption line that follows
        while i < len(lines) and not lines[i].strip(): i += 1
        if i < len(lines) and lines[i].startswith("*") and lines[i].rstrip().endswith("*") and not lines[i].startswith("* "): i += 1
        continue
    if ln.startswith("* "):
        items = []
        while i < len(lines) and lines[i].startswith("* "): items.append(lines[i][2:]); i += 1
        out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>"); continue
    if re.match(r"\d+\. ", ln):
        items = []
        while i < len(lines) and re.match(r"\d+\. ", lines[i]): items.append(re.sub(r"^\d+\. ", "", lines[i])); i += 1
        out.append("<ol>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ol>"); continue
    if ln.strip():
        out.append(f"<p>{inline(ln)}</p>")
    i += 1
if sec: out.append("</section>")

nav = "".join(f"<a href='#{sid}'>{html.escape(t)}</a>" for sid, t in toc)
page = f"""<title>v2 Detailed Analysis</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,500;6..72,600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* layout: a narrow reading column with a sticky section nav on wide screens; tables and figures may run wider than the text */
:root {{ --bg:#f6f7f7; --surface:#ffffff; --fg:#1c2226; --muted:#5b6670; --line:#d8dde1; --accent:#0e6a78; --accent-soft:#e3f0f2; --code:#eef1f2;
  --display:"Newsreader", Georgia, "Times New Roman", serif; --body:"IBM Plex Sans", "Helvetica Neue", Arial, sans-serif; --mono:"IBM Plex Mono", Menlo, Consolas, monospace; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#121618; --surface:#191f23; --fg:#e4e8ea; --muted:#9aa5ad; --line:#2b3338; --accent:#63c4d1; --accent-soft:#17353a; --code:#1f272c; color-scheme:dark }} }}
:root[data-theme="dark"] {{ --bg:#121618; --surface:#191f23; --fg:#e4e8ea; --muted:#9aa5ad; --line:#2b3338; --accent:#63c4d1; --accent-soft:#17353a; --code:#1f272c; color-scheme:dark }}
body {{ background:var(--bg); color:var(--fg); font-family:var(--body); font-size:15px; line-height:1.55; padding-left:max(16px, env(safe-area-inset-left, 0px)); padding-right:max(16px, env(safe-area-inset-right, 0px)); padding-block:0 64px; }}
.wrap {{ max-width:1180px; margin:0 auto; display:grid; grid-template-columns:220px minmax(0,1fr); gap:40px; }}
nav {{ position:sticky; top:env(safe-area-inset-top, 0px); align-self:start; padding-top:28px; display:flex; flex-direction:column; gap:2px; font-size:13px; max-height:100vh; overflow-y:auto; }}
nav a {{ color:var(--muted); text-decoration:none; padding:5px 10px; border-left:2px solid var(--line); }}
nav a:hover, nav a:focus-visible {{ color:var(--accent); border-color:var(--accent); outline:none; }}
main {{ min-width:0; }}
.masthead {{ padding:36px 0 18px; border-bottom:1px solid var(--line); margin-bottom:8px; }}
.eyebrow {{ font-family:var(--mono); font-size:11px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); margin:0 0 10px; }}
h1 {{ font-family:var(--display); font-weight:500; font-size:clamp(28px, 4vw, 40px); line-height:1.1; margin:0 0 12px; text-wrap:balance; }}
.lede {{ color:var(--muted); max-width:70ch; margin:0; }}
h2 {{ font-family:var(--display); font-weight:600; font-size:24px; margin:40px 0 10px; padding-top:8px; text-wrap:balance; }}
section > p, section > ul, section > ol {{ max-width:72ch; }}
p {{ margin:8px 0; }} ul, ol {{ padding-left:22px; margin:8px 0; }} li {{ margin:4px 0; }}
code {{ font-family:var(--mono); font-size:.88em; background:var(--code); padding:1px 5px; border-radius:3px; }}
strong {{ font-weight:600; }}
.tbl {{ overflow-x:auto; margin:12px 0 18px; border:1px solid var(--line); border-radius:4px; background:var(--surface); }}
table {{ border-collapse:collapse; font-size:12.5px; font-variant-numeric:tabular-nums; min-width:100%; }}
th, td {{ padding:5px 9px; border-bottom:1px solid var(--line); vertical-align:top; white-space:nowrap; }}
th {{ text-align:left; font-weight:600; background:var(--accent-soft); color:var(--fg); position:sticky; top:0; }}
td.n {{ text-align:right; font-family:var(--mono); font-size:12px; }}
tbody tr:hover td {{ background:var(--code); }}
figure {{ margin:18px 0 22px; }}
figure img {{ max-width:100%; height:auto; display:block; background:#fff; border:1px solid var(--line); border-radius:4px; }}
figcaption {{ font-family:var(--mono); font-size:12px; color:var(--muted); margin-top:6px; }}
@media (max-width: 860px) {{ .wrap {{ grid-template-columns:1fr; gap:0; }} nav {{ position:static; max-height:none; flex-direction:row; flex-wrap:wrap; gap:6px; padding:16px 0 0; }} nav a {{ border:1px solid var(--line); border-radius:999px; padding:4px 10px; }} }}
@media (prefers-reduced-motion: no-preference) {{ html {{ scroll-behavior:smooth; }} }}
</style>
<div class="wrap"><nav aria-label="Sections">{nav}</nav><main>{''.join(out)}</main></div>
"""
DST.write_text(page)
print(f"wrote {DST} ({DST.stat().st_size/1e6:.1f} MB), {len(toc)} sections")
