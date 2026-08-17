#!/usr/bin/env python3
"""
render.py -- builds the static AI-safety concept wiki from store/graph.json.

Usage:
    python tools/render.py

Reads store/graph.json (read-only) and completely regenerates site/ next to it.
The JSON is the single source of truth: site/ is deleted and rebuilt on every run.

Requires the third-party "markdown" package (pip install markdown). The script
will try to install it automatically if it is missing.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
import urllib.request
import urllib.error
from collections import defaultdict
from pathlib import Path

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------

TOOLS_DIR = Path(__file__).resolve().parent
BASE_DIR = TOOLS_DIR.parent
STORE_PATH = BASE_DIR / "store" / "graph.json"
SITE_DIR = BASE_DIR / "site"
ASSETS_DIR = SITE_DIR / "assets"
HELP_SHOTS_DIR = BASE_DIR / "help-shots"  # source screenshots for the help page (site/ is wiped)

# --------------------------------------------------------------------------
# Dependency bootstrap
# --------------------------------------------------------------------------

try:
    import markdown as md
except ImportError:
    print("[render] 'markdown' package not found; attempting `pip install markdown` ...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "markdown"])
        import markdown as md  # noqa: E402
    except Exception as exc:  # pragma: no cover
        print(f"[render] FATAL: could not install 'markdown': {exc}")
        print("[render] Install it manually with: pip install markdown")
        sys.exit(1)

# --------------------------------------------------------------------------
# Kind metadata
# --------------------------------------------------------------------------

# internal kind key -> (json collection key, output directory name, human label)
KIND_INFO = {
    "concept":    ("concepts",     "concept",    "concept"),
    "edge":       ("edges",        "edge",       "edge"),
    "theme":      ("themes",       "theme",      "theme"),
    "supertheme": ("superthemes",  "supertheme", "supertheme"),
    "superedge":  ("superedges",   "superedge",  "super edge"),
    "tissue":     ("tissueThemes", "tissue",     "connective theme"),
    "story":      ("paperStories", "story",      "stories"),
}

KIND_DIR = {k: v[1] for k, v in KIND_INFO.items()}
KIND_LABEL = {k: v[2] for k, v in KIND_INFO.items()}

# Figures are per-paper (store key "figures" is a dict keyed by paper id), so
# they sit outside KIND_INFO's generic collection loop; pages land at
# site/figure/<paperId>--<figureId>.html.
KIND_DIR["figure"] = "figure"
KIND_LABEL["figure"] = "figure"

# page kinds whose html lives at the site root (everything else is one dir down)
ROOT_KINDS = {"index", "help"}

# --------------------------------------------------------------------------
# Load data
# --------------------------------------------------------------------------


def load_data() -> dict:
    with open(STORE_PATH, encoding="utf-8") as f:
        return json.load(f)


# --------------------------------------------------------------------------
# Text helpers
# --------------------------------------------------------------------------


def deverb(type_str: str) -> str:
    """Turn a kebab-case verb-phrase edge type into readable words."""
    return type_str.replace("-", " ")


def esc(s: str) -> str:
    return html.escape(s, quote=True)


# --------------------------------------------------------------------------
# Main builder
# --------------------------------------------------------------------------


class SiteBuilder:
    def __init__(self, data: dict):
        self.data = data
        self.papers = {p["id"]: p for p in data["papers"]}
        self.concepts = {c["id"]: c for c in data["concepts"]}
        self.edges = {e["id"]: e for e in data["edges"]}
        self.themes = {t["id"]: t for t in data["themes"]}
        self.superthemes = {t["id"]: t for t in data["superthemes"]}
        self.superedges = {e["id"]: e for e in data["superedges"]}
        self.tissues = {t["id"]: t for t in data["tissueThemes"]}
        self.paper_stories = {e["id"]: e for e in data.get("paperStories") or []}
        self.figures = data.get("figures") or {}
        self.paper_overlay_narrative = {
            e["paper"]: e.get("narrative", "")
            for e in (data.get("paperOverlay") or {}).get("papers", [])}

        self.unresolved: list[tuple[str, str, str]] = []  # (from_kind, from_id, target_id)
        self.markdown_artifacts: list[tuple[str, str]] = []  # (page, artifact)

        self._build_indices()
        self._build_registry()

    # ---- derived indices ----------------------------------------------

    def _build_indices(self):
        d = self.data

        # concept parent/children
        self.children_of: dict[str, list[str]] = defaultdict(list)
        for c in d["concepts"]:
            if c["parent"]:
                self.children_of[c["parent"]].append(c["id"])
        for k in self.children_of:
            self.children_of[k].sort(key=lambda cid: self.concepts[cid]["name"].lower())

        # edges touching each concept
        self.edges_of_concept: dict[str, list[dict]] = defaultdict(list)
        for e in d["edges"]:
            self.edges_of_concept[e["source"]].append(e)
            if e["target"] != e["source"]:
                self.edges_of_concept[e["target"]].append(e)

        # themes containing each concept (lenses)
        self.themes_of_concept: dict[str, list[str]] = defaultdict(list)
        for t in d["themes"]:
            for m in t["members"]:
                self.themes_of_concept[m].append(t["id"])

        # superthemes containing each theme
        self.superthemes_of_theme: dict[str, list[str]] = defaultdict(list)
        for st in d["superthemes"]:
            for m in st["members"]:
                self.superthemes_of_theme[m].append(st["id"])

        # superedges touching each theme
        self.superedges_of_theme: dict[str, list[dict]] = defaultdict(list)
        for se in d["superedges"]:
            self.superedges_of_theme[se["source"]].append(se)
            if se["target"] != se["source"]:
                self.superedges_of_theme[se["target"]].append(se)

        # superedges grouped by their supertheme
        self.superedges_of_supertheme: dict[str, list[dict]] = defaultdict(list)
        for se in d["superedges"]:
            self.superedges_of_supertheme[se["supertheme"]].append(se)

        # edges grouped by the theme that motivated them
        self.edges_of_theme: dict[str, list[dict]] = defaultdict(list)
        for e in d["edges"]:
            self.edges_of_theme[e["motivatedByTheme"]].append(e)

        # tissue themes containing each edge
        self.tissues_of_edge: dict[str, list[str]] = defaultdict(list)
        for tt in d["tissueThemes"]:
            for m in tt["members"]:
                self.tissues_of_edge[m].append(tt["id"])

        # paper lens: (paper, concept) -> origin, first locator in that paper,
        # and each paper's concepts by role in order of first appearance
        self.origin_of: dict[tuple[str, str], dict] = {}
        self.first_loc: dict[tuple[str, str], dict] = {}
        self.concepts_of_paper: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
        for c in d["concepts"]:
            for o in c["origins"]:
                self.origin_of[(o["paper"], c["id"])] = o
                self.concepts_of_paper[o["paper"]][o["role"]].append(c["id"])
            for loc in c.get("locators", []):
                key = (loc["paper"], c["id"])
                if key not in self.first_loc or loc["page"] < self.first_loc[key]["page"]:
                    self.first_loc[key] = loc
        for pid, by_role in self.concepts_of_paper.items():
            for role in by_role:
                by_role[role].sort(key=lambda cid: (
                    self.first_loc.get((pid, cid), {"page": 999})["page"],
                    self.concepts[cid]["name"].lower()))

    # ---- global id registry for wiki-link resolution -------------------

    def edge_sentence(self, e: dict) -> str:
        return (f"{self.concepts[e['source']]['name']} — {deverb(e['type'])} "
                f"→ {self.concepts[e['target']]['name']}")

    def superedge_sentence(self, e: dict) -> str:
        return (f"{self.themes[e['source']]['name']} — {deverb(e['type'])} "
                f"→ {self.themes[e['target']]['name']}")

    def _build_registry(self):
        paper_alt = "|".join(re.escape(pid) for pid in self.papers)
        self.cite_re = re.compile(
            r'\((' + paper_alt + r'), (?=[^)]*pp?\. ?\d)([^()<>]{1,300})\)')
        self.cite_seg_re = re.compile(r'§"([^"]{1,150})", (pp?\. (\d+)(?:[-–]\d+)?)')
        self.cite_page_re = re.compile(r'pp?\. ?(\d+)(?:[-–]\d+)?(?![^<]*</a>)')
        self.registry: dict[str, tuple[str, str]] = {}
        for c in self.data["concepts"]:
            self.registry[c["id"]] = ("concept", c["name"])
        for t in self.data["themes"]:
            self.registry[t["id"]] = ("theme", t["name"])
        for t in self.data["superthemes"]:
            self.registry[t["id"]] = ("supertheme", t["name"])
        for t in self.data["tissueThemes"]:
            self.registry[t["id"]] = ("tissue", t["name"])
        for e in self.data["edges"]:
            self.registry[e["id"]] = ("edge", self.edge_sentence(e))
        for e in self.data["superedges"]:
            self.registry[e["id"]] = ("superedge", self.superedge_sentence(e))

    # ---- href helpers ----------------------------------------------------

    def href(self, from_kind: str, to_kind: str, to_id: str | None) -> str:
        if to_kind == "index":
            rel = "index.html"
        elif to_kind == "help":
            rel = "help.html"
        else:
            rel = f"{KIND_DIR[to_kind]}/{to_id}.html"
        return rel if from_kind in ROOT_KINDS else "../" + rel

    def asset_href(self, from_kind: str, name: str) -> str:
        rel = f"assets/{name}"
        return rel if from_kind in ROOT_KINDS else "../" + rel

    def paper_href(self, paper_id: str) -> str:
        p = self.papers[paper_id]
        return f"https://arxiv.org/abs/{p['arxiv']}"

    def pdf_href(self, from_kind: str, paper_id: str, page: int | None = None) -> str:
        href = self.asset_href(from_kind, f"papers/{paper_id}.pdf")
        return f"{href}#page={page}" if page else href

    # ---- sources / citations ---------------------------------------------

    def dedup_locators(self, locs: list[dict]) -> list[dict]:
        order = {pid: i for i, pid in enumerate(self.papers)}
        seen, out = set(), []
        for loc in locs:
            key = (loc["paper"], loc["section"], loc["page"])
            if key in seen:
                continue
            seen.add(key)
            out.append(loc)
        out.sort(key=lambda l: (order.get(l["paper"], 99), l["page"], l["section"].lower()))
        return out

    def cite_link(self, page_kind: str, loc: dict) -> str:
        return (f'<a class="cite" href="{self.pdf_href(page_kind, loc["paper"], loc["page"])}" '
                f'target="_blank" rel="noopener">&sect;&ldquo;{esc(loc["section"])}&rdquo;, p. {loc["page"]}</a>')

    def sources_block(self, page_kind: str, locs: list[dict],
                      paper_first: str | None = None, collapsible: bool = False) -> str:
        """Grouped-by-paper citation list, every entry deep-linking into the
        shipped PDF at its page. Returns '' if there is nothing to cite."""
        locs = self.dedup_locators(locs)
        if not locs:
            return ""
        if paper_first:
            locs = ([l for l in locs if l["paper"] == paper_first]
                    + [l for l in locs if l["paper"] != paper_first])
        groups: dict[str, list[dict]] = {}
        for loc in locs:
            groups.setdefault(loc["paper"], []).append(loc)
        parts = []
        for pid, ls in groups.items():
            p = self.papers[pid]
            title_link = (f'<a href="{self.paper_href(pid)}" target="_blank" rel="noopener">'
                          f'{esc(p["title"])}</a>')
            items = "".join(f"<li>{self.cite_link(page_kind, l)}</li>" for l in ls)
            parts.append(f'<li class="source-paper">{title_link}'
                         f'<ul class="source-locs">{items}</ul></li>')
        inner = f'<ul class="sources">{"".join(parts)}</ul>'
        if collapsible:
            n, m = len(locs), len(groups)
            word = "passage" if n == 1 else "passages"
            pw = "paper" if m == 1 else "papers"
            return (f'<details class="sources-details"><summary>{n} source {word} '
                    f'in {m} {pw}</summary>{inner}</details>')
        return inner

    def theme_locators(self, tid: str) -> list[dict]:
        return [loc for cid in self.themes[tid]["members"]
                for loc in self.concepts[cid].get("locators", [])]

    def edge_locators(self, e: dict) -> list[dict]:
        return (self.concepts[e["source"]].get("locators", [])
                + self.concepts[e["target"]].get("locators", []))

    # ---- markdown / math / wikilink pipeline ------------------------------

    MATH_RE = re.compile(r"\$\$(.+?)\$\$|\$([^$]+?)\$", re.S)
    WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")

    def process_body(self, text: str, from_kind: str, from_id: str) -> str:
        """Markdown-render prose while protecting math spans and resolving
        [[id]] / [[id|label]] wiki-links against the global registry."""

        # 1. protect math spans so markdown/html-escaping never touches them
        math_store: list[str] = []

        def math_sub(m: re.Match) -> str:
            idx = len(math_store)
            if m.group(1) is not None:
                math_store.append("$$" + m.group(1) + "$$")
            else:
                math_store.append("$" + m.group(2) + "$")
            return f"MATH{idx}"

        text = self.MATH_RE.sub(math_sub, text)

        # 2. protect wiki-links
        link_store: list[tuple[str, str | None]] = []

        def link_sub(m: re.Match) -> str:
            target_id = m.group(1).strip()
            label = m.group(2).strip() if m.group(2) else None
            idx = len(link_store)
            link_store.append((target_id, label))
            return f"LINK{idx}"

        text = self.WIKILINK_RE.sub(link_sub, text)

        # 3. markdown conversion (paragraphs, *emphasis*)
        body_html = md.markdown(text)

        # 4. restore math verbatim (HTML-escaped so raw LaTeX renders as text
        #    for KaTeX to find, rather than being parsed as markup)
        def restore_math(m: re.Match) -> str:
            raw = math_store[int(m.group(1))]
            return html.escape(raw, quote=False)

        body_html = re.sub(r"MATH(\d+)", restore_math, body_html)

        # 5. restore wiki-links as real anchors
        def restore_link(m: re.Match) -> str:
            idx = int(m.group(1))
            target_id, label = link_store[idx]
            entry = self.registry.get(target_id)
            if entry is None:
                self.unresolved.append((from_kind, from_id, target_id))
                return esc(label if label else target_id)
            to_kind, display = entry
            text_out = label if label else display
            href = self.href(from_kind, to_kind, target_id)
            return f'<a href="{href}">{esc(text_out)}</a>'

        body_html = re.sub(r"LINK(\d+)", restore_link, body_html)

        # 6. turn inline citations like (paper, §"Section", p. N; Table 3, p. M)
        #    into PDF deep links: quoted-section segments link whole, any
        #    leftover bare page refs link individually
        def linkify_cite(m: re.Match) -> str:
            pid, inner = m.group(1), m.group(2)

            def link_seg(sm: re.Match) -> str:
                section, ptext, first = sm.group(1), sm.group(2), int(sm.group(3))
                href = self.pdf_href(from_kind, pid, first)
                return (f'<a class="cite" href="{href}" target="_blank" rel="noopener">'
                        f'§"{section}", {ptext}</a>')

            def link_page(pm: re.Match) -> str:
                href = self.pdf_href(from_kind, pid, int(pm.group(1)))
                return (f'<a class="cite" href="{href}" target="_blank" rel="noopener">'
                        f'{pm.group(0)}</a>')

            inner = self.cite_seg_re.sub(link_seg, inner)
            inner = self.cite_page_re.sub(link_page, inner)
            return f'({pid}, {inner})'

        body_html = self.cite_re.sub(linkify_cite, body_html)

        return body_html

    # ---- page shell --------------------------------------------------

    def shell(self, page_kind: str, title: str, body: str) -> str:
        # Content-hash version on the assets that change between deploys, so
        # returning visitors never pair fresh HTML with a stale cached
        # stylesheet (Netlify caches /assets/* for a week).
        css_href = f'{self.asset_href(page_kind, "style.css")}?v={ASSET_VERSION}'
        popup_js = f'{self.asset_href(page_kind, "popup.js")}?v={ASSET_VERSION}'
        katex_css = self.asset_href(page_kind, "katex.min.css")
        katex_js = self.asset_href(page_kind, "katex.min.js")
        autorender_js = self.asset_href(page_kind, "auto-render.min.js")
        index_href = self.href(page_kind, "index", None)
        help_href = self.href(page_kind, "help", None)
        help_current = ' aria-current="page"' if page_kind == "help" else ''
        label = KIND_LABEL.get(page_kind, "")

        if KATEX_LOCAL:
            katex_head = (
                f'<link rel="stylesheet" href="{katex_css}">\n'
                f'    <script defer src="{katex_js}"></script>\n'
                f'    <script defer src="{autorender_js}" '
                f'onload="renderMathInElement(document.body, katexOptions);"></script>'
            )
        else:
            katex_head = (
                '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">\n'
                '    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>\n'
                '    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js" '
                'onload="renderMathInElement(document.body, katexOptions);"></script>'
            )

        return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="color-scheme" content="light dark">
    <title>{esc(title)}</title>
    <link rel="stylesheet" href="{css_href}">
    <script defer src="{popup_js}"></script>
    {katex_head}
    <script>
      var katexOptions = {{
        delimiters: [
          {{left: "$$", right: "$$", display: true}},
          {{left: "$", right: "$", display: false}}
        ],
        throwOnError: false
      }};
    </script>
  </head>
  <body class="pk-{page_kind}">
    <header class="site-header">
      <div class="header-inner">
        <a class="home-link" href="{index_href}">{'&larr; ' if page_kind != 'index' else ''}<b>Explore</b><span class="home-sub">an AI safety wiki</span></a>
        <span class="header-tools">{f'<span class="kind-badge kind-{page_kind}">{esc(label)}</span>' if label else ''}<a class="help-link" href="{help_href}"{help_current}>Help</a></span>
      </div>
    </header>
    <div class="page">
      <main>
{body}
      </main>
      <footer class="site-footer">
        <a href="{index_href}">&larr; Back to index</a>
      </footer>
    </div>
  </body>
</html>
"""

    # ---- small rendering helpers ---------------------------------------

    def concept_link(self, page_kind: str, cid: str) -> str:
        c = self.concepts[cid]
        href = self.href(page_kind, "concept", cid)
        return f'<a href="{href}">{esc(c["name"])}</a>'

    def theme_link(self, page_kind: str, tid: str) -> str:
        t = self.themes[tid]
        href = self.href(page_kind, "theme", tid)
        return f'<a href="{href}">{esc(t["name"])}</a>'

    def supertheme_link(self, page_kind: str, tid: str) -> str:
        t = self.superthemes[tid]
        href = self.href(page_kind, "supertheme", tid)
        return f'<a href="{href}">{esc(t["name"])}</a>'

    def tissue_link(self, page_kind: str, tid: str) -> str:
        t = self.tissues[tid]
        href = self.href(page_kind, "tissue", tid)
        return f'<a href="{href}">{esc(t["name"])}</a>'

    def edge_sentence_link(self, page_kind: str, e: dict) -> str:
        """Whole-sentence link to an edge page (used for member/lens listings)."""
        href = self.href(page_kind, "edge", e["id"])
        sentence = self.edge_sentence(e)
        tag = ' <span class="tag hindsight">hindsight</span>' if e["hindsight"] else ""
        return f'<a href="{href}">{esc(sentence)}</a>{tag}'

    def superedge_sentence_link(self, page_kind: str, e: dict) -> str:
        href = self.href(page_kind, "superedge", e["id"])
        sentence = self.superedge_sentence(e)
        tag = ' <span class="tag hindsight">hindsight</span>' if e["hindsight"] else ""
        return f'<a href="{href}">{esc(sentence)}</a>{tag}'

    def connection_line(self, page_kind: str, e: dict, focus_cid: str) -> str:
        """One edge from the point of view of focus_cid: focus side bolded,
        verb phrase linking to the edge page."""
        src_name = self.concepts[e["source"]]["name"]
        tgt_name = self.concepts[e["target"]]["name"]
        verb_href = self.href(page_kind, "edge", e["id"])
        verb_html = f'<a href="{verb_href}">{esc(deverb(e["type"]))}</a>'
        if e["source"] == focus_cid:
            left, right = f"<strong>{esc(src_name)}</strong>", esc(tgt_name)
        else:
            left, right = esc(src_name), f"<strong>{esc(tgt_name)}</strong>"
        tag = ' <span class="tag hindsight">hindsight</span>' if e["hindsight"] else ""
        return f"{left} — {verb_html} → {right}{tag}"

    def intro_block(self, page_kind: str, item: dict) -> str:
        """Gentle two-paragraph page introduction, when the item has one."""
        intro = (item.get("intro") or "").strip()
        if not intro:
            return ""
        return (f'<div class="page-intro">'
                f'{self.process_body(intro, page_kind, item["id"])}</div>')

    def origin_line(self, origins: list[dict]) -> str:
        parts = []
        for o in origins:
            paper = self.papers[o["paper"]]
            parts.append(
                f'<a href="{self.paper_href(o["paper"])}" '
                f'target="_blank" rel="noopener">{esc(paper["title"])}</a> '
                f'— <span class="role role-{esc(o["role"])}">{esc(o["role"])}</span>'
            )
        return "; ".join(parts)

    # ---- page builders --------------------------------------------------

    def build_concept_page(self, c: dict) -> str:
        pk = "concept"
        parts = []

        parts.append(f"<h1>{esc(c['name'])}</h1>")
        parts.append(f'<p class="origins">{self.origin_line(c["origins"])}</p>')
        parts.append(f'<p class="lede">{esc(c["summary"])}</p>')
        parts.append(self.intro_block(pk, c))

        for s in c["sections"]:
            parts.append(f"<section class=\"prose-section\">")
            parts.append(f"<h2>{esc(s['heading'])}</h2>")
            parts.append(self.process_body(s["body"], pk, c["id"]))
            parts.append("</section>")

        parts.append('<hr class="divider">')

        # Part of / Contains
        if c["parent"]:
            parts.append("<section class=\"nav-block\"><h2>Part of</h2><p>"
                          + self.concept_link(pk, c["parent"]) + "</p></section>")
        children = self.children_of.get(c["id"], [])
        if children:
            items = "".join(f"<li>{self.concept_link(pk, cid)}</li>" for cid in children)
            parts.append(f"<section class=\"nav-block\"><h2>Contains</h2><ul>{items}</ul></section>")

        # Connections
        conns = sorted(
            self.edges_of_concept.get(c["id"], []),
            key=lambda e: self.concepts[e["target"] if e["source"] == c["id"] else e["source"]]["name"].lower(),
        )
        if conns:
            items = [f"<li>{self.connection_line(pk, e, c['id'])}</li>" for e in conns]
            parts.append(f"<section class=\"nav-block\"><h2>Connections</h2><ul class=\"connections\">"
                          + "".join(items) + "</ul></section>")

        # Lenses
        lens_ids = self.themes_of_concept.get(c["id"], [])
        if lens_ids:
            lens_ids_sorted = sorted(lens_ids, key=lambda tid: self.themes[tid]["name"].lower())
            items = "".join(f"<li>{self.theme_link(pk, tid)}</li>" for tid in lens_ids_sorted)
            parts.append(f"<section class=\"nav-block\"><h2>Lenses</h2><ul>{items}</ul></section>")

        # Sources
        if c["locators"]:
            parts.append(f"<section class=\"nav-block\"><h2>Sources</h2>"
                         f"{self.sources_block(pk, c['locators'])}</section>")

        return self.shell(pk, f"{c['name']} — Concept", "\n".join(parts))

    def build_edge_page(self, e: dict) -> str:
        pk = "edge"
        parts = []
        title = self.edge_sentence(e)
        parts.append(f"<h1>{esc(title)}</h1>")

        meta_bits = []
        if e["hindsight"]:
            meta_bits.append('<span class="tag hindsight">hindsight</span>')
        if e["groundedIn"]:
            paper = self.papers[e["groundedIn"]]
            meta_bits.append(
                f'grounded in <a href="{self.paper_href(e["groundedIn"])}" target="_blank" rel="noopener">'
                f'{esc(paper["title"])}</a>'
            )
        if e["motivatedByTheme"]:
            meta_bits.append("explored within the theme " + self.theme_link(pk, e["motivatedByTheme"]))
        if meta_bits:
            parts.append(f'<p class="edge-meta">{" &middot; ".join(meta_bits)}</p>')

        parts.append('<section class="prose-section">' + self.process_body(e["prose"], pk, e["id"]) + "</section>")

        parts.append('<hr class="divider">')
        parts.append(
            "<section class=\"nav-block\"><h2>Endpoints</h2><p>"
            + self.concept_link(pk, e["source"]) + " and " + self.concept_link(pk, e["target"])
            + "</p></section>"
        )

        tissue_ids = self.tissues_of_edge.get(e["id"], [])
        if tissue_ids:
            items = "".join(f"<li>{self.tissue_link(pk, tid)}</li>" for tid in sorted(
                tissue_ids, key=lambda tid: self.tissues[tid]["name"].lower()))
            parts.append(f"<section class=\"nav-block\"><h2>Appears in connective themes</h2><ul>{items}</ul></section>")

        src = self.sources_block(pk, self.edge_locators(e), paper_first=e.get("groundedIn"))
        if src:
            parts.append(f'<section class="nav-block"><h2>Sources</h2>'
                         f'<p class="section-note">Passages behind the two endpoint concepts'
                         f'{", grounding paper first" if e.get("groundedIn") else ""}.</p>{src}</section>')

        return self.shell(pk, f"{title} — Edge", "\n".join(parts))

    def build_theme_page(self, t: dict) -> str:
        pk = "theme"
        parts = []
        parts.append(f"<h1>{esc(t['name'])}</h1>")
        parts.append(self.intro_block(pk, t))
        parts.append('<section class="prose-section">' + self.process_body(t["narrative"], pk, t["id"]) + "</section>")

        parts.append('<hr class="divider">')

        walk = t.get("walk")
        if walk:
            steps = "".join(
                f'<li>{self.concept_link(pk, s["concept"])}'
                f'<div class="walk-prose">{self.process_body(s["prose"], pk, t["id"])}</div></li>'
                for s in walk
            )
            parts.append(
                f"<section class=\"nav-block\"><h2>Members &mdash; a guided walk</h2>"
                f"<ol class=\"walk\">{steps}</ol></section>"
            )
        else:
            items = "".join(f"<li>{self.concept_link(pk, cid)}</li>" for cid in t["members"])
            parts.append(f"<section class=\"nav-block\"><h2>Members</h2><ul>{items}</ul></section>")

        st_ids = self.superthemes_of_theme.get(t["id"], [])
        if st_ids:
            items = "".join(f"<li>{self.supertheme_link(pk, sid)}</li>" for sid in sorted(
                st_ids, key=lambda sid: self.superthemes[sid]["name"].lower()))
            parts.append(f"<section class=\"nav-block\"><h2>Superthemes</h2><ul>{items}</ul></section>")

        motivated = self.edges_of_theme.get(t["id"], [])
        if motivated:
            items = "".join(f"<li>{self.edge_sentence_link(pk, e)}</li>" for e in motivated)
            parts.append(f"<section class=\"nav-block\"><h2>Edges explored within this theme</h2><ul>{items}</ul></section>")

        se_list = self.superedges_of_theme.get(t["id"], [])
        if se_list:
            items = "".join(f"<li>{self.superedge_sentence_link(pk, e)}</li>" for e in se_list)
            parts.append(f"<section class=\"nav-block\"><h2>Super edges touching this theme</h2><ul>{items}</ul></section>")

        src = self.sources_block(pk, self.theme_locators(t["id"]), collapsible=True)
        if src:
            parts.append(f'<section class="nav-block"><h2>Sources</h2>'
                         f'<p class="section-note">Every passage behind this theme&rsquo;s member concepts.</p>'
                         f'{src}</section>')

        return self.shell(pk, f"{t['name']} — Theme", "\n".join(parts))

    def build_supertheme_page(self, t: dict) -> str:
        pk = "supertheme"
        parts = []
        parts.append(f"<h1>{esc(t['name'])}</h1>")
        parts.append(self.intro_block(pk, t))
        parts.append('<section class="prose-section">' + self.process_body(t["narrative"], pk, t["id"]) + "</section>")

        parts.append('<hr class="divider">')

        items = "".join(f"<li>{self.theme_link(pk, tid)}</li>" for tid in t["members"])
        parts.append(f"<section class=\"nav-block\"><h2>Member themes</h2><ul>{items}</ul></section>")

        se_list = self.superedges_of_supertheme.get(t["id"], [])
        if se_list:
            items = "".join(f"<li>{self.superedge_sentence_link(pk, e)}</li>" for e in se_list)
            parts.append(f"<section class=\"nav-block\"><h2>Super edges</h2><ul>{items}</ul></section>")

        st_locs = [loc for tid in t["members"] for loc in self.theme_locators(tid)]
        src = self.sources_block(pk, st_locs, collapsible=True)
        if src:
            parts.append(f'<section class="nav-block"><h2>Sources</h2>'
                         f'<p class="section-note">Every passage behind the concepts of this '
                         f'supertheme&rsquo;s member themes.</p>{src}</section>')

        return self.shell(pk, f"{t['name']} — Supertheme", "\n".join(parts))

    def build_superedge_page(self, e: dict) -> str:
        pk = "superedge"
        parts = []
        title = self.superedge_sentence(e)
        parts.append(f"<h1>{esc(title)}</h1>")

        meta_bits = []
        if e["hindsight"]:
            meta_bits.append('<span class="tag hindsight">hindsight</span>')
        if e["groundedIn"]:
            paper = self.papers[e["groundedIn"]]
            meta_bits.append(
                f'grounded in <a href="{self.paper_href(e["groundedIn"])}" target="_blank" rel="noopener">'
                f'{esc(paper["title"])}</a>'
            )
        meta_bits.append("part of the supertheme " + self.supertheme_link(pk, e["supertheme"]))
        parts.append(f'<p class="edge-meta">{" &middot; ".join(meta_bits)}</p>')

        parts.append('<section class="prose-section">' + self.process_body(e["prose"], pk, e["id"]) + "</section>")

        parts.append('<hr class="divider">')
        parts.append(
            "<section class=\"nav-block\"><h2>Endpoints</h2><p>"
            + self.theme_link(pk, e["source"]) + " and " + self.theme_link(pk, e["target"])
            + "</p></section>"
        )

        se_locs = self.theme_locators(e["source"]) + self.theme_locators(e["target"])
        src = self.sources_block(pk, se_locs, paper_first=e.get("groundedIn"), collapsible=True)
        if src:
            parts.append(f'<section class="nav-block"><h2>Sources</h2>'
                         f'<p class="section-note">Every passage behind the two endpoint '
                         f'themes&rsquo; concepts.</p>{src}</section>')

        return self.shell(pk, f"{title} — Super edge", "\n".join(parts))

    def build_tissue_page(self, t: dict) -> str:
        pk = "tissue"
        parts = []
        parts.append(f"<h1>{esc(t['name'])}</h1>")
        parts.append(self.intro_block(pk, t))
        parts.append('<section class="prose-section">' + self.process_body(t["narrative"], pk, t["id"]) + "</section>")

        parts.append('<hr class="divider">')

        items = []
        for eid in t["members"]:
            e = self.edges[eid]
            items.append(f"<li>{self.edge_sentence_link(pk, e)}</li>")
        parts.append(f"<section class=\"nav-block\"><h2>Member edges</h2><ul>{''.join(items)}</ul></section>")

        tt_locs = [loc for eid in t["members"] for loc in self.edge_locators(self.edges[eid])]
        src = self.sources_block(pk, tt_locs, collapsible=True)
        if src:
            parts.append(f'<section class="nav-block"><h2>Sources</h2>'
                         f'<p class="section-note">Every passage behind the concepts its member '
                         f'edges connect.</p>{src}</section>')

        return self.shell(pk, f"{t['name']} — Connective theme", "\n".join(parts))

    def build_figure_page(self, pid: str, item: dict, items: list[dict]) -> str:
        pk = "figure"
        p = self.papers[pid]
        page_id = f"{pid}--{item['id']}"
        story_href = self.href(pk, "story", pid)
        loc = {"paper": pid, "section": item["section"], "page": item["page"]}

        fig_story = (self.figures.get(pid) or {}).get("story") or {}
        story_seg = ""
        if fig_story.get("id"):
            story_seg = (f' &middot; in <a href="{story_href}#{esc(fig_story["id"])}">'
                         f'{esc(fig_story.get("tab") or "The experiments")}</a>')
        parts = [f"<h1>{esc(item['name'])}</h1>"]
        parts.append(
            f'<p class="edge-meta">{esc(item["label"])} of '
            f'<a href="{story_href}">{esc(p["title"])}</a>'
            f' &middot; {self.cite_link(pk, loc)}'
            f'{story_seg}</p>'
        )
        img_src = self.asset_href(pk, item["image"])
        parts.append(
            f'<figure class="figure-plate">'
            f'<a href="{img_src}" target="_blank" rel="noopener">'
            f'<img src="{img_src}" alt="{esc(item["label"])} — {esc(item["name"])}" loading="lazy">'
            f'</a></figure>'
        )
        for s in item.get("sections", []):
            parts.append('<section class="prose-section">')
            parts.append(f"<h2>{esc(s['heading'])}</h2>")
            parts.append(self.process_body(s["body"], pk, page_id))
            parts.append("</section>")

        parts.append('<hr class="divider">')
        idx = next(i for i, it in enumerate(items) if it["id"] == item["id"])
        neighbors = []
        for off, word in ((-1, "Previous"), (1, "Next")):
            j = idx + off
            if 0 <= j < len(items):
                n = items[j]
                n_href = self.href(pk, "figure", f"{pid}--{n['id']}")
                neighbors.append(f'<li>{word}: <a href="{n_href}">{esc(n["label"])} '
                                 f'&mdash; {esc(n["name"])}</a></li>')
        if neighbors:
            parts.append('<section class="nav-block"><h2>More figures from this paper</h2>'
                         f'<ul>{"".join(neighbors)}</ul></section>')
        parts.append(f'<section class="nav-block"><h2>Sources</h2>'
                     f'{self.sources_block(pk, [loc])}</section>')

        return self.shell(pk, f"{item['name']} — Figure", "\n".join(parts))

    def build_paper_story_page(self, entry: dict) -> str:
        pk = "story"
        pid = entry["id"]
        p = self.papers[pid]
        stories = entry["stories"]
        # The experiments story (the paper's figures as one connected arc) is a
        # story panel like the tellings, sourced from the figures collection.
        fig_story = (self.figures.get(pid) or {}).get("story")
        if fig_story:
            stories = stories + [fig_story]
        # Presentation order (stable): the big-picture telling lands first and is
        # the default tab; store order is unchanged.
        tab_rank = {"The big picture": 0, "Inside the paper": 1,
                    "Across the corpus": 2, "The experiments": 3}
        stories = sorted(stories, key=lambda s: tab_rank.get(s.get("tab"), len(tab_rank)))

        parts = []
        parts.append(f"<h1>{esc(p['title'])}</h1>")
        parts.append(
            f'<p class="edge-meta">'
            f'<a href="{self.paper_href(pid)}" target="_blank" rel="noopener">arXiv:{esc(p["arxiv"])}</a>'
            f' &middot; <a href="{self.pdf_href(pk, pid)}" target="_blank" rel="noopener">PDF</a>'
            f' &middot; {p["pages"]} pp.'
            f' &middot; <a href="{self.href(pk, "index", None)}#tab-papers">its place among the papers</a></p>'
        )
        fig_note = (
            ' <b>The experiments</b> explains the paper&rsquo;s experiments and '
            'results as one connected account, built from the paper&rsquo;s '
            'concepts, with its figures and tables attached as supporting '
            'evidence &mdash; each opening into a page of its own.'
            if fig_story else '')
        multi_note = (
            '<p class="section-note">One paper, several tellings. <b>The big '
            'picture</b> states the paper&rsquo;s own thesis and contributions in '
            'its own terms; <b>Inside the paper</b> follows the paper&rsquo;s own '
            'arc; <b>Across the corpus</b> '
            'traces how it connects to the other papers; <b>The concepts</b> '
            'lists everything the paper uses, in reading order.'
            + fig_note +
            ' Pick a tab, then '
            'use the +/&minus; toggles to open it level by level, or set a '
            'granularity to read the whole thing at that zoom.</p>'
        )
        single_note = (
            '<p class="section-note">This paper told as a story: chapters in '
            'reading order, each opening into the concepts and themes that carry '
            'it. Use the +/&minus; toggles to open the story level by level, or '
            'set a granularity to read the whole story at that zoom.</p>'
        )
        extra = []
        concepts_body = self._paper_concepts_panel(pid)
        if concepts_body:
            extra.append(("paper-concepts", "The concepts", concepts_body))
        parts.append(self._story_tabs(stories, pk, multi_note, single_note, extra,
                                      fig_pid=pid))
        parts.append(self.INDEX_TABS_JS)
        return self.shell(pk, f"{p['title']} — Stories", "\n".join(parts))

    # ---- index page: tabs + overlay tree --------------------------------

    def _overlay_theme_members(self, tid: str, pk: str = "index") -> str:
        """Member concepts of a theme, each expandable into its edges. When the
        theme has a walk, members follow its reading order and each step's
        connective prose is shown beneath the concept."""
        t = self.themes[tid]
        walk = t.get("walk")
        steps = walk if walk else [{"concept": cid, "prose": ""} for cid in t["members"]]
        items = []
        for step in steps:
            cid = step["concept"]
            clink = self.concept_link(pk, cid)
            prose = (step.get("prose") or "").strip()
            prose_html = (
                f'<div class="walk-prose">{self.process_body(prose, pk, tid)}</div>' if prose else ""
            )
            edges = sorted(
                self.edges_of_concept.get(cid, []),
                key=lambda e: self.concepts[e["target"] if e["source"] == cid else e["source"]]["name"].lower(),
            )
            if edges:
                n = len(edges)
                word = "connection" if n == 1 else "connections"
                lines = "".join(f"<li>{self.connection_line(pk, e, cid)}</li>" for e in edges)
                items.append(
                    f'<li class="walk-step"><details class="tree-node node-concept" data-depth="4">'
                    f'<summary>{clink} <span class="tree-count">({n} {word})</span></summary>'
                    f'<ul class="tree-edges">{lines}</ul></details>{prose_html}</li>'
                )
            else:
                items.append(f'<li class="walk-step tree-leaf">{clink}{prose_html}</li>')
        return f'<ul class="tree-concepts">{"".join(items)}</ul>'

    def _overlay_supertheme_threads(self, stid: str, pk: str = "index") -> str:
        """Superedges of a supertheme as a collapsible block inside its node."""
        se_list = self.superedges_of_supertheme.get(stid, [])
        if not se_list:
            return ""
        n = len(se_list)
        word = "thread" if n == 1 else "threads"
        items = "".join(f"<li>{self.superedge_sentence_link(pk, e)}</li>" for e in se_list)
        return (
            f'<details class="tree-node node-superedges" data-depth="4">'
            f'<summary>{n} {word} between these themes '
            f'<span class="tree-kind kind-superedge">super edges</span></summary>'
            f'<ul class="tree-edges">{items}</ul></details>'
        )

    def _overlay_node(self, node: dict, depth: int, arc_num: int | None = None,
                      pk: str = "index", fig_pid: str | None = None) -> str:
        """Recursively render one overlay node as a collapsible tree node.
        `fig_pid` names the paper whose figures `figure` refs resolve against
        (figure page ids are `<paper>--<figure>`)."""
        ref = node.get("ref")
        kind = ref["kind"] if ref else ("root" if depth == 0 else "arc")
        children = node.get("children", [])

        name_html = esc(node["name"])
        if ref:
            name_html = f'<a href="{self.href(pk, ref["kind"], ref["id"])}">{name_html}</a>'
        if kind == "arc" and arc_num is not None:
            name_html = f'<span class="arc-num">Chapter {arc_num}</span>{name_html}'

        badge = ""
        if kind in ("supertheme", "theme", "tissue", "concept", "edge"):
            badge = f' <span class="tree-kind kind-{kind}">{esc(KIND_LABEL[kind])}</span>'
        era = (node.get("era") or "").strip()
        if era:
            badge = f' <span class="era-tag">{esc(era)}</span>' + badge

        if kind == "root":
            count = f'{len(children)} chapter' + ("s" if len(children) != 1 else "")
        elif kind == "arc":
            child_kinds = {(ch.get("ref") or {}).get("kind") or "section" for ch in children}
            word = child_kinds.pop() if len(child_kinds) == 1 else "section"
            count = f'{len(children)} {word}' + ("s" if len(children) != 1 else "")
        elif kind == "supertheme":
            count = f'{len(children)} theme' + ("s" if len(children) != 1 else "")
        elif kind == "theme":
            n = len(self.themes[ref["id"]]["members"])
            count = f'{n} concept' + ("s" if n != 1 else "")
        elif kind == "tissue":
            n = len(self.tissues[ref["id"]]["members"])
            count = f'{n} edge' + ("s" if n != 1 else "")
        elif kind == "concept":
            n = len(self.edges_of_concept.get(ref["id"], []))
            count = (f'{n} connection' + ("s" if n != 1 else "")) if n else ""
        else:
            count = ""
        count_html = f' <span class="tree-count">({count})</span>' if count else ""

        body = []
        narrative = (node.get("narrative") or "").strip()
        if narrative:
            body.append(f'<div class="node-narrative">{self.process_body(narrative, pk, "overlay")}</div>')
        # Attached figures: supporting evidence for the node's claim, shown as
        # thumbnail + note, each leading to the figure's own page.
        atts = node.get("figures") or []
        if atts and fig_pid:
            items_by_id = {x["id"]: x
                           for x in (self.figures.get(fig_pid) or {}).get("items") or []}
            for att in atts:
                it = items_by_id.get(att.get("figure"))
                if it is None:
                    continue
                img = self.asset_href(pk, it["image"])
                fig_href = self.href(pk, "figure", f"{fig_pid}--{it['id']}")
                note_html = self.process_body((att.get("note") or "").strip(), pk, "overlay")
                body.append(
                    f'<div class="fig-entry">'
                    f'<a class="fig-thumb" href="{fig_href}">'
                    f'<img src="{img}" alt="{esc(it["label"])} &mdash; {esc(it["name"])}" '
                    f'loading="lazy"></a>'
                    f'<div class="fig-info">'
                    f'<p class="fig-title"><a href="{fig_href}">{esc(it["label"])} '
                    f'&mdash; {esc(it["name"])}</a></p>'
                    f'<div class="fig-note">{note_html}</div>'
                    f'</div></div>')
        for i, ch in enumerate(children, start=1):
            body.append(self._overlay_node(ch, depth + 1, arc_num=i if kind == "root" else None,
                                           pk=pk, fig_pid=fig_pid))
        if kind == "theme":
            body.append(self._overlay_theme_members(ref["id"], pk))
        if kind == "supertheme":
            body.append(self._overlay_supertheme_threads(ref["id"], pk))
        if kind == "tissue":
            lines = "".join(f"<li>{self.edge_sentence_link(pk, self.edges[eid])}</li>"
                            for eid in self.tissues[ref["id"]]["members"])
            body.append(f'<details class="tree-node node-tissue-edges" data-depth="4">'
                        f'<summary>member edges</summary>'
                        f'<ul class="tree-edges">{lines}</ul></details>')
        if kind == "concept":
            edges = sorted(
                self.edges_of_concept.get(ref["id"], []),
                key=lambda e: self.concepts[e["target"] if e["source"] == ref["id"] else e["source"]]["name"].lower(),
            )
            if edges:
                lines = "".join(f"<li>{self.connection_line(pk, e, ref['id'])}</li>" for e in edges)
                body.append(f'<details class="tree-node node-connections" data-depth="4">'
                            f'<summary>connections</summary>'
                            f'<ul class="tree-edges">{lines}</ul></details>')

        open_attr = " open" if kind == "root" else ""
        gran = {"root": 0, "arc": 1, "supertheme": 2, "theme": 3}.get(kind, depth)
        return (
            f'<details class="tree-node node-{kind}" id="node-{esc(node["id"])}" '
            f'data-depth="{gran}"{open_attr}>'
            f'<summary>{name_html}{badge}{count_html}</summary>'
            f'<div class="node-body">{"".join(body)}</div></details>'
        )

    def _story_has_kind(self, node: dict, kind: str) -> bool:
        ref = node.get("ref")
        if ref and ref.get("kind") == kind:
            return True
        return any(self._story_has_kind(ch, kind) for ch in node.get("children", []))

    def _story_has_figures(self, node: dict) -> bool:
        if node.get("figures"):
            return True
        return any(self._story_has_figures(ch) for ch in node.get("children", []))

    def _story_tabs(self, stories: list[dict], pk: str,
                    multi_note: str, single_note: str,
                    extra: list[tuple[str, str, str]] = (),
                    fig_pid: str | None = None) -> str:
        """The sub-tab row and its panels. `extra` adds non-story tabs after
        the tellings, as (panel_id, tab_label, body_html) triples — they share
        the same tab/hash behaviour as the story panels. `fig_pid` resolves any
        figure refs (the experiments story) against that paper's figures."""
        parts = []
        if len(stories) + len(extra) > 1:
            parts.append(multi_note)
            buttons = []
            for i, (sid, label) in enumerate(
                    [(s["id"], s.get("tab") or s["name"]) for s in stories]
                    + [(xid, xlabel) for xid, xlabel, _ in extra]):
                active = ' active' if i == 0 else ''
                selected = 'true' if i == 0 else 'false'
                buttons.append(
                    f'<button type="button" class="subtab{active}" id="subtabbtn-{esc(sid)}" '
                    f'role="tab" aria-selected="{selected}" aria-controls="{esc(sid)}">'
                    f'{esc(label)}</button>'
                )
            parts.append('<nav class="subtabs" role="tablist" aria-label="Story lenses">'
                         + "".join(buttons) + '</nav>')
        else:
            parts.append(single_note)

        for i, s in enumerate(stories):
            hidden = '' if i == 0 else ' hidden'
            if self._story_has_figures(s):
                # The experiments story: no theme layer; concept nodes carry
                # the explanation with figures attached as evidence.
                levels = [(0, "root claim"), (1, "chapters"),
                          (4, "concepts"), (5, "everything")]
            else:
                levels = [(0, "root claim"), (1, "chapters")]
                if self._story_has_kind(s, "supertheme"):
                    levels.append((2, "superthemes"))
                levels += [(3, "themes"), (4, "concepts"), (5, "everything")]
            gran_buttons = "".join(
                f'<button type="button" class="gran-chip" data-gran="{g}" '
                f'data-scope="{esc(s["id"])}">{label}</button>'
                for g, label in levels
            )
            parts.append(
                f'<div class="story-panel" id="{esc(s["id"])}" role="tabpanel" '
                f'aria-labelledby="subtabbtn-{esc(s["id"])}"{hidden}>\n'
                f'{self.intro_block(pk, s)}\n'
                f'<p class="tree-controls"><span class="controls-label">Read at</span>{gran_buttons}</p>\n'
                f'<div class="overlay-tree">{self._overlay_node(s, 0, pk=pk, fig_pid=fig_pid)}</div>\n</div>'
            )
        for xid, _xlabel, body in extra:
            hidden = '' if not stories else ' hidden'
            parts.append(
                f'<div class="story-panel" id="{esc(xid)}" role="tabpanel" '
                f'aria-labelledby="subtabbtn-{esc(xid)}"{hidden}>\n{body}\n</div>'
            )
        return "\n".join(parts)

    def _index_tab_superthemes(self) -> str:
        pk = "index"
        parts = []
        parts.append("<p class=\"section-note\">Eight superthemes, each grouping several themes.</p>")
        parts.append("<ul class=\"supertheme-list\">")
        for st in sorted(self.data["superthemes"], key=lambda t: t["name"].lower()):
            theme_items = "".join(f"<li>{self.theme_link(pk, tid)}</li>" for tid in st["members"])
            parts.append(
                f"<li>{self.supertheme_link(pk, st['id'])}"
                f"<ul class=\"theme-sublist\">{theme_items}</ul></li>"
            )
        parts.append("</ul>")
        return "\n".join(parts)

    def _index_tab_tissues(self) -> str:
        pk = "index"
        parts = []
        parts.append("<p class=\"section-note\">Twenty-eight connective themes, each a short thread of edges.</p>")
        parts.append("<ul>")
        for tt in sorted(self.data["tissueThemes"], key=lambda t: t["name"].lower()):
            n = len(tt["members"])
            member_word = "edge" if n == 1 else "edges"
            parts.append(f"<li>{self.tissue_link(pk, tt['id'])} <span class=\"muted\">({n} {member_word})</span></li>")
        parts.append("</ul>")
        return "\n".join(parts)

    def _index_tab_concepts(self) -> str:
        pk = "index"
        parts = []
        by_letter: dict[str, list[dict]] = defaultdict(list)
        for c in self.data["concepts"]:
            letter = c["name"][0].upper()
            if not letter.isalpha():
                letter = "#"
            by_letter[letter].append(c)
        for letter in sorted(by_letter):
            items = "".join(
                f"<li>{self.concept_link(pk, c['id'])}</li>"
                for c in sorted(by_letter[letter], key=lambda c: c["name"].lower())
            )
            parts.append(f"<h3 class=\"letter-head\">{esc(letter)}</h3><ul class=\"concept-az\">{items}</ul>")
        return "\n".join(parts)

    def _index_tab_papers(self) -> str:
        pk = "index"
        parts = [
            '<p class="section-note">The corpus, paper by paper. Each paper opens '
            'into a page of its own: the paper told as stories, and every concept '
            'it uses in reading order.</p>',
            '<div class="paper-cards">',
        ]
        for p in self.data["papers"]:
            pid = p["id"]
            page = self.href(pk, "story", pid)
            n = sum(len(v) for v in self.concepts_of_paper.get(pid, {}).values())
            n_figs = len((self.figures.get(pid) or {}).get("items") or [])
            fig_meta = f' &middot; {n_figs} figures' if n_figs else ''
            parts.append(
                f'<div class="paper-card">'
                f'<h3 class="pc-title"><a href="{page}">{esc(p["title"])}</a></h3>'
                f'<p class="edge-meta">'
                f'<a href="{self.paper_href(pid)}" target="_blank" rel="noopener">arXiv:{esc(p["arxiv"])}</a>'
                f' &middot; <a href="{self.pdf_href(pk, pid)}" target="_blank" rel="noopener">PDF</a>'
                f' &middot; {p["pages"]} pp. &middot; {n} concepts{fig_meta}</p>'
                f'</div>'
            )
        parts.append("</div>")
        return "\n".join(parts)

    # ---- index page: paper overlay tree ----------------------------------

    ROLE_ORDER = ("introduced", "refined", "inherited")
    ROLE_HEADS = {
        "introduced": "Introduced here",
        "refined": "Refined here",
        "inherited": "Inherited — used, not invented here",
    }

    def _paper_concept_item(self, pid: str, cid: str, pk: str) -> str:
        """One concept as it appears in one paper: link, deep-linked first
        locator, the paper's own take on it as prose, expandable connections."""
        clink = self.concept_link(pk, cid)
        loc = self.first_loc.get((pid, cid))
        cite = f' <span class="tree-count">{self.cite_link(pk, loc)}</span>' if loc else ""
        origin = self.origin_of.get((pid, cid), {})
        summary = (origin.get("summary") or "").strip()
        prose_html = f'<div class="walk-prose">{esc(summary)}</div>' if summary else ""
        edges = sorted(
            self.edges_of_concept.get(cid, []),
            key=lambda e: self.concepts[e["target"] if e["source"] == cid else e["source"]]["name"].lower(),
        )
        if edges:
            n = len(edges)
            word = "connection" if n == 1 else "connections"
            lines = "".join(f"<li>{self.connection_line(pk, e, cid)}</li>" for e in edges)
            return (
                f'<li class="walk-step"><details class="tree-node node-concept" data-depth="2">'
                f'<summary>{clink} <span class="tree-count">({n} {word})</span>{cite}</summary>'
                f'<ul class="tree-edges">{lines}</ul></details>{prose_html}</li>'
            )
        return f'<li class="walk-step tree-leaf">{clink}{cite}{prose_html}</li>'

    def _paper_concepts_panel(self, pid: str) -> str:
        """Body of the paper page's "The concepts" tab: the paper's concepts
        by role (introduced/refined/inherited, reading order, PDF deep links)
        with its overlay narrative."""
        pk = "story"
        by_role = self.concepts_of_paper.get(pid, {})
        if not any(by_role.values()):
            return ""
        parts = []
        narrative = self.paper_overlay_narrative.get(pid, "")
        if narrative:
            parts.append(
                f'<div class="node-narrative">{self.process_body(narrative, pk, "paper-overlay")}</div>')
        gran_buttons = "".join(
            f'<button type="button" class="gran-chip" data-gran="{g}" data-scope="paper-concepts">{label}</button>'
            for g, label in ((1, "roles"), (2, "concepts"), (3, "everything"))
        )
        parts.append(f'<p class="tree-controls"><span class="controls-label">Read at</span>{gran_buttons}</p>')
        parts.append('<div class="overlay-tree">')
        for role in self.ROLE_ORDER:
            cids = by_role.get(role, [])
            if not cids:
                continue
            n = len(cids)
            items = "".join(self._paper_concept_item(pid, cid, pk) for cid in cids)
            parts.append(
                f'<details class="tree-node node-rolegroup" data-depth="1">'
                f'<summary>{esc(self.ROLE_HEADS[role])} '
                f'<span class="tree-kind role-{role}">{role}</span> '
                f'<span class="tree-count">({n} concept{"s" if n != 1 else ""}, in reading order)</span></summary>'
                f'<ul class="tree-concepts">{items}</ul></details>'
            )
        parts.append('</div>')
        return "\n".join(parts)

    INDEX_TABS_JS = """
<script>
(function () {
  var tabs = Array.prototype.slice.call(document.querySelectorAll('.tabs [role="tab"]'));
  function activate(slug) {
    tabs.forEach(function (btn) {
      var on = btn.id === 'tabbtn-' + slug;
      btn.classList.toggle('active', on);
      btn.setAttribute('aria-selected', on ? 'true' : 'false');
      var panel = document.getElementById(btn.getAttribute('aria-controls'));
      if (panel) panel.hidden = !on;
    });
  }
  tabs.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var slug = btn.id.replace('tabbtn-', '');
      activate(slug);
      if (history.replaceState) history.replaceState(null, '', '#tab-' + slug);
    });
  });
  function activateFromHash() {
    if (location.hash.indexOf('#tab-') === 0) {
      var slug = location.hash.slice(5);
      if (document.getElementById('tabbtn-' + slug)) activate(slug);
    }
  }
  activateFromHash();
  window.addEventListener('hashchange', activateFromHash);
  var subtabs = Array.prototype.slice.call(document.querySelectorAll('.subtabs [role="tab"]'));
  function activateStory(sid) {
    subtabs.forEach(function (btn) {
      var on = btn.id === 'subtabbtn-' + sid;
      btn.classList.toggle('active', on);
      btn.setAttribute('aria-selected', on ? 'true' : 'false');
      var panel = document.getElementById(btn.getAttribute('aria-controls'));
      if (panel) panel.hidden = !on;
    });
  }
  subtabs.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var sid = btn.id.replace('subtabbtn-', '');
      activateStory(sid);
      if (history.replaceState) history.replaceState(null, '', '#' + sid);
    });
  });
  if (document.getElementById('subtabbtn-' + location.hash.slice(1))) {
    activateStory(location.hash.slice(1));
  }
  Array.prototype.forEach.call(document.querySelectorAll('[data-gran]'), function (btn) {
    btn.addEventListener('click', function () {
      var g = parseInt(btn.getAttribute('data-gran'), 10);
      var scope = btn.getAttribute('data-scope');
      if (!scope) return;
      Array.prototype.forEach.call(
        document.querySelectorAll('#' + scope + ' details[data-depth]'),
        function (d) { d.open = parseInt(d.getAttribute('data-depth'), 10) < g; }
      );
    });
  });
})();
</script>
<noscript><style>
  .tab-panel[hidden], .story-panel[hidden] { display: block; }
  .tabs, .subtabs, .tree-controls { display: none; }
  .panel-title { display: block; }
  .story-panel + .story-panel { margin-top: 2.5rem; border-top: 1px solid var(--stroke-strong); padding-top: 1.5rem; }
</style></noscript>"""

    def build_index_page(self) -> str:
        pk = "index"
        d = self.data

        parts = []
        parts.append('<h1 class="hero-title">Explore</h1>')
        parts.append('<p class="hero-tag">An AI safety wiki</p>')
        parts.append(
            "<p class=\"lede\">A quiet way to explore AI-safety research. "
            "Each paper is taken down to its bare-bones concepts, so you can see "
            "what it&rsquo;s really made of and follow how the ideas connect &mdash; "
            "within the paper itself, and out across the wider field. "
            "Every paper also comes with its own stories &mdash; several tellings "
            "of the same paper, told chapter by chapter.</p>"
        )
        parts.append(
            '<p class="section-note">First visit? <a href="help.html">How to use this '
            'wiki</a> &mdash; a short illustrated guide to the pieces and the controls.</p>'
        )
        tabs: list[tuple[str, str, str]] = [
            ("papers", "Papers", self._index_tab_papers()),
            ("superthemes", "Superthemes", self._index_tab_superthemes()),
            ("tissue", "Connective themes", self._index_tab_tissues()),
            ("concepts", "Concepts A–Z", self._index_tab_concepts()),
        ]

        buttons = []
        panels = []
        for i, (slug, label, body) in enumerate(tabs):
            active = ' active' if i == 0 else ''
            selected = 'true' if i == 0 else 'false'
            hidden = '' if i == 0 else ' hidden'
            buttons.append(
                f'<button type="button" class="tab{active}" id="tabbtn-{slug}" role="tab" '
                f'aria-selected="{selected}" aria-controls="tab-{slug}">{esc(label)}</button>'
            )
            panels.append(
                f'<section class="tab-panel" id="tab-{slug}" role="tabpanel" '
                f'aria-labelledby="tabbtn-{slug}"{hidden}>\n'
                f'<h2 class="panel-title">{esc(label)}</h2>\n{body}\n</section>'
            )

        parts.append('<nav class="tabs" role="tablist" aria-label="Index views">' + "".join(buttons) + "</nav>")
        parts.extend(panels)
        parts.append(self.INDEX_TABS_JS)

        return self.shell(pk, "Explore — an AI safety wiki", "\n".join(parts))

    # ---- help page ---------------------------------------------------------

    def _help_figure(self, filename: str, alt: str, caption: str) -> str:
        """A screenshot figure for the help page. Renders nothing if the
        source image is absent, so the build never emits a broken link."""
        if not (HELP_SHOTS_DIR / filename).is_file():
            return ""
        src = self.asset_href("help", f"help/{filename}")
        return (f'<figure class="help-figure"><img src="{src}" alt="{esc(alt)}" loading="lazy">'
                f'<figcaption>{caption}</figcaption></figure>')

    _SMALL_NUMBERS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
                      6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}

    def build_help_page(self) -> str:
        pk = "help"
        d = self.data
        paper_stories = d.get("paperStories") or []
        n_papers = self._SMALL_NUMBERS.get(len(d["papers"]), str(len(d["papers"])))
        n_concepts = len(d["concepts"])
        n_edges = len(d["edges"])
        n_themes = len(d["themes"])

        parts = []
        parts.append("<h1>How to use this wiki</h1>")
        parts.append(
            f'<p class="lede">Everything here is built from {n_papers} AI-safety papers, '
            f'taken apart into their bare-bones ideas and wired back together. '
            f'This page shows what the pieces are and how to move around them. '
            f'It reads top to bottom in a few minutes.</p>'
        )

        # -- the pieces ------------------------------------------------------
        parts.append('<section class="prose-section">')
        parts.append("<h2>What the pieces are</h2>")
        parts.append(
            f"<p>The wiki has a small vocabulary, and every page is one of these kinds "
            f"(the coloured badge in the top-right corner of a page tells you which one "
            f"you are reading):</p>"
        )
        parts.append(
            '<ul class="help-kinds">'
            f'<li><b>Concepts</b> &mdash; the atoms. Each of the {n_concepts} concept pages '
            f'explains one idea from one or more of the papers, in plain prose.</li>'
            f'<li><b>Edges</b> &mdash; the wiring. Each of the {n_edges} edge pages explains how '
            f'two concepts relate; a few are marked <i>hindsight</i>, meaning the link only '
            f'became visible after a later paper.</li>'
            f'<li><b>Themes</b> &mdash; small groups of concepts that belong together, each with '
            f'a guided walk through its members in reading order ({n_themes} of them).</li>'
            f'<li><b>Superthemes</b> &mdash; groups of themes; the largest structures in the wiki.</li>'
            f'<li><b>Connective themes</b> &mdash; lenses over the <i>edges</i> rather than the concepts: '
            f'short threads of related connections.</li>'
            f'<li><b>Stories</b> &mdash; each paper retold as a story: its own arc chapter '
            f'by chapter, its ties to the other papers, and its thesis and contributions '
            f'in its own terms.</li>'
            f'<li><b>Figures</b> &mdash; a paper&rsquo;s own figures and tables, each with '
            f'a page explaining how to read it and what it shows; the reader meets them '
            f'as supporting evidence inside the paper&rsquo;s <i>The experiments</i> '
            f'telling. (Rolling out paper by paper; not every paper has them yet.)</li>'
            '</ul>'
        )
        parts.append("</section>")

        # -- the front page ----------------------------------------------------
        parts.append('<section class="prose-section">')
        parts.append("<h2>The front page</h2>")
        parts.append(self._help_figure(
            "index-tabs.png",
            "The front page of the wiki, with its row of view tabs under the title",
            "The front page. Each tab is a different view of the same material.",
        ))
        tab_bullets = [
            '<li><b>Papers</b> &mdash; where the front page opens: a card per paper, '
            'each linking to the paper&rsquo;s own page &mdash; its stories, and every '
            'concept it uses in reading order. The best place to start reading.</li>'
        ]
        tab_bullets.append('<li><b>Superthemes</b> &mdash; the big structures, each listing its themes.</li>')
        tab_bullets.append('<li><b>Connective themes</b> &mdash; the threads of connections.</li>')
        tab_bullets.append('<li><b>Concepts A&ndash;Z</b> &mdash; every concept, alphabetically. '
                           'Use it when you already know what you are looking for.</li>')
        parts.append(f'<ul>{"".join(tab_bullets)}</ul>')
        parts.append(
            '<p>The address bar follows the tab you are on (<code>#tab-concepts</code>, '
            '<code>#tab-superthemes</code>, &hellip;), so you can bookmark or share a '
            'particular view.</p>'
        )
        parts.append("</section>")

        # -- reading a story ---------------------------------------------------
        if paper_stories:
            parts.append('<section class="prose-section">')
            parts.append("<h2>Reading a paper as stories</h2>")
            parts.append(
                "<p>Every paper has a page of its own &mdash; open it from its card "
                "in the Papers tab. A row of tabs at the top picks the telling: "
                "<b>The big picture</b> states the paper&rsquo;s own thesis and "
                "contributions in its own terms, <b>Inside the paper</b> follows "
                "the paper&rsquo;s own arc, and <b>Across the corpus</b> traces how "
                "it connects to the other papers. They all cover the same paper &mdash; "
                "choose whichever question interests you most.</p>"
            )
            parts.append(self._help_figure(
                "story-controls.png",
                "The story sub-tabs with the row of 'Read at' granularity buttons below them",
                "Pick a telling, then pick a zoom. &ldquo;Read at&rdquo; opens the whole story "
                "to one depth: <i>root claim</i> is a single sentence, <i>everything</i> is the "
                "full tree.",
            ))
            parts.append(
                "<p>Each story is a collapsible tree. The <b>Read at</b> buttons set how "
                "deep it opens &mdash; from the root claim alone down to every concept and "
                "its connections. You can also open and close any single branch by hand "
                "with the +/&minus; markers.</p>"
            )
            parts.append(
                "<p>A last tab, <b>The concepts</b>, holds the paper&rsquo;s full "
                "inventory &mdash; what it introduced, refined, and inherited, in "
                "reading order, each deep-linked into the PDF &mdash; with a "
                "<b>Read at</b> zoom of its own.</p>"
            )
            if self.figures:
                parts.append(
                    "<p>Where a paper&rsquo;s figures have been processed, one more "
                    "telling joins the row: <b>The experiments</b> explains the "
                    "paper&rsquo;s experiments and results chapter by chapter, "
                    "each experiment set up by the one before it. Its nodes are "
                    "the concepts doing the work in each experiment, and the "
                    "paper&rsquo;s figures and tables sit beside the claims they "
                    "support, as evidence. Each figure opens into a page of its "
                    "own, which explains how to read the visualization before "
                    "stating what the paper concludes.</p>"
                )
            parts.append(self._help_figure(
                "story-tree.png",
                "A story tree with chapters partially expanded, showing the +/− toggles",
                "A story opened to chapter level. Click a marker to open one branch; "
                "the prose at each level explains what the level below contains.",
            ))
            parts.append("</section>")

        # -- concept pages -----------------------------------------------------
        parts.append('<section class="prose-section">')
        parts.append("<h2>Concept pages</h2>")
        parts.append(self._help_figure(
            "concept-page.png",
            "The top of a concept page: title, origin line, summary, and introduction",
            "The top of a concept page: which papers it comes from, a one-line summary, "
            "then a gentle introduction before the detail.",
        ))
        parts.append(
            "<p>Every concept page follows the same shape. Prose first; then, after the "
            "divider, its place in the graph: <b>Part of / Contains</b> (parent and child "
            "concepts), <b>Connections</b> (its edges, each one sentence), <b>Lenses</b> "
            "(the themes it belongs to), and <b>Sources</b>. Highlighted phrases in the "
            "prose are links to other pages.</p>"
        )
        parts.append("</section>")

        # -- popups --------------------------------------------------------------
        parts.append('<section class="prose-section">')
        parts.append("<h2>Links open in a popup</h2>")
        parts.append(self._help_figure(
            "popup.png",
            "A concept page open in a popup dialog over the index",
            "Following a link opens the page in a popup, so you never lose your place.",
        ))
        parts.append(
            "<p>Clicking any concept, edge, or theme link opens the page in a popup over "
            "where you are, so a quick side-glance never costs you your place. Close it "
            "with the <b>&times;</b>, the <b>Esc</b> key, or a click outside; "
            "<b>open as full page&nbsp;&#8599;</b> in its top bar promotes the popup to a "
            "real visit. To skip the popup entirely, open the link in a new tab as usual "
            "(ctrl-click, cmd-click, or middle-click).</p>"
        )
        parts.append("</section>")

        # -- sources ---------------------------------------------------------------
        parts.append('<section class="prose-section">')
        parts.append("<h2>Sources go straight into the papers</h2>")
        parts.append(self._help_figure(
            "sources.png",
            "A Sources block listing section and page citations grouped by paper",
            "Every page ends with its sources: each entry opens the paper&rsquo;s PDF "
            "at that page.",
        ))
        parts.append(
            "<p>Nothing here is invented: every page cites the passages it is built from. "
            "The PDFs ship with the wiki, and both the <b>Sources</b> lists and the inline "
            "citations in the prose (the <i>&sect;&hellip;, p.&nbsp;N</i> parts) open the "
            "right paper at the right page, in a new tab.</p>"
        )
        parts.append("</section>")

        # -- small print -------------------------------------------------------------
        parts.append('<section class="prose-section">')
        parts.append("<h2>Small print</h2>")
        parts.append(
            '<ul>'
            '<li>The wiki is fully self-contained &mdash; pages, papers, fonts, and math '
            'all work offline.</li>'
            '<li>Without JavaScript everything still reads: tabs and trees simply stack '
            'as one long page, and links navigate normally instead of opening popups.</li>'
            '<li>Lost? The <b>Explore</b> mark in the header always returns to the front page.</li>'
            '</ul>'
        )
        parts.append("</section>")

        return self.shell(pk, "How to use this wiki — Explore", "\n".join(parts))

    # ---- top-level build --------------------------------------------------

    def build_all(self) -> dict[str, int]:
        counts = {}

        for kind, (coll_key, dirname, _label) in KIND_INFO.items():
            out_dir = SITE_DIR / dirname
            out_dir.mkdir(parents=True, exist_ok=True)
            items = self.data.get(coll_key) or []
            builder = {
                "concept": self.build_concept_page,
                "edge": self.build_edge_page,
                "theme": self.build_theme_page,
                "supertheme": self.build_supertheme_page,
                "superedge": self.build_superedge_page,
                "tissue": self.build_tissue_page,
                "story": self.build_paper_story_page,
            }[kind]
            n = 0
            for item in items:
                html_doc = builder(item)
                (out_dir / f"{item['id']}.html").write_text(html_doc, encoding="utf-8")
                n += 1
            counts[kind] = n

        fig_dir = SITE_DIR / KIND_DIR["figure"]
        fig_dir.mkdir(parents=True, exist_ok=True)
        n = 0
        for pid, entry in self.figures.items():
            items = entry.get("items") or []
            for item in items:
                html_doc = self.build_figure_page(pid, item, items)
                (fig_dir / f"{pid}--{item['id']}.html").write_text(html_doc, encoding="utf-8")
                n += 1
        counts["figure"] = n

        (SITE_DIR / "index.html").write_text(self.build_index_page(), encoding="utf-8")
        counts["index"] = 1

        (SITE_DIR / "help.html").write_text(self.build_help_page(), encoding="utf-8")
        counts["help"] = 1

        return counts


