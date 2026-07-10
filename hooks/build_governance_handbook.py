#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_governance_handbook.py -- generate spindleloom_website/governance-handbook.html
from knowledge_hub/GOVERNANCE.md.

GOVERNANCE.md is the single source of truth (Part I layout standard, Part II story
craft, Part III team + Azure DevOps). This page is the readable single-file view --
same derive-then-check contract as build_agent_index.py / build_harness_artifacts.py.
Page chrome authored here is pure ASCII; the MD content passes through as-is.

Usage:
    python hooks/build_governance_handbook.py            # regenerate the HTML
    python hooks/build_governance_handbook.py --check     # exit 1 if stale (CI/pre-commit)

Stdlib-only.
"""
import html as H
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HUB = ROOT / "knowledge_hub"
SITE = ROOT / "spindleloom_website"
SOURCE = "GOVERNANCE.md"
OUT = SITE / "governance-handbook.html"

DEKS = {
    "I": "The versioned mandate for adopter repos: the tree, profiles, cadence planes, naming, concurrency and conformance.",
    "II": "How every backlog item is written and judged: cards, INVEST, acceptance criteria, vertical splitting, sizing.",
    "III": "The 10-person mapping, the architect's epic-decomposition sequence, and the Azure DevOps system-of-record fit.",
}

CODE_PH = "\x00CODE%d\x00"


def split_parts():
    """Split GOVERNANCE.md at its '# Part N -- Title' headers -> [(num, title, body)]."""
    t = (HUB / SOURCE).read_text(encoding="utf-8").replace("\r\n", "\n")
    chunks = re.split(r"(?m)^# (Part [IVX]+ [^\n]*)$", t)
    parts = []
    for i in range(1, len(chunks), 2):
        m = re.match(r"Part ([IVX]+)\s*[-–—]+\s*(.*)", chunks[i])
        num, title = m.group(1), m.group(2).strip()
        body = re.sub(r"\n---\s*$", "", chunks[i + 1].strip("\n"))
        parts.append((num, title, body))
    return parts


def inline(s, codes):
    def stash(m):
        codes.append(m.group(1))
        return CODE_PH % (len(codes) - 1)
    s = re.sub(r"`([^`]+)`", stash, s)
    s = H.escape(s, quote=False)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<i>\1</i>", s)
    return s


def restore(s, codes):
    for i, c in enumerate(codes):
        s = s.replace(CODE_PH % i, "<code>%s</code>" % H.escape(c))
    return s


def slug(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:60] or "s"


def md2html(text, part_key, toc):
    codes, out, lines, i = [], [], text.split("\n"), 0
    in_ul = in_ol = in_table = False
    table_rows = []

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul: out.append("</ul>"); in_ul = False
        if in_ol: out.append("</ol>"); in_ol = False

    def flush_table():
        nonlocal in_table, table_rows
        if not in_table: return
        rows = [r for r in table_rows if not re.match(r"^\s*\|[\s\-:|]+\|\s*$", r)]
        out.append('<div class="tw"><table>')
        for ri, r in enumerate(rows):
            cells = [c.strip() for c in r.strip().strip("|").split("|")]
            tag = "th" if ri == 0 else "td"
            out.append("<tr>" + "".join("<%s>%s</%s>" % (tag, inline(c, codes), tag) for c in cells) + "</tr>")
        out.append("</table></div>")
        in_table = False; table_rows = []

    while i < len(lines):
        l = lines[i]
        if l.startswith("```"):
            close_lists(); flush_table()
            block = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                block.append(lines[i]); i += 1
            out.append("<pre>" + H.escape("\n".join(block)) + "</pre>")
            i += 1
            continue
        if l.startswith("|"):
            close_lists(); in_table = True; table_rows.append(l); i += 1
            continue
        flush_table()
        if re.match(r"^#{1,3} ", l):
            close_lists()
            level = len(l) - len(l.lstrip("#"))
            txt = l.lstrip("# ").strip()
            if level != 1:
                sid = part_key + "-" + slug(txt)
                if level == 2:
                    toc.append((sid, txt))
                out.append('<h%d id="%s">%s</h%d>' % (level + 1, sid, inline(txt, codes), level + 1))
            i += 1
            continue
        if l.startswith(">"):
            close_lists()
            q = [l.lstrip("> ").strip()]
            while i + 1 < len(lines) and lines[i + 1].startswith(">"):
                i += 1; q.append(lines[i].lstrip("> ").strip())
            out.append("<blockquote><p>" + inline(" ".join(q), codes) + "</p></blockquote>")
            i += 1
            continue
        m = re.match(r"^(\s*)[-*] (.*)", l)
        if m:
            if in_ol: out.append("</ol>"); in_ol = False
            if not in_ul: out.append("<ul>"); in_ul = True
            out.append("<li>" + inline(m.group(2), codes) + "</li>"); i += 1
            continue
        m = re.match(r"^(\s*)\d+\. (.*)", l)
        if m:
            if in_ul: out.append("</ul>"); in_ul = False
            if not in_ol: out.append("<ol>"); in_ol = True
            out.append("<li>" + inline(m.group(2), codes) + "</li>"); i += 1
            continue
        if re.match(r"^\s*---+\s*$", l):
            close_lists(); out.append("<hr>"); i += 1
            continue
        if l.strip() == "":
            close_lists(); i += 1
            continue
        para = [l.strip()]
        while (i + 1 < len(lines) and lines[i + 1].strip() != ""
               and not re.match(r"^(#{1,3} |\||>|```|\s*[-*] |\s*\d+\. |\s*---+\s*$)", lines[i + 1])):
            i += 1; para.append(lines[i].strip())
        out.append("<p>" + inline(" ".join(para), codes) + "</p>"); i += 1
    close_lists(); flush_table()
    return restore("\n".join(out), codes)


MARK = ('<svg width="20" height="20" viewBox="0 0 20 20" aria-hidden="true" style="flex-shrink:0;vertical-align:-4px">'
        '<path d="M10 10 C7.6 6.9 3.1 6.6 3.1 10 C3.1 13.4 7.6 13.1 10 10" fill="none" stroke="var(--weft)" stroke-width="1.7" stroke-linecap="round"/>'
        '<path d="M10 10 C12.4 6.9 16.9 6.6 16.9 10 C16.9 13.4 12.4 13.1 10 10" fill="none" stroke="var(--gold)" stroke-width="1.7" stroke-linecap="round"/>'
        '<circle cx="10" cy="10" r="2.9" fill="var(--ground)"/><circle cx="10" cy="10" r="1.7" fill="var(--gold)"/>'
        '<circle cx="10" cy="10" r="0.7" fill="var(--ground)"/></svg>')

SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Spindleloom Governance Handbook</title>
<style>
:root{
  --ground:#0E1524; --panel:#141E2E; --panel-2:#18263A;
  --ink:#DBE5F1; --ink-mid:#93A6BC; --ink-dim:#8497AE; --hair:#1E2E45; --hair-2:#2A3E5C;
  --gold:#CFA23A; --gold-hi:#E7BE58; --weft:#5C90BE;
  --shadow:0 1px 0 rgba(255,255,255,.03),0 14px 34px rgba(0,0,0,.34);
  --serif:"Hoefler Text","Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
  --sans:ui-sans-serif,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --mono:ui-monospace,"SF Mono","Cascadia Code","JetBrains Mono",Menlo,Consolas,monospace;
}
@media (prefers-color-scheme:light){:root{
  --ground:#E9EAE5; --panel:#FFFFFF; --panel-2:#F3F3EF;
  --ink:#16202E; --ink-mid:#47586B; --ink-dim:#556575; --hair:#DEDFD8; --hair-2:#C9CBC1;
  --gold:#8A6816; --gold-hi:#7C5D12; --weft:#3C6C93;
  --shadow:0 1px 2px rgba(20,27,38,.05),0 12px 30px rgba(20,27,38,.07);
}}
:root[data-theme="light"]{--ground:#E9EAE5;--panel:#FFFFFF;--panel-2:#F3F3EF;--ink:#16202E;--ink-mid:#47586B;--ink-dim:#556575;--hair:#DEDFD8;--hair-2:#C9CBC1;--gold:#8A6816;--gold-hi:#7C5D12;--weft:#3C6C93;--shadow:0 1px 2px rgba(20,27,38,.05),0 12px 30px rgba(20,27,38,.07)}
:root[data-theme="dark"]{--ground:#0E1524;--panel:#141E2E;--panel-2:#18263A;--ink:#DBE5F1;--ink-mid:#93A6BC;--ink-dim:#8497AE;--hair:#1E2E45;--hair-2:#2A3E5C;--gold:#CFA23A;--gold-hi:#E7BE58;--weft:#5C90BE;--shadow:0 1px 0 rgba(255,255,255,.03),0 14px 34px rgba(0,0,0,.34)}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:var(--ground);color:var(--ink);font-family:var(--sans);font-size:16px;line-height:1.66;-webkit-font-smoothing:antialiased}
a{color:var(--gold);text-decoration:none}a:hover{text-decoration:underline}
b,strong{color:var(--ink)}
::selection{background:color-mix(in srgb,var(--gold) 30%,transparent)}
:focus-visible{outline:2px solid var(--gold);outline-offset:2px;border-radius:2px}
.bar{position:sticky;top:0;z-index:80;display:flex;align-items:center;gap:14px;padding:11px 26px;
  background:color-mix(in srgb,var(--ground) 88%,transparent);backdrop-filter:blur(9px);border-bottom:1px solid var(--hair)}
.bar .brand{display:flex;align-items:center;gap:10px;font-family:var(--mono);font-size:11px;letter-spacing:.24em;
  text-transform:uppercase;color:var(--ink-mid);white-space:nowrap}
.bar .brand b{color:var(--gold)}
.bar nav{margin-left:auto;display:flex;gap:4px;flex-wrap:wrap}
.bar nav a{font-family:var(--mono);font-size:11px;color:var(--ink-mid);padding:6px 10px;border-radius:8px}
.bar nav a:hover{color:var(--gold);text-decoration:none}
.toggle{font-family:var(--mono);font-size:11px;color:var(--ink-mid);background:transparent;border:1px solid var(--hair-2);
  border-radius:20px;padding:6px 13px;cursor:pointer;white-space:nowrap}
.toggle:hover{border-color:var(--gold);color:var(--gold)}
.hero{border-bottom:1px solid var(--hair)}
.hero .in{max-width:1120px;margin:0 auto;padding:52px 30px 40px}
.kicker{font-family:var(--mono);font-size:11px;letter-spacing:.32em;text-transform:uppercase;color:var(--ink-mid)}
.hero h1{font-family:var(--serif);font-weight:600;font-size:clamp(34px,5vw,54px);line-height:1.02;letter-spacing:-.02em;margin:12px 0 0;text-wrap:balance}
.hero h1 em{font-style:italic;color:var(--gold)}
.hero .dek{color:var(--ink-mid);max-width:70ch;margin:16px 0 0;font-size:16.5px}
.hero .note{font-family:var(--mono);font-size:11.5px;color:var(--ink-mid);margin-top:14px}
.layout{max-width:1120px;margin:0 auto;padding:34px 30px 80px;display:grid;grid-template-columns:250px minmax(0,1fr);gap:44px}
@media(max-width:960px){.layout{grid-template-columns:1fr}.spine{display:none}}
.spine{position:sticky;top:64px;align-self:start;max-height:calc(100vh - 90px);overflow:auto;font-size:12.5px}
.spine .sp-part{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;margin:18px 0 6px}
.spine .sp-part a{color:var(--gold)}
.spine ol{list-style:none}
.spine li a{display:block;color:var(--ink-mid);padding:3px 0 3px 12px;border-left:2px solid var(--hair)}
.spine li a:hover{color:var(--ink);text-decoration:none}
.spine li.on a{color:var(--gold);border-left-color:var(--gold)}
article{margin-bottom:64px}
.parthead{border-bottom:1px solid var(--hair-2);margin-bottom:26px;padding-bottom:18px}
.parthead .pn{font-family:var(--mono);font-size:11px;letter-spacing:.28em;text-transform:uppercase;color:var(--gold)}
.parthead .pt{font-family:var(--serif);font-weight:600;font-size:clamp(26px,3.6vw,38px);letter-spacing:-.015em;margin:8px 0 0}
.parthead .pd{color:var(--ink-mid);margin-top:10px;max-width:68ch}
.parthead .src{font-family:var(--mono);font-size:11.5px;color:var(--ink-mid);margin-top:12px}
article h3{font-family:var(--serif);font-weight:600;font-size:23px;letter-spacing:-.01em;margin:40px 0 12px;scroll-margin-top:72px}
article h4{font-size:15.5px;margin:26px 0 8px;scroll-margin-top:72px}
article p{margin:0 0 13px;max-width:76ch;color:var(--ink-mid)}
article li{margin:0 0 7px;color:var(--ink-mid)}
article ul,article ol{margin:0 0 14px;padding-left:22px}
article blockquote{border-left:3px solid var(--gold);background:var(--panel);border-radius:0 10px 10px 0;
  padding:12px 18px;margin:0 0 16px}
article blockquote p{margin:0}
article hr{border:0;height:1px;background:var(--hair);margin:34px 0}
article code{font-family:var(--mono);font-size:.86em;background:var(--panel-2);border:1px solid var(--hair);border-radius:5px;padding:1px 6px;color:var(--gold-hi)}
article pre{font-family:var(--mono);font-size:12.5px;line-height:1.55;background:var(--panel);border:1px solid var(--hair);
  border-radius:12px;padding:16px 18px;overflow-x:auto;margin:0 0 16px;color:var(--ink-mid)}
.tw{overflow-x:auto;margin:0 0 18px;border:1px solid var(--hair);border-radius:12px;box-shadow:var(--shadow)}
table{width:100%;border-collapse:collapse;font-size:13.5px;background:var(--panel)}
th{font-family:var(--mono);font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-mid);
  text-align:left;padding:10px 14px;border-bottom:1px solid var(--hair-2);background:var(--panel-2)}
td{padding:10px 14px;border-bottom:1px solid var(--hair);vertical-align:top;color:var(--ink-mid)}
tr:last-child td{border-bottom:0}
footer{border-top:1px solid var(--hair)}
footer .in{max-width:1120px;margin:0 auto;padding:22px 30px;font-size:12.5px;color:var(--ink-mid)}
</style>
</head>
<body>
<div class="bar">
  <span class="brand">__MARK__ Spindleloom &middot; <b>Governance Handbook</b></span>
  <nav aria-label="Parts">
    <a href="#part-i">I &middot; Standard</a>
    <a href="#part-ii">II &middot; Story Craft</a>
    <a href="#part-iii">III &middot; Team &amp; ADO</a>
  </nav>
  <button class="toggle" id="themeToggle" aria-label="Toggle light or dark theme">&#9681; theme</button>
</div>
<header class="hero"><div class="in">
  <div class="kicker">Spindleloom &middot; Layer 3 &middot; Govern</div>
  <h1>The <em>Governance</em> Handbook</h1>
  <p class="dek">The three standards that govern how work is laid out, written and run -- the layout mandate,
  the story-craft rulebook, and the team + Azure DevOps operating fit -- on one page.</p>
  <p class="note">Generated view. Source of truth: <a href="../knowledge_hub/GOVERNANCE.md">knowledge_hub/GOVERNANCE.md</a> --
  edit the MD, then run <code>python hooks/build_governance_handbook.py</code>.</p>
</div></header>
<div class="layout">
  <nav class="spine" aria-label="Contents">__SPINE__</nav>
  <main>__ARTICLES__</main>
</div>
<footer><div class="in">
  Part of the <a href="readme.html">guides site</a> &middot; the by-role surface is the
  <a href="personas/index.html">Persona Field Handbook</a> &middot; the canonical end-to-end page is
  <a href="project-overview.html">project-overview.html</a>.
</div></footer>
<script>
const root=document.documentElement;
document.getElementById("themeToggle").addEventListener("click",()=>{
  const dark=matchMedia("(prefers-color-scheme:dark)").matches;
  const cur=root.getAttribute("data-theme")||(dark?"dark":"light");
  root.setAttribute("data-theme",cur==="dark"?"light":"dark");
});
const items=[...document.querySelectorAll(".spine li")];
const map={};items.forEach(li=>{const a=li.querySelector("a");if(a)map[a.getAttribute("href").slice(1)]=li;});
const spy=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){
  items.forEach(l=>l.classList.remove("on"));const li=map[e.target.id];if(li)li.classList.add("on");}}),
  {rootMargin:"-20% 0px -70% 0px"});
document.querySelectorAll("article h3[id]").forEach(h=>spy.observe(h));
</script>
</body>
</html>
"""


