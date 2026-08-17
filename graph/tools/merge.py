"""Central merge for the concept-graph store.

Workers stage JSON files in graph/staging/. This script is the only writer of
graph/store/graph.json. Each subcommand ingests staged work into an in-memory
copy of the store, validates the whole store, and writes atomically only if
every check passes. On any failure it writes nothing and reports the errors.

Usage:
  python merge.py init
  python merge.py concepts <staged.json>... [--aliases aliases.json]
  python merge.py themes <staged.json>
  python merge.py edges <staged.json>...
  python merge.py superthemes <staged.json>
  python merge.py superedges <staged.json>...
  python merge.py tissue-themes <staged.json>
  python merge.py paper-stories <staged.json>...
  python merge.py drop-stories
  python merge.py paper-overlay <staged.json>
  python merge.py walks <staged.json>...
  python merge.py pages <staged.json>...
  python merge.py intros <staged.json>...
  python merge.py figures <staged.json>...
  python merge.py figure-pages <staged.json>...
  python merge.py figure-story <staged.json>...
  python merge.py apply <manifest.json>
  python merge.py validate

`apply` runs several subcommands as one transaction — one in-memory store, one
validation, one atomic write — for additions that can only be valid together
(e.g. a new paper's concepts plus the theme/story/overlay updates that cover
them). The manifest lists ordinary steps:
  {"steps": [{"cmd": "concepts", "files": ["staging/x.json"], "aliases": "staging/a.json"},
             {"cmd": "themes",   "files": ["staging/y.json"]}, ...]}
File paths are relative to the graph/ directory (this file's parent's parent).
"""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORE = ROOT / "store" / "graph.json"

EMPTY = {
    "papers": [],
    "concepts": [],
    "edges": [],
    "themes": [],
    "superthemes": [],
    "superedges": [],
    "tissueThemes": [],
    "paperStories": [],
    "paperOverlay": None,
    "figures": {},
}

KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

FIGURE_CLASSIFICATIONS = ("data-and-experiments", "results-and-interpretation")
# Papers merged before the figure stage existed (stages 0-43). They are exempt
# from the figures-required rule until their backfill lands; every paper added
# after sparse-autoencoders MUST bring its figure inventory, pages, and
# experiments story in the same apply transaction, or validation rejects the add.
FIGURE_BACKFILL_PENDING = {
    "concrete-problems", "instructgpt", "constitutional-ai",
    "deep-rl-human-prefs", "contrastive-activation-addition", "persona-vectors",
}
# (staged src, store dest) image copies, executed only after validation passes.
PENDING_IMAGE_COPIES = []


def load_store():
    if STORE.exists():
        return json.loads(STORE.read_text(encoding="utf-8"))
    return json.loads(json.dumps(EMPTY))