# --------------------------------------------------------------------------
# CSS
# --------------------------------------------------------------------------

CSS = """
/* ==========================================================================
   Explore — an AI safety wiki · "aurora glass"
   Frosted panels floating over a slow ambient aurora field.
   Display/UI and prose: Source Serif 4 · Math: KaTeX
   ========================================================================== */

@font-face {
  font-family: "Source Serif 4";
  src: url("typefaces/source-serif-4-latin-wght-normal.woff2") format("woff2-variations");
  font-weight: 200 900;
  font-style: normal;
  font-display: swap;
}

/* ---- tokens ---------------------------------------------------------- */

:root {
  color-scheme: light dark;
  --sans: "Source Serif 4", Georgia, "Iowan Old Style", serif;
  --serif: "Source Serif 4", Georgia, "Iowan Old Style", serif;
  --mono: ui-monospace, "Cascadia Code", Consolas, monospace;

  --bg0: #eef1fa;
  --fg: #1a2036;
  --muted: #545f80;
  --faint: #7f88a8;
  --stroke: rgba(26, 32, 62, 0.10);
  --stroke-strong: rgba(26, 32, 62, 0.20);
  --panel: rgba(255, 255, 255, 0.58);
  --card: rgba(255, 255, 255, 0.52);
  --chip: rgba(255, 255, 255, 0.5);
  --hover: rgba(26, 32, 62, 0.05);
  --header-bg: rgba(243, 245, 252, 0.6);
  --link: #0b63a5;
  --link-visited: #6d28d9;
  --acc-a: #0891b2;
  --acc-b: #6366f1;
  --acc-c: #c026d3;
  --hero-grad: linear-gradient(95deg, #312e81, #0e7490 55%, #a21caf);
  --panel-shadow: 0 18px 50px rgba(60, 70, 130, 0.16), inset 0 1px 0 rgba(255, 255, 255, 0.75);
  --card-shadow: 0 2px 10px rgba(60, 70, 130, 0.06);
  --dialog-bg: rgba(250, 251, 255, 0.82);
  --noise-opacity: 0.25;
  --k-concept: #b45309;
  --k-edge: #047857;
  --k-theme: #4f46e5;
  --k-supertheme: #a21caf;
  --k-superedge: #4d7c0f;
  --k-tissue: #0e7490;
  --k-story: #be123c;
  --k-figure: #0f766e;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg0: #0a0d1c;
    --fg: #e9ecf8;
    --muted: #9aa3c0;
    --faint: #6e779a;
    --stroke: rgba(255, 255, 255, 0.08);
    --stroke-strong: rgba(255, 255, 255, 0.17);
    --panel: rgba(20, 25, 48, 0.52);
    --card: rgba(255, 255, 255, 0.04);
    --chip: rgba(255, 255, 255, 0.055);
    --hover: rgba(255, 255, 255, 0.055);
    --header-bg: rgba(10, 13, 28, 0.55);
    --link: #8fd7fc;
    --link-visited: #c4b5fd;
    --acc-a: #67e8f9;
    --acc-b: #8b95f8;
    --acc-c: #f0abfc;
    --hero-grad: linear-gradient(95deg, #eaf6ff, #8fe8ff 35%, #a8b3ff 65%, #f2b8ff);
    --panel-shadow: 0 24px 70px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.07);
    --card-shadow: 0 2px 12px rgba(0, 0, 0, 0.18);
    --dialog-bg: rgba(15, 19, 40, 0.85);
    --noise-opacity: 0.35;
    --k-concept: #fbbf24;
    --k-edge: #34d399;
    --k-theme: #8b95f8;
    --k-supertheme: #e879f9;
    --k-superedge: #bccf5a;
    --k-tissue: #67e8f9;
    --k-story: #fb7185;
    --k-figure: #5eead4;
  }
}

/* ---- base ------------------------------------------------------------ */

* { box-sizing: border-box; }

html {
  -webkit-text-size-adjust: 100%;
  background: var(--bg0);
  scrollbar-width: thin;
  scrollbar-color: var(--stroke-strong) transparent;
}

body {
  margin: 0;
  color: var(--fg);
  font-family: var(--serif);
  font-weight: 450;
  font-size: 1.15rem;
  line-height: 1.72;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
}

/* ambient aurora field */
body::before {
  content: "";
  position: fixed;
  inset: -25%;
  z-index: -2;
  pointer-events: none;
  background:
    radial-gradient(38% 45% at 18% 12%, rgba(99, 102, 241, 0.20), transparent 65%),
    radial-gradient(42% 48% at 85% 18%, rgba(8, 145, 178, 0.14), transparent 68%),
    radial-gradient(50% 55% at 72% 90%, rgba(192, 38, 211, 0.11), transparent 70%),
    radial-gradient(36% 42% at 6% 82%, rgba(56, 189, 248, 0.15), transparent 65%);
}
@media (prefers-color-scheme: dark) {
  body::before {
    background:
      radial-gradient(38% 45% at 18% 12%, rgba(109, 92, 255, 0.30), transparent 65%),
      radial-gradient(42% 48% at 85% 18%, rgba(45, 212, 191, 0.17), transparent 68%),
      radial-gradient(50% 55% at 72% 90%, rgba(232, 121, 249, 0.14), transparent 70%),
      radial-gradient(36% 42% at 6% 82%, rgba(56, 189, 248, 0.16), transparent 65%);
  }
}

/* film grain so the glass never bands */
body::after {
  content: "";
  position: fixed;
  inset: 0;
  z-index: -1;
  pointer-events: none;
  opacity: calc(var(--noise-opacity) * 0.1);
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}

@media (prefers-reduced-motion: no-preference) {
  body::before {
    animation: aurora-drift 90s ease-in-out infinite alternate;
  }
  @keyframes aurora-drift {
    from { transform: translate3d(-1.5%, -1%, 0) rotate(0deg) scale(1); }
    to   { transform: translate3d(1.5%, 2%, 0) rotate(3deg) scale(1.07); }
  }
  main { animation: rise 0.45s cubic-bezier(0.2, 0.7, 0.3, 1) both; }
  @keyframes rise {
    from { opacity: 0; transform: translateY(10px); }
  }
}

::selection { background: rgba(139, 149, 248, 0.35); }

:focus-visible {
  outline: 2px solid var(--acc-a);
  outline-offset: 2px;
  border-radius: 4px;
}

::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: var(--stroke-strong);
  border-radius: 8px;
  border: 2px solid transparent;
  background-clip: content-box;
}

/* ---- frame: header / panel / footer ----------------------------------- */

.site-header {
  position: sticky;
  top: 0;
  z-index: 40;
  background: var(--header-bg);
  -webkit-backdrop-filter: blur(18px) saturate(1.4);
  backdrop-filter: blur(18px) saturate(1.4);
  border-bottom: 1px solid var(--stroke);
}

.header-inner {
  width: min(1060px, 100% - 1.4rem);
  margin: 0 auto;
  padding: 0.62rem 0.15rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  font-family: var(--sans);
  font-size: 0.88rem;
}

.home-link {
  color: var(--muted);
  text-decoration: none;
  font-weight: 600;
  letter-spacing: 0.015em;
  display: inline-flex;
  align-items: baseline;
  gap: 0.5rem;
}
.home-link b {
  color: var(--fg);
  font-weight: 700;
  letter-spacing: -0.01em;
}
.home-sub {
  color: var(--faint);
  font-weight: 500;
  font-size: 0.82em;
}
.home-link:hover b { color: var(--acc-a); }
@media (max-width: 560px) { .home-sub { display: none; } }

.header-tools {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
}
.help-link {
  color: var(--muted);
  text-decoration: none;
  font-weight: 600;
  font-size: 0.78rem;
  letter-spacing: 0.02em;
  padding: 0.2rem 0.66rem;
  border: 1px solid var(--stroke-strong);
  border-radius: 999px;
}
.help-link:hover { color: var(--acc-a); border-color: var(--acc-a); }
.help-link[aria-current="page"] { color: var(--fg); border-color: var(--stroke-strong); }

/* ---- help page ----------------------------------------------------------- */

.help-figure {
  margin: 1.15rem 0 1.5rem;
}
.help-figure img {
  display: block;
  width: 100%;
  height: auto;
  border: 1px solid var(--stroke-strong);
  border-radius: 14px;
  box-shadow: var(--card-shadow);
}
.help-figure figcaption {
  font-family: var(--sans);
  font-size: 0.84rem;
  line-height: 1.5;
  color: var(--muted);
  margin-top: 0.55rem;
}
.help-kinds li { margin: 0.45rem 0; }

.page {
  width: min(1060px, 100% - 1.4rem);
  margin: 1.15rem auto 2.8rem;
  padding: clamp(1.5rem, 4vw, 2.6rem) clamp(1.15rem, 4.5vw, 2.6rem) clamp(1.5rem, 4vw, 2.3rem);
  background: var(--panel);
  -webkit-backdrop-filter: blur(22px) saturate(1.4);
  backdrop-filter: blur(22px) saturate(1.4);
  border: 1px solid var(--stroke);
  border-radius: 22px;
  box-shadow: var(--panel-shadow);
}

.site-footer {
  margin-top: 2.8rem;
  padding-top: 1.1rem;
  border-top: 1px solid var(--stroke);
  font-family: var(--sans);
  font-size: 0.84rem;
}
.site-footer a { color: var(--muted); text-decoration: none; }
.site-footer a:hover { color: var(--fg); }

/* ---- typography -------------------------------------------------------- */

h1, h2, h3 {
  font-family: var(--sans);
  line-height: 1.22;
  font-weight: 600;
}

h1 {
  font-size: clamp(1.5rem, 1.2rem + 1.4vw, 2rem);
  letter-spacing: -0.022em;
  margin: 0 0 0.8rem;
  text-wrap: balance;
}
main > h1:first-child::before {
  content: "";
  display: block;
  width: 44px;
  height: 3px;
  border-radius: 3px;
  background: linear-gradient(90deg, var(--acc-a), var(--acc-c));
  margin-bottom: 1rem;
}

.pk-index main > h1.hero-title {
  font-size: clamp(2.6rem, 1.5rem + 5vw, 4.4rem);
  font-weight: 680;
  letter-spacing: -0.03em;
  line-height: 1.02;
  margin-bottom: 0.15rem;
  background: var(--hero-grad);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.hero-tag {
  font-family: var(--sans);
  font-size: clamp(0.92rem, 0.85rem + 0.4vw, 1.08rem);
  font-weight: 500;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--muted);
  margin: 0 0 1.4rem;
}

h2 {
  font-size: 0.74rem;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--muted);
  margin: 1.7rem 0 0.6rem;
}

.prose-section h2 {
  font-size: 1.16rem;
  text-transform: none;
  letter-spacing: -0.012em;
  color: var(--fg);
  margin: 1.9rem 0 0.55rem;
}

h3.letter-head {
  font-size: 0.92rem;
  font-weight: 700;
  color: var(--acc-b);
  margin: 1.3rem 0 0.35rem;
  border-bottom: 1px solid var(--stroke);
  padding-bottom: 0.2rem;
}

p { margin: 0 0 2rem; }

.lede {
  font-size: 1.22rem;
  line-height: 1.55;
  font-weight: 420;
  margin-bottom: 1.1rem;
}

/* gentle two-paragraph page introduction — plain prose, part of the page flow */
.page-intro { margin: 0 0 1.6rem; }

.origins, .edge-meta {
  font-family: var(--sans);
  font-size: 0.84rem;
  color: var(--muted);
  margin-bottom: 1.2rem;
}

blockquote {
  margin: 1.1rem 0;
  padding: 0.15rem 0 0.15rem 1rem;
  border-left: 2px solid;
  border-image: linear-gradient(180deg, var(--acc-a), var(--acc-c)) 1;
  color: var(--muted);
  font-style: italic;
}

code {
  font-family: var(--mono);
  font-size: 0.88em;
  background: var(--chip);
  border: 1px solid var(--stroke);
  border-radius: 6px;
  padding: 0.06em 0.35em;
}

/* ---- links ------------------------------------------------------------- */

a {
  color: var(--link);
  text-decoration: underline;
  text-decoration-color: transparent;
  text-decoration-thickness: 1px;
  text-underline-offset: 3px;
  transition: text-decoration-color 0.15s ease, color 0.15s ease;
}
a:hover { text-decoration-color: currentColor; }
a:visited { color: var(--link-visited); }

a.cite {
  color: var(--muted);
  font-size: 0.92em;
  text-decoration-style: dotted;
  text-decoration-color: var(--stroke-strong);
}
a.cite:hover { color: var(--fg); text-decoration-color: currentColor; }

.linklike {
  background: none;
  border: none;
  padding: 0;
  font: inherit;
  color: var(--link);
  cursor: pointer;
}
.linklike:hover { text-decoration: underline; }

/* ---- chips, badges, tags ------------------------------------------------ */

.kind-concept    { --k: var(--k-concept); }
.kind-edge       { --k: var(--k-edge); }
.kind-theme      { --k: var(--k-theme); }
.kind-supertheme { --k: var(--k-supertheme); }
.kind-superedge  { --k: var(--k-superedge); }
.kind-tissue     { --k: var(--k-tissue); }
.kind-story      { --k: var(--k-story); }
.kind-figure     { --k: var(--k-figure); }
.role-introduced { --k: var(--k-concept); }
.role-refined    { --k: var(--k-theme); }
.role-inherited  { --k: var(--muted); }

.kind-badge {
  display: inline-block;
  font-family: var(--sans);
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 0.22rem 0.62rem;
  border-radius: 999px;
  color: var(--k, var(--muted));
  border: 1px solid color-mix(in srgb, var(--k, var(--muted)) 40%, transparent);
  background: color-mix(in srgb, var(--k, var(--muted)) 10%, transparent);
  white-space: nowrap;
}

.tag {
  display: inline-block;
  font-family: var(--sans);
  font-size: 0.66rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
  vertical-align: middle;
}
.tag.hindsight {
  color: var(--k-concept);
  border: 1px solid color-mix(in srgb, var(--k-concept) 45%, transparent);
  background: color-mix(in srgb, var(--k-concept) 10%, transparent);
}

.role { font-weight: 600; color: var(--k, var(--muted)); }

.era-tag {
  display: inline-block;
  font-family: var(--sans);
  font-size: 0.66rem;
  font-weight: 500;
  border: 1px solid var(--stroke);
  background: var(--chip);
  border-radius: 999px;
  padding: 0.08rem 0.5rem;
  color: var(--muted);
  margin-left: 0.45rem;
  vertical-align: middle;
  white-space: nowrap;
}

.muted { color: var(--muted); font-size: 0.85em; }

/* ---- content blocks ------------------------------------------------------ */

.prose-section { margin-bottom: 1.5rem; }

.divider {
  border: none;
  height: 1px;
  margin: 2.2rem 0 1.4rem;
  background: linear-gradient(90deg, transparent, var(--stroke-strong), transparent);
}

.nav-block {
  margin: 0 0 0.9rem;
  padding: 1.05rem 1.3rem 1.1rem;
  background: var(--card);
  border: 1px solid var(--stroke);
  border-radius: 16px;
  box-shadow: var(--card-shadow);
}
.nav-block > h2 {
  margin: 0 0 0.55rem;
  display: flex;
  align-items: center;
  gap: 0.55rem;
}
.nav-block > h2::before {
  content: "";
  width: 14px;
  height: 2px;
  border-radius: 2px;
  background: linear-gradient(90deg, var(--acc-a), var(--acc-c));
}
.nav-block ul { padding-left: 1.2rem; margin: 0.3rem 0; }
.nav-block li { margin: 0.3rem 0; }

.connections { list-style: none; padding-left: 0; }
.nav-block ul.connections { padding-left: 0; }
.connections li {
  padding: 0.38rem 0.1rem;
  border-bottom: 1px solid var(--stroke);
}
.connections li:last-child { border-bottom: none; }

.section-note {
  font-family: var(--sans);
  font-size: 0.85rem;
  color: var(--muted);
}

/* sources */
.sources {
  list-style: none;
  padding-left: 0;
  font-family: var(--sans);
  font-size: 0.85rem;
  margin: 0.3rem 0;
}
.nav-block ul.sources { padding-left: 0; }
.source-paper { margin: 0.5rem 0; }
.source-locs {
  padding-left: 1.2rem;
  margin: 0.2rem 0;
  color: var(--muted);
}
.source-locs li { margin: 0.18rem 0; }

.sources-details > summary {
  cursor: pointer;
  font-family: var(--sans);
  font-size: 0.85rem;
  color: var(--muted);
}
.sources-details > summary:hover { color: var(--fg); }
.sources-details[open] > summary { margin-bottom: 0.3rem; }

.supertheme-list { list-style: none; padding-left: 0; }
.supertheme-list > li { margin-bottom: 0.95rem; }
.theme-sublist { padding-left: 1.3rem; margin-top: 0.3rem; }

.concept-az {
  columns: 2;
  column-gap: 2.2rem;
  padding-left: 1.1rem;
  list-style: disc;
}
.concept-az li::marker { color: var(--faint); }

/* ---- index tabs ----------------------------------------------------------- */

.tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 5px;
  width: fit-content;
  max-width: 100%;
  background: var(--chip);
  border: 1px solid var(--stroke);
  border-radius: 16px;
  box-shadow: var(--card-shadow);
  margin: 1.5rem 0 1.4rem;
  font-family: var(--sans);
}
.tab {
  background: none;
  border: none;
  border-radius: 11px;
  padding: 0.48rem 0.9rem;
  font-family: var(--sans);
  font-size: 0.87rem;
  font-weight: 500;
  color: var(--muted);
  cursor: pointer;
  transition: color 0.15s ease, background 0.15s ease;
}
.tab:hover { color: var(--fg); background: var(--hover); }
.tab.active {
  color: var(--fg);
  font-weight: 600;
  background: var(--panel);
  box-shadow: inset 0 0 0 1px var(--stroke-strong), 0 2px 8px rgba(0, 0, 0, 0.12);
}
.panel-title { display: none; }

/* ---- story sub-tabs (lenses over the same corpus) ---------------------- */

.subtabs {
  display: flex;
  flex-wrap: wrap;
  gap: 3px;
  margin: 0.4rem 0 1.3rem;
  padding-bottom: 0.55rem;
  border-bottom: 1px solid var(--stroke);
  font-family: var(--sans);
}
.subtab {
  background: none;
  border: 1px solid transparent;
  border-radius: 10px;
  padding: 0.38rem 0.8rem;
  font-family: var(--sans);
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--muted);
  cursor: pointer;
  transition: color 0.15s ease, background 0.15s ease, border-color 0.15s ease;
}
.subtab:hover { color: var(--fg); background: var(--hover); }
.subtab.active {
  color: var(--fg);
  font-weight: 600;
  background: var(--chip);
  border-color: var(--stroke-strong);
}
.story-panel[hidden] { display: none; }

/* ---- overlay story tree ------------------------------------------------ */

.tree-controls {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.4rem;
  margin: 0.9rem 0 1.2rem;
  font-family: var(--sans);
}
.controls-label {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.13em;
  color: var(--faint);
  margin-right: 0.25rem;
}
.gran-chip {
  font-family: var(--sans);
  font-size: 0.78rem;
  font-weight: 500;
  color: var(--muted);
  background: var(--chip);
  border: 1px solid var(--stroke);
  border-radius: 999px;
  padding: 0.3rem 0.75rem;
  cursor: pointer;
  transition: color 0.15s ease, border-color 0.15s ease, background 0.15s ease;
}
.gran-chip:hover {
  color: var(--fg);
  border-color: var(--stroke-strong);
  background: var(--hover);
}

.tree-node > summary {
  cursor: pointer;
  list-style: none;
  padding: 0.3rem 0.45rem;
  margin-inline: -0.45rem;
  border-radius: 9px;
  line-height: 1.5;
  transition: background 0.15s ease;
}
.tree-node > summary:hover { background: var(--hover); }
.tree-node > summary::-webkit-details-marker { display: none; }
.tree-node > summary::before {
  content: "+";
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.25rem;
  height: 1.25rem;
  margin-right: 0.55rem;
  border-radius: 7px;
  background: var(--chip);
  border: 1px solid var(--stroke);
  color: var(--acc-a);
  font-family: var(--sans);
  font-size: 0.85rem;
  font-weight: 600;
  vertical-align: -0.22em;
  transition: border-color 0.15s ease;
}
.tree-node > summary:hover::before {
  border-color: color-mix(in srgb, var(--acc-a) 55%, transparent);
}
.tree-node[open] > summary::before { content: "−"; }

.node-body {
  margin: 0.15rem 0 0.8rem 0.6rem;
  padding-left: 1.05rem;
  border-left: 1px solid var(--stroke-strong);
}

.node-root > summary {
  font-family: var(--sans);
  font-size: 1.13rem;
  font-weight: 650;
  line-height: 1.35;
}
.node-arc > summary { font-family: var(--sans); font-size: 1rem; font-weight: 650; }
.node-supertheme > summary { font-family: var(--sans); font-weight: 600; }
.node-theme > summary { font-family: var(--sans); font-size: 0.95rem; }
.node-superedges > summary { font-family: var(--sans); font-size: 0.88rem; color: var(--muted); }
.node-rolegroup > summary { font-family: var(--sans); font-size: 0.95rem; font-weight: 600; }

/* ---- papers tab cards --------------------------------------------------- */

.paper-cards {
  display: grid;
  gap: 0.9rem;
  margin: 0.4rem 0 1.3rem;
}
.paper-card {
  padding: 0.95rem 1.15rem 1rem;
  background: var(--card);
  border: 1px solid var(--stroke);
  border-radius: 16px;
  box-shadow: var(--card-shadow);
}
.paper-card .pc-title {
  margin: 0 0 0.25rem;
  font-family: var(--sans);
  font-size: 1.05rem;
  font-weight: 650;
  line-height: 1.35;
}
.paper-card .pc-title a { color: var(--fg); text-decoration: none; }
.paper-card .pc-title a:hover { color: var(--link); }
.paper-card .edge-meta { margin: 0; }

.arc-num {
  color: var(--acc-a);
  margin-right: 0.55rem;
  font-size: 0.7rem;
  font-weight: 650;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.node-narrative p { margin: 0.4rem 0 0.85rem; }

.tree-count {
  font-family: var(--sans);
  font-size: 0.76em;
  font-weight: 400;
  color: var(--faint);
  font-variant-numeric: tabular-nums;
}
.tree-kind {
  font-family: var(--sans);
  font-size: 0.62rem;
  font-weight: 650;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-left: 0.4rem;
  color: var(--k, var(--muted));
}

.tree-concepts {
  list-style: none;
  padding-left: 0;
  margin: 0.3rem 0;
}
.tree-concepts > li { margin: 0.15rem 0; }
.tree-leaf { padding-left: 1.85rem; }

.tree-edges {
  list-style: none;
  padding-left: 1.85rem;
  margin: 0.2rem 0 0.55rem;
  font-size: 0.93rem;
}
.tree-edges li { margin: 0.26rem 0; }

.walk-step { margin-bottom: 0.35rem; }
.walk-prose {
  margin: 0.05rem 0 0.75rem 1.85rem;
  font-size: 0.96rem;
}
.walk-prose p { margin: 0 0 0.45rem; }

ol.walk { padding-left: 1.5rem; }
ol.walk > li { margin: 0.6rem 0; }
ol.walk > li::marker {
  font-family: var(--sans);
  font-size: 0.85em;
  font-weight: 600;
  color: var(--acc-b);
}
ol.walk .walk-prose { margin-left: 0; }

/* ---- figure pages and the paper-page figure tours ----------------------- */

.figure-plate {
  margin: 0.4rem 0 1.6rem;
}
.figure-plate img {
  display: block;
  width: 100%;
  height: auto;
  background: #fff;
  border: 1px solid var(--stroke-strong);
  border-radius: 14px;
  box-shadow: var(--card-shadow);
  padding: 0.6rem;
  box-sizing: border-box;
}

.fig-entry {
  display: grid;
  grid-template-columns: 180px 1fr;
  gap: 1rem;
  align-items: start;
  padding: 0.4rem 0.1rem 0.2rem;
}
.fig-title {
  font-family: var(--sans);
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0 0 0.3rem;
}
.fig-note {
  font-size: 0.98rem;
  line-height: 1.55;
  color: var(--muted);
}
.fig-note p { margin: 0 0 0.4rem; }
.fig-note p:last-child { margin-bottom: 0; }
.fig-thumb img {
  display: block;
  width: 100%;
  max-height: 140px;
  object-fit: contain;
  background: #fff;
  border: 1px solid var(--stroke-strong);
  border-radius: 10px;
  padding: 0.3rem;
  box-sizing: border-box;
}

@media (max-width: 640px) {
  .fig-entry { grid-template-columns: 1fr; }
  .fig-thumb img { max-height: 180px; }
}

/* ---- popup dialog --------------------------------------------------------- */

.popup-dialog {
  padding: 0;
  border: 1px solid var(--stroke-strong);
  border-radius: 18px;
  background: var(--dialog-bg);
  -webkit-backdrop-filter: blur(28px) saturate(1.4);
  backdrop-filter: blur(28px) saturate(1.4);
  color: var(--fg);
  width: min(86ch, 94vw);
  height: min(85vh, 60rem);
  max-width: 94vw;
  max-height: 85vh;
  box-shadow: 0 32px 90px rgba(0, 0, 0, 0.5);
  overflow: hidden;
}
.popup-dialog[open] {
  display: flex;
  flex-direction: column;
}
.popup-dialog::backdrop {
  background: rgba(5, 7, 16, 0.45);
  -webkit-backdrop-filter: blur(6px);
  backdrop-filter: blur(6px);
}

.popup-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.45rem 0.55rem 0.45rem 1rem;
  border-bottom: 1px solid var(--stroke);
  font-family: var(--sans);
  font-size: 0.82rem;
  flex: none;
}
.popup-full { color: var(--muted); text-decoration: none; }
.popup-full:hover { color: var(--fg); }
.popup-close {
  background: none;
  border: none;
  padding: 0 0.55rem;
  font-family: var(--sans);
  font-size: 1.35rem;
  line-height: 1;
  color: var(--muted);
  cursor: pointer;
  border-radius: 8px;
}
.popup-close:hover { color: var(--fg); background: var(--hover); }

.popup-frame {
  border: none;
  width: 100%;
  flex: 1;
  background: var(--bg0);
}

/* page rendered inside a popup frame: hide the site chrome */
.in-popup .site-header,
.in-popup .site-footer { display: none; }
.in-popup .page {
  margin: 0.9rem auto 1.4rem;
  width: min(1060px, 100% - 1.1rem);
}

/* ---- math / misc ------------------------------------------------------- */

.katex-display { overflow-x: auto; overflow-y: hidden; padding: 0.2rem 0; }

/* ---- responsive -------------------------------------------------------- */

@media (max-width: 640px) {
  body { font-size: 1.08rem; }
  .concept-az { columns: 1; }
  .page { border-radius: 16px; margin-top: 0.8rem; }
  .node-body { margin-left: 0.45rem; padding-left: 0.75rem; }
  .tree-leaf, .walk-prose { padding-left: 1.4rem; }
  .walk-prose { margin-left: 1.4rem; padding-left: 0; }
  .tree-edges { padding-left: 1.4rem; }
}
"""