def render():
    articles, toc_parts = [], []
    for num, title, body_md in split_parts():
        toc = []
        body = md2html(body_md, "p" + num.lower(), toc)
        toc_parts.append((num, title, "part-" + num.lower(), toc))
        articles.append(
            '<article id="part-%s">'
            '<div class="parthead"><span class="pn">Part %s</span><h2 class="pt">%s</h2>'
            '<p class="pd">%s</p>'
            '<p class="src">Source of truth: <a href="../knowledge_hub/%s"><code>knowledge_hub/%s</code></a> (this part) '
            '-- this page is the generated reading view; edit the source, not this file.</p></div>'
            "%s</article>" % (num.lower(), num, title, DEKS.get(num, ""), SOURCE, SOURCE, body))
    spine = []
    for num, title, pid, toc in toc_parts:
        spine.append('<div class="sp-part"><a href="#%s">Part %s -- %s</a></div>' % (pid, num, title))
        spine.append("<ol>")
        for sid, txt in toc:
            spine.append('<li><a href="#%s">%s</a></li>' % (sid, H.escape(txt)))
        spine.append("</ol>")
    return (SHELL.replace("__MARK__", MARK)
                 .replace("__SPINE__", "\n".join(spine))
                 .replace("__ARTICLES__", "\n".join(articles)))


def main():
    check = "--check" in sys.argv[1:]
    page = render()
    if check:
        if not OUT.exists():
            print("build_governance_handbook: %s missing -- run the generator" % OUT.name)
            return 1
        current = OUT.read_text(encoding="utf-8").replace("\r\n", "\n")
        if current.strip() != page.strip():
            print("build_governance_handbook: STALE -- governance-handbook.html out of sync with GOVERNANCE.md; run `python hooks/build_governance_handbook.py`")
            return 1
        print("build_governance_handbook: in sync")
        return 0
    crlf = OUT.exists() and b"\r\n" in OUT.read_bytes()
    OUT.write_bytes((page.replace("\n", "\r\n") if crlf else page).encode("utf-8"))
    print("build_governance_handbook: wrote %s" % OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