def save_store(store):
    tmp = STORE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(store, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(STORE)


def ids(coll):
    return {x["id"] for x in coll}


def validate(store):
    errors = []

    def err(msg):
        errors.append(msg)

    for coll_name in ("concepts", "edges", "themes", "superthemes", "superedges", "tissueThemes"):
        seen = set()
        for item in store[coll_name]:
            cid = item.get("id", "")
            if not KEBAB.match(cid):
                err(f"{coll_name}: id not kebab-case: {cid!r}")
            if cid in seen:
                err(f"{coll_name}: duplicate id {cid!r}")
            seen.add(cid)

    paper_ids = ids(store["papers"])
    concept_ids = ids(store["concepts"])
    theme_ids = ids(store["themes"])
    edge_ids = ids(store["edges"])
    supertheme_ids = ids(store["superthemes"])

    for c in store["concepts"]:
        if c.get("parent") and c["parent"] not in concept_ids:
            err(f"concept {c['id']}: parent {c['parent']!r} does not exist")
        if not c.get("name") or not c.get("summary"):
            err(f"concept {c['id']}: missing name or summary")
        origins = c.get("origins", [])
        if not origins:
            err(f"concept {c['id']}: no origins")
        for o in origins:
            if o.get("paper") not in paper_ids:
                err(f"concept {c['id']}: origin paper {o.get('paper')!r} unknown")
            if o.get("role") not in ("introduced", "refined", "inherited"):
                err(f"concept {c['id']}: bad role {o.get('role')!r}")
        for loc in c.get("locators", []):
            if not loc.get("section") or not isinstance(loc.get("page"), int):
                err(f"concept {c['id']}: malformed locator {loc}")
            if loc.get("paper") and loc["paper"] not in paper_ids:
                err(f"concept {c['id']}: locator paper {loc['paper']!r} unknown")

    for e in store["edges"]:
        if e.get("source") not in concept_ids:
            err(f"edge {e['id']}: source {e.get('source')!r} not a concept")
        if e.get("target") not in concept_ids:
            err(f"edge {e['id']}: target {e.get('target')!r} not a concept")
        if not e.get("type"):
            err(f"edge {e['id']}: missing type")
        if len(e.get("prose", "").strip()) < 200:
            err(f"edge {e['id']}: prose missing or too short to teach anything")

    for t in store["themes"]:
        if not t.get("narrative", "").strip():
            err(f"theme {t['id']}: missing narrative")
        if len(t.get("members", [])) < 2:
            err(f"theme {t['id']}: fewer than 2 members")
        for m in t.get("members", []):
            if m not in concept_ids:
                err(f"theme {t['id']}: member {m!r} not a concept")
        walk = t.get("walk")
        if walk is not None:
            step_cids = [s.get("concept") for s in walk]
            if len(step_cids) != len(set(step_cids)):
                err(f"theme {t['id']}: walk repeats a concept")
            if set(step_cids) != set(t.get("members", [])):
                missing = set(t.get("members", [])) - set(step_cids)
                extra = set(step_cids) - set(t.get("members", []))
                err(f"theme {t['id']}: walk must cover exactly the members "
                    f"(missing {sorted(missing)}, extra {sorted(extra)})")
            for s in walk:
                if len(s.get("prose", "").strip()) < 80:
                    err(f"theme {t['id']}: walk step {s.get('concept')!r} prose too short to tie anything together")

    if store["themes"]:
        covered = set()
        for t in store["themes"]:
            covered.update(t.get("members", []))
        for c in concept_ids - covered:
            err(f"concept {c} belongs to no theme (coverage must be total)")

    for st in store["superthemes"]:
        if not st.get("narrative", "").strip():
            err(f"supertheme {st['id']}: missing narrative")
        for m in st.get("members", []):
            if m not in theme_ids:
                err(f"supertheme {st['id']}: member {m!r} not a theme")

    if store["superthemes"]:
        covered = set()
        for st in store["superthemes"]:
            covered.update(st.get("members", []))
        for t in theme_ids - covered:
            err(f"theme {t} belongs to no supertheme (coverage must be total)")

    st_of_theme = {}
    for st in store["superthemes"]:
        for m in st.get("members", []):
            st_of_theme.setdefault(m, set()).add(st["id"])
    for se in store["superedges"]:
        if se.get("source") not in theme_ids or se.get("target") not in theme_ids:
            err(f"superedge {se['id']}: endpoints must be themes")
        elif not (st_of_theme.get(se["source"], set()) & st_of_theme.get(se["target"], set())):
            err(f"superedge {se['id']}: endpoints share no supertheme")
        if not se.get("type"):
            err(f"superedge {se['id']}: missing type")
        if len(se.get("prose", "").strip()) < 200:
            err(f"superedge {se['id']}: prose missing or too short")

    for tt in store["tissueThemes"]:
        if not tt.get("narrative", "").strip():
            err(f"connective theme {tt['id']}: missing narrative")
        for m in tt.get("members", []):
            if m not in edge_ids:
                err(f"connective theme {tt['id']}: member {m!r} not an edge")

    if store["tissueThemes"]:
        covered = set()
        for tt in store["tissueThemes"]:
            covered.update(tt.get("members", []))
        for e in edge_ids - covered:
            err(f"edge {e} belongs to no connective theme (coverage must be total)")

    kind_ids = {"concept": concept_ids, "edge": edge_ids, "theme": theme_ids,
                "supertheme": supertheme_ids,
                "superedge": ids(store["superedges"]),
                "tissue": ids(store["tissueThemes"])}

    paper_stories = store.get("paperStories") or []
    if paper_stories:
        seen_entries = set()
        for entry in paper_stories:
            pid = entry.get("id", "?")
            if pid not in paper_ids:
                err(f"paper stories: paper {pid!r} does not exist")
            if pid in seen_entries:
                err(f"paper stories: duplicate entry for {pid!r}")
            seen_entries.add(pid)
            p_stories = entry.get("stories") or []
            if not p_stories:
                err(f"paper stories {pid}: no stories")
            seen_nodes_p = set()  # node ids become DOM ids on the paper's page
            seen_tabs_p = set()
            for s in p_stories:
                sid = s.get("id", "?")
                tab = (s.get("tab") or "").strip()
                if not tab:
                    err(f"paper story {sid}: needs a short 'tab' label")
                elif tab.lower() in seen_tabs_p:
                    err(f"paper story {sid}: duplicate tab label {tab!r}")
                seen_tabs_p.add(tab.lower())
                if not (s.get("intro") or "").strip():
                    err(f"paper story {sid}: missing intro")
                themes_placed = set()

                def walk_ps(node, _sid=sid, _placed=themes_placed):
                    nid = node.get("id", "")
                    if not KEBAB.match(nid):
                        err(f"paper story {_sid}: node id not kebab-case: {nid!r}")
                    if nid in seen_nodes_p:
                        err(f"paper story {_sid}: duplicate node id {nid!r} "
                            f"(must be unique across the paper's stories)")
                    seen_nodes_p.add(nid)
                    if not node.get("name"):
                        err(f"paper story {_sid} node {nid}: missing name")
                    if node.get("children") and len(node.get("narrative", "").strip()) < 50:
                        err(f"paper story {_sid} node {nid}: internal node needs a narrative")
                    ref = node.get("ref")
                    if ref:
                        kind, rid = ref.get("kind"), ref.get("id")
                        if kind not in kind_ids:
                            err(f"paper story {_sid} node {nid}: unknown ref kind {kind!r}")
                        elif rid not in kind_ids[kind]:
                            err(f"paper story {_sid} node {nid}: ref {kind}:{rid!r} does not exist")
                        elif kind == "theme":
                            if rid in _placed:
                                err(f"paper story {_sid}: theme {rid} placed more than once")
                            _placed.add(rid)
                    for ch in node.get("children", []):
                        walk_ps(ch, _sid, _placed)

                walk_ps(s)
        for pid in paper_ids - seen_entries:
            err(f"paper stories: paper {pid} has no entry (coverage must be total)")

    paper_overlay = store.get("paperOverlay")
    if paper_overlay:
        if len(paper_overlay.get("narrative", "").strip()) < 50:
            err("paper overlay: missing or too-short top narrative")
        seen_po = set()
        for entry in paper_overlay.get("papers", []):
            pid = entry.get("paper")
            if pid not in paper_ids:
                err(f"paper overlay: paper {pid!r} does not exist")
            if pid in seen_po:
                err(f"paper overlay: duplicate paper {pid!r}")
            seen_po.add(pid)
            if len(entry.get("narrative", "").strip()) < 50:
                err(f"paper overlay: paper {pid!r} narrative missing or too short")
        for pid in paper_ids - seen_po:
            err(f"paper overlay: paper {pid} has no entry (coverage must be total)")

    figures = store.get("figures") or {}
    for pid in paper_ids - set(figures) - FIGURE_BACKFILL_PENDING:
        err(f"paper {pid}: no figure inventory (figures/pages/story are "
            f"required for every new paper; land them in the same apply)")
    pending_dests = {dest for _src, dest in PENDING_IMAGE_COPIES}
    for pid, entry in figures.items():
        if pid not in paper_ids:
            err(f"figures: paper {pid!r} does not exist")
        items = entry.get("items") or []
        if not items:
            err(f"figures {pid}: empty inventory")
        seen_f = set()
        for it in items:
            fid = it.get("id", "")
            if not KEBAB.match(fid):
                err(f"figures {pid}: id not kebab-case: {fid!r}")
            if fid in seen_f:
                err(f"figures {pid}: duplicate id {fid!r}")
            seen_f.add(fid)
            if it.get("kind") not in ("figure", "table"):
                err(f"figure {pid}/{fid}: bad kind {it.get('kind')!r}")
            if it.get("classification") not in FIGURE_CLASSIFICATIONS:
                err(f"figure {pid}/{fid}: bad classification {it.get('classification')!r}")
            if not it.get("label") or not it.get("section"):
                err(f"figure {pid}/{fid}: missing label or section locator")
            if not isinstance(it.get("page"), int):
                err(f"figure {pid}/{fid}: page must be an int")
            image = it.get("image", "")
            dest = STORE.parent / image
            if not image or not (dest.is_file() or dest in pending_dests):
                err(f"figure {pid}/{fid}: image file missing: {image!r}")
            if not it.get("name"):
                err(f"figure {pid}/{fid}: missing page name")
            secs = it.get("sections") or []
            if not secs:
                err(f"figure {pid}/{fid}: no page sections (every figure needs a page)")
            for s in secs:
                if not s.get("heading") or len(s.get("body", "").strip()) < 100:
                    err(f"figure {pid}/{fid}: section {s.get('heading')!r} empty or too thin")
        # The experiments story: the paper's figures retold as ONE rooted tree
        # with connective narrative, every figure placed exactly once. Its node
        # ids become DOM ids on the paper's story page, which also carries the
        # paperStories node ids — so the two sets must be disjoint.
        story = entry.get("story")
        if not story:
            err(f"figures {pid}: no experiments story (the figures must be "
                f"told as one connected story; land it with the inventory)")
        else:
            item_ids = {it["id"] for it in items}
            reserved = set()
            for ps_entry in store.get("paperStories") or []:
                if ps_entry.get("id") != pid:
                    continue

                def collect_ids(node):
                    reserved.add(node.get("id"))
                    for ch in node.get("children") or []:
                        collect_ids(ch)

                for s in ps_entry.get("stories") or []:
                    collect_ids(s)
            if story.get("id") != f"{pid}-experiments":
                err(f"figures {pid}: story root id must be {pid}-experiments "
                    f"(frozen deep-link anchor), got {story.get('id')!r}")
            if not (story.get("tab") or "").strip():
                err(f"figures {pid}: story needs a short 'tab' label")
            if not (story.get("intro") or "").strip():
                err(f"figures {pid}: story missing intro")
            placed = []
            seen_nodes = set()

            def walk_fs(node):
                nid = node.get("id", "")
                if not KEBAB.match(nid):
                    err(f"figures {pid} story: node id not kebab-case: {nid!r}")
                if nid in seen_nodes:
                    err(f"figures {pid} story: duplicate node id {nid!r}")
                seen_nodes.add(nid)
                if nid in reserved:
                    err(f"figures {pid} story: node id {nid!r} collides with "
                        f"a telling's node id on the same page")
                if not node.get("name"):
                    err(f"figures {pid} story node {nid}: missing name")
                ref = node.get("ref")
                children = node.get("children") or []
                if ref:
                    if ref.get("kind") != "figure":
                        err(f"figures {pid} story node {nid}: refs must be "
                            f"figures, got {ref.get('kind')!r}")
                    elif ref.get("id") not in item_ids:
                        err(f"figures {pid} story node {nid}: unknown figure "
                            f"{ref.get('id')!r}")
                    else:
                        placed.append(ref["id"])
                    if children:
                        err(f"figures {pid} story node {nid}: figure nodes "
                            f"must be leaves")
                    if len((node.get("narrative") or "").strip()) < 60:
                        err(f"figures {pid} story node {nid}: figure node "
                            f"needs prose placing it in the arc")
                elif len((node.get("narrative") or "").strip()) < 50:
                    err(f"figures {pid} story node {nid}: connective node "
                        f"needs a narrative")
                for ch in children:
                    walk_fs(ch)

            walk_fs(story)
            if len(placed) != len(set(placed)):
                dupes = sorted({x for x in placed if placed.count(x) > 1})
                err(f"figures {pid}: story places {dupes} more than once")
            missing = item_ids - set(placed)
            if missing:
                err(f"figures {pid}: story misses {sorted(missing)} "
                    f"(coverage must be total)")

    pages_done = [c for c in store["concepts"] if c.get("sections")]
    for c in pages_done:
        for s in c["sections"]:
            if not s.get("heading") or len(s.get("body", "").strip()) < 100:
                err(f"concept {c['id']}: section {s.get('heading')!r} empty or too thin")

    def check_intro(owner, intro):
        paras = [p for p in intro.split("\n\n") if p.strip()]
        if len(paras) != 2:
            err(f"{owner}: intro must be exactly two paragraphs, got {len(paras)}")
        if "[[" in intro:
            err(f"{owner}: intro must not contain wiki-links")
        words = len(intro.split())
        if not 35 <= words <= 160:
            err(f"{owner}: intro is {words} words, outside 35-160")

    for coll, kindname in (("concepts", "concept"), ("themes", "theme"),
                           ("superthemes", "supertheme"), ("tissueThemes", "connective theme")):
        for item in store[coll]:
            if item.get("intro"):
                check_intro(f"{kindname} {item['id']}", item["intro"])
    for entry in store.get("paperStories") or []:
        for s in entry.get("stories") or []:
            if s.get("intro"):
                check_intro(f"paper story {s['id']}", s["intro"])
    for pid, entry in figures.items():
        s = entry.get("story") or {}
        if s.get("intro"):
            check_intro(f"figures story {pid}", s["intro"])

    return errors


def merge_concepts(store, staged_files, aliases):
    for f in staged_files:
        data = json.loads(Path(f).read_text(encoding="utf-8"))
        paper = data["paper"]
        if paper["id"] not in ids(store["papers"]):
            store["papers"].append(paper)
        by_id = {c["id"]: c for c in store["concepts"]}
        for sc in data["concepts"]:
            cid = aliases.get(sc["id"], sc["id"])
            parent = sc.get("parent")
            parent = aliases.get(parent, parent) if parent else None
            locators = [dict(loc, paper=paper["id"]) for loc in sc.get("locators", [])]
            origin = {"paper": paper["id"], "role": sc["role"],
                      "summary": sc["summary"], "notes": sc.get("notes", "")}
            if cid in by_id:
                c = by_id[cid]
                if not any(o["paper"] == paper["id"] for o in c["origins"]):
                    c["origins"].append(origin)
                c["locators"].extend(locators)
                if parent and not c.get("parent"):
                    c["parent"] = parent
            else:
                c = {"id": cid, "name": sc["name"], "summary": sc["summary"],
                     "parent": parent, "origins": [origin], "locators": locators,
                     "sections": []}
                store["concepts"].append(c)
                by_id[cid] = c


def merge_simple(store, key, staged_files):
    by_id = {x["id"]: x for x in store[key]}
    for f in staged_files:
        data = json.loads(Path(f).read_text(encoding="utf-8"))
        items = data[key] if isinstance(data, dict) else data
        for item in items:
            if item["id"] in by_id:
                by_id[item["id"]].update(item)
            else:
                store[key].append(item)
                by_id[item["id"]] = item


INTRO_KIND_COLL = {"concept": "concepts", "theme": "themes",
                   "supertheme": "superthemes", "tissue": "tissueThemes"}


def merge_intros(store, staged_files):
    index = {}
    for kind, coll in INTRO_KIND_COLL.items():
        for item in store.get(coll) or []:
            index[(kind, item["id"])] = item
    for f in staged_files:
        data = json.loads(Path(f).read_text(encoding="utf-8"))
        for entry in data["intros"]:
            key = (entry["kind"], entry["id"])
            if key not in index:
                raise SystemExit(f"intros: unknown {entry['kind']} {entry['id']!r} in {f}")
            index[key]["intro"] = entry["intro"].strip()


def merge_pages(store, staged_files):
    by_id = {c["id"]: c for c in store["concepts"]}
    for f in staged_files:
        data = json.loads(Path(f).read_text(encoding="utf-8"))
        items = data["pages"] if isinstance(data, dict) else data
        for page in items:
            cid = page["id"]
            if cid not in by_id:
                raise SystemExit(f"pages: unknown concept {cid!r} in {f}")
            by_id[cid]["sections"] = page["sections"]
            if page.get("summary"):  # optional refresh when the old one was paper-specific
                by_id[cid]["summary"] = page["summary"]


def merge_figures(store, staged_files):
    """Ingest a paper's figure inventory. Staged image paths are relative to
    graph/; they are verified now, rewritten to figures/<paper>/<file> relative
    to store/, and copied there only after the whole store validates."""
    store.setdefault("figures", {})
    for f in staged_files:
        data = json.loads(Path(f).read_text(encoding="utf-8"))
        pid = data["paper"]
        entry = store["figures"].setdefault(pid, {"items": [], "story": None})
        by_id = {it["id"]: it for it in entry["items"]}
        for it in data["figures"]:
            src = ROOT / it["image"]
            if not src.is_file():
                raise SystemExit(f"figures: staged image missing: {it['image']} (in {f})")
            item = dict(it, image=f"figures/{pid}/{src.name}")
            PENDING_IMAGE_COPIES.append((src, STORE.parent / item["image"]))
            if item["id"] in by_id:
                by_id[item["id"]].update(item)
            else:
                entry["items"].append(item)
                by_id[item["id"]] = item


def merge_figure_pages(store, staged_files):
    figures = store.get("figures") or {}
    for f in staged_files:
        data = json.loads(Path(f).read_text(encoding="utf-8"))
        entry = figures.get(data["paper"])
        if entry is None:
            raise SystemExit(f"figure-pages: paper {data['paper']!r} has no figure "
                             f"inventory (run figures first) in {f}")
        by_id = {it["id"]: it for it in entry["items"]}
        for page in data["pages"]:
            if page["id"] not in by_id:
                raise SystemExit(f"figure-pages: unknown figure {page['id']!r} in {f}")
            by_id[page["id"]]["name"] = page["name"]
            by_id[page["id"]]["sections"] = page["sections"]


def merge_figure_story(store, staged_files):
    figures = store.get("figures") or {}
    for f in staged_files:
        data = json.loads(Path(f).read_text(encoding="utf-8"))
        entry = figures.get(data["paper"])
        if entry is None:
            raise SystemExit(f"figure-story: paper {data['paper']!r} has no figure "
                             f"inventory (run figures first) in {f}")
        entry["story"] = data["story"]
        # The story replaces the retired flat two-section form.
        entry.pop("dataAndExperiments", None)
        entry.pop("resultsAndInterpretation", None)


def run_step(store, cmd, files, aliases):
    if cmd == "concepts":
        merge_concepts(store, files, aliases)
    elif cmd == "themes":
        merge_simple(store, "themes", files)
    elif cmd == "edges":
        merge_simple(store, "edges", files)
    elif cmd == "superthemes":
        merge_simple(store, "superthemes", files)
    elif cmd == "superedges":
        merge_simple(store, "superedges", files)
    elif cmd == "tissue-themes":
        merge_simple(store, "tissueThemes", files)
    elif cmd == "drop-stories":
        # Corpus-wide stories are retired; the paper story pages are the only
        # stories. Also drops the legacy single-story "overlay" key.
        store.pop("stories", None)
        store.pop("overlay", None)
    elif cmd == "paper-stories":
        store.setdefault("paperStories", [])
        merge_simple(store, "paperStories", files)
    elif cmd == "paper-overlay":
        data = json.loads(Path(files[0]).read_text(encoding="utf-8"))
        store["paperOverlay"] = data["paperOverlay"]
    elif cmd == "walks":
        by_id = {t["id"]: t for t in store["themes"]}
        for f in files:
            data = json.loads(Path(f).read_text(encoding="utf-8"))
            for w in data["walks"]:
                if w["theme"] not in by_id:
                    raise SystemExit(f"walks: unknown theme {w['theme']!r} in {f}")
                by_id[w["theme"]]["walk"] = w["steps"]
    elif cmd == "pages":
        merge_pages(store, files)
    elif cmd == "intros":
        merge_intros(store, files)
    elif cmd == "figures":
        merge_figures(store, files)
    elif cmd == "figure-pages":
        merge_figure_pages(store, files)
    elif cmd == "figure-story":
        merge_figure_story(store, files)
    else:
        raise SystemExit(f"unknown command {cmd!r}")


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    cmd, args = sys.argv[1], sys.argv[2:]

    if cmd == "init":
        STORE.parent.mkdir(parents=True, exist_ok=True)
        save_store(json.loads(json.dumps(EMPTY)))
        print("store initialized")
        return

    store = load_store()

    if cmd == "validate":
        errors = validate(store)
        if errors:
            print("\n".join(errors))
            raise SystemExit(f"\n{len(errors)} validation error(s)")
        print("store valid")
        return

    aliases = {}
    if "--aliases" in args:
        i = args.index("--aliases")
        aliases = json.loads(Path(args[i + 1]).read_text(encoding="utf-8"))
        args = args[:i] + args[i + 2:]

    if cmd == "apply":
        manifest = json.loads(Path(args[0]).read_text(encoding="utf-8"))
        for step in manifest["steps"]:
            step_aliases = {}
            if step.get("aliases"):
                step_aliases = json.loads(Path(step["aliases"]).read_text(encoding="utf-8"))
            run_step(store, step["cmd"], step.get("files", []), step_aliases)
    else:
        run_step(store, cmd, args, aliases)

    errors = validate(store)
    if errors:
        print("\n".join(errors))
        raise SystemExit(f"\nmerge aborted, store NOT written: {len(errors)} error(s)")
    for src, dest in PENDING_IMAGE_COPIES:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    save_store(store)
    n_figs = sum(len(e.get("items") or []) for e in (store.get("figures") or {}).values())
    print(f"merged {cmd}: store now has "
          + ", ".join(f"{len(store[k])} {k}" for k in
                      ("concepts", "themes", "edges", "superthemes", "superedges", "tissueThemes"))
          + f", {n_figs} figures")


if __name__ == "__main__":
    main()