# --------------------------------------------------------------------------
# Popup script: concept / theme / tissue pages open in a modal dialog
# --------------------------------------------------------------------------

POPUP_JS = r"""
(function () {
  'use strict';
  var POPUP_KINDS = /\/(concept|edge|theme|supertheme|superedge|tissue|figure)\/[^\/]+\.html$/;

  function popupTarget(ev) {
    if (ev.defaultPrevented || ev.button !== 0 ||
        ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey) return null;
    var a = ev.target.closest ? ev.target.closest('a[href]') : null;
    if (!a || a.target === '_blank') return null;
    var url;
    try { url = new URL(a.getAttribute('href'), window.location.href); }
    catch (e) { return null; }
    if (url.origin !== window.location.origin) return null;
    return url;
  }

  if (window.self !== window.top) {
    // Inside the popup frame: hide the page chrome, keep concept/theme/tissue
    // links inside the frame, break every other link out to the full window.
    document.documentElement.classList.add('in-popup');
    document.addEventListener('click', function (ev) {
      var url = popupTarget(ev);
      if (!url) return;
      if (!POPUP_KINDS.test(url.pathname)) {
        ev.preventDefault();
        window.top.location.href = url.href;
      }
    });
    return;
  }

  var dialog = null, frame = null, fullLink = null;

  function ensureDialog() {
    if (dialog) return dialog;
    dialog = document.createElement('dialog');
    dialog.className = 'popup-dialog';

    var bar = document.createElement('div');
    bar.className = 'popup-bar';

    fullLink = document.createElement('a');
    fullLink.className = 'popup-full';
    fullLink.textContent = 'open as full page ↗';
    bar.appendChild(fullLink);

    var closeBtn = document.createElement('button');
    closeBtn.type = 'button';
    closeBtn.className = 'popup-close';
    closeBtn.setAttribute('aria-label', 'Close');
    closeBtn.textContent = '×';
    closeBtn.addEventListener('click', function () { dialog.close(); });
    bar.appendChild(closeBtn);

    frame = document.createElement('iframe');
    frame.className = 'popup-frame';
    frame.setAttribute('title', 'Wiki page');
    frame.addEventListener('load', function () {
      try { fullLink.href = frame.contentWindow.location.href; } catch (e) {}
    });

    dialog.appendChild(bar);
    dialog.appendChild(frame);
    // click on the backdrop (the dialog element itself) closes
    dialog.addEventListener('click', function (ev) {
      if (ev.target === dialog) dialog.close();
    });
    dialog.addEventListener('close', function () {
      frame.src = 'about:blank';
    });
    document.body.appendChild(dialog);
    return dialog;
  }

  document.addEventListener('click', function (ev) {
    var url = popupTarget(ev);
    if (!url || !POPUP_KINDS.test(url.pathname)) return;
    var d = ensureDialog();
    if (typeof d.showModal !== 'function') return; // very old browser: navigate
    ev.preventDefault();
    fullLink.href = url.href;
    frame.src = url.href;
    if (!d.open) d.showModal();
  });
})();
"""

# --------------------------------------------------------------------------
# KaTeX asset fetch
# --------------------------------------------------------------------------

KATEX_VERSION = "0.16.9"
KATEX_CDN_BASE = f"https://cdn.jsdelivr.net/npm/katex@{KATEX_VERSION}"

KATEX_FONT_NAMES = [
    "KaTeX_AMS-Regular", "KaTeX_Caligraphic-Bold", "KaTeX_Caligraphic-Regular",
    "KaTeX_Fraktur-Bold", "KaTeX_Fraktur-Regular", "KaTeX_Main-Bold",
    "KaTeX_Main-BoldItalic", "KaTeX_Main-Italic", "KaTeX_Main-Regular",
    "KaTeX_Math-BoldItalic", "KaTeX_Math-Italic", "KaTeX_SansSerif-Bold",
    "KaTeX_SansSerif-Italic", "KaTeX_SansSerif-Regular", "KaTeX_Script-Regular",
    "KaTeX_Size1-Regular", "KaTeX_Size2-Regular", "KaTeX_Size3-Regular",
    "KaTeX_Size4-Regular", "KaTeX_Typewriter-Regular",
]
KATEX_FONT_EXTS = [".ttf", ".woff", ".woff2"]

KATEX_FILES = {
    "/dist/katex.min.css": "katex.min.css",
    "/dist/katex.min.js": "katex.min.js",
    "/dist/contrib/auto-render.min.js": "auto-render.min.js",
}
for _name in KATEX_FONT_NAMES:
    for _ext in KATEX_FONT_EXTS:
        KATEX_FILES[f"/dist/fonts/{_name}{_ext}"] = f"fonts/{_name}{_ext}"

KATEX_LOCAL = True  # set to False in main() if download fails


# --------------------------------------------------------------------------
# Webfont fetch (Source Serif 4 for everything)
# --------------------------------------------------------------------------

# dest file (under assets/typefaces/) -> candidate CDN URLs, first hit wins
# (fontsource variable packages name their default file after the axis set,
# which differs per font, hence the candidates)
FONT_FILES: dict[str, list[str]] = {
    "source-serif-4-latin-wght-normal.woff2": [
        "https://cdn.jsdelivr.net/npm/@fontsource-variable/source-serif-4@5/files/source-serif-4-latin-wght-normal.woff2",
        "https://cdn.jsdelivr.net/npm/@fontsource-variable/source-serif-4@5/files/source-serif-4-latin-opsz-normal.woff2",
    ],
}


def download_fonts() -> bool:
    """Fetch the webfont locally. Non-fatal: on failure the CSS
    font stacks fall back to Georgia."""
    dest_dir = ASSETS_DIR / "typefaces"
    dest_dir.mkdir(parents=True, exist_ok=True)
    ok = True
    for relname, urls in FONT_FILES.items():
        dest = dest_dir / relname
        got = False
        for url in urls:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=20) as resp:
                    data = resp.read()
                dest.write_bytes(data)
                got = True
                break
            except (urllib.error.URLError, TimeoutError, OSError):
                continue
        if not got:
            print(f"[render] webfont download failed for {relname} (system fallback will be used)")
            ok = False
    return ok


def download_katex() -> bool:
    """Try to download all KaTeX assets locally. Returns True on full success."""
    (ASSETS_DIR / "fonts").mkdir(parents=True, exist_ok=True)
    ok = True
    for src, relpath in KATEX_FILES.items():
        url = KATEX_CDN_BASE + src
        dest = ASSETS_DIR / relpath
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
            dest.write_bytes(data)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            print(f"[render] KaTeX download failed for {url}: {exc}")
            ok = False
    return ok


# --------------------------------------------------------------------------
# Verification
# --------------------------------------------------------------------------

HREF_RE = re.compile(r'(?:href|src)="([^"]+)"')


def crawl_links(site_dir: Path) -> list[tuple[Path, str]]:
    """Return list of (file, broken_href) for every internal href/src that
    doesn't resolve to an existing file on disk."""
    broken = []
    html_files = list(site_dir.rglob("*.html"))
    for f in html_files:
        text = f.read_text(encoding="utf-8")
        for m in HREF_RE.finditer(text):
            target = m.group(1)
            if target.startswith(("http://", "https://", "mailto:", "//", "#")):
                continue
            target_no_frag = target.split("#", 1)[0].split("?", 1)[0]
            if not target_no_frag:
                continue
            resolved = (f.parent / target_no_frag).resolve()
            if not resolved.is_file():
                broken.append((f, target))
    return broken


def scan_markdown_artifacts(site_dir: Path) -> list[tuple[Path, str]]:
    """Look for tell-tale leftover markdown syntax that should have been
    converted or protected (very rough heuristic, not a validator)."""
    found = []
    patterns = ["[[", "]]", "**"]
    for f in site_dir.rglob("*.html"):
        text = f.read_text(encoding="utf-8")
        for p in patterns:
            if p in text:
                found.append((f, p))
    return found


# Version tag appended to the style.css / popup.js URLs in every page head.
# Content-derived, so it changes exactly when those files change and browser
# caches (Netlify serves /assets/* with a 7-day max-age) are busted on deploy.
ASSET_VERSION = hashlib.sha1((CSS + POPUP_JS).encode("utf-8")).hexdigest()[:10]


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------


def main():
    global KATEX_LOCAL

    print(f"[render] loading {STORE_PATH}")
    data = load_data()

    print(f"[render] wiping and recreating {SITE_DIR}")
    # Delete the directory's contents, not the directory itself: on Windows a
    # process whose cwd (or open handle) is site/ would make rmtree(SITE_DIR)
    # fail even though every file inside is deletable.
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    for child in SITE_DIR.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    ASSETS_DIR.mkdir(parents=True)

    print("[render] writing stylesheet and popup script")
    (ASSETS_DIR / "style.css").write_text(CSS, encoding="utf-8")
    (ASSETS_DIR / "popup.js").write_text(POPUP_JS, encoding="utf-8")

    print("[render] copying source PDFs into site/assets/papers/")
    papers_dst = ASSETS_DIR / "papers"
    papers_dst.mkdir(parents=True, exist_ok=True)
    for pdf in (BASE_DIR / "papers").glob("*.pdf"):
        shutil.copy2(pdf, papers_dst / pdf.name)

    figures_src = BASE_DIR / "store" / "figures"
    if figures_src.is_dir():
        print("[render] copying figure images into site/assets/figures/")
        shutil.copytree(figures_src, ASSETS_DIR / "figures")

    if HELP_SHOTS_DIR.is_dir():
        shots = sorted(HELP_SHOTS_DIR.glob("*.png"))
        if shots:
            print(f"[render] copying {len(shots)} help screenshots into site/assets/help/")
            help_dst = ASSETS_DIR / "help"
            help_dst.mkdir(parents=True, exist_ok=True)
            for shot in shots:
                shutil.copy2(shot, help_dst / shot.name)
    else:
        print("[render] no help-shots/ directory -- help page renders without figures")

    print("[render] downloading webfonts ...")
    if download_fonts():
        print("[render] webfonts downloaded into site/assets/typefaces/")

    print("[render] downloading KaTeX assets ...")
    KATEX_LOCAL = download_katex()
    if KATEX_LOCAL:
        print("[render] KaTeX assets downloaded locally into site/assets/")
    else:
        print("[render] KaTeX download incomplete -- pages will fall back to CDN <script> tags")

    builder = SiteBuilder(data)

    print("[render] writing paper-selection filter script")

    print("[render] generating pages ...")
    counts = builder.build_all()

    print("\n[render] === Page counts ===")
    expected = {
        "concept": len(data["concepts"]),
        "edge": len(data["edges"]),
        "theme": len(data["themes"]),
        "supertheme": len(data["superthemes"]),
        "superedge": len(data["superedges"]),
        "tissue": len(data["tissueThemes"]),
        "story": len(data.get("paperStories") or []),
        "figure": sum(len(e.get("items") or [])
                      for e in (data.get("figures") or {}).values()),
        "index": 1,
        "help": 1,
    }
    total_generated = 0
    total_expected = 0
    for kind in expected:
        gen = counts.get(kind, 0)
        exp = expected[kind]
        total_generated += gen
        total_expected += exp
        status = "OK" if gen == exp else "MISMATCH"
        print(f"  {kind:<12} generated={gen:<5} expected={exp:<5} [{status}]")
    print(f"  {'TOTAL':<12} generated={total_generated:<5} expected={total_expected:<5}")

    print("\n[render] === Unresolved [[id]] references ===")
    if builder.unresolved:
        for from_kind, from_id, target in builder.unresolved:
            print(f"  {from_kind}:{from_id} -> [[{target}]] UNRESOLVED")
    else:
        print("  none")

    print("\n[render] === Link crawl (internal href/src resolution) ===")
    broken = crawl_links(SITE_DIR)
    if broken:
        for f, target in broken:
            print(f"  BROKEN in {f.relative_to(SITE_DIR)}: {target}")
    else:
        print(f"  all internal links resolve (checked {len(list(SITE_DIR.rglob('*.html')))} html files)")

    print("\n[render] === Markdown-artifact scan ===")
    artifacts = scan_markdown_artifacts(SITE_DIR)
    if artifacts:
        for f, p in artifacts[:40]:
            print(f"  {f.relative_to(SITE_DIR)}: found stray '{p}'")
        if len(artifacts) > 40:
            print(f"  ... and {len(artifacts) - 40} more")
    else:
        print("  none found")

    print(f"\n[render] KaTeX: {'local (site/assets)' if KATEX_LOCAL else 'CDN fallback'}")
    print(f"[render] done. Open: {SITE_DIR / 'index.html'}")


if __name__ == "__main__":
    main()
