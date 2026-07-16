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
  python merge.py stories <staged.json>
  python merge.py paper-overlay <staged.json>
  python merge.py walks <staged.json>...
  python merge.py pages <staged.json>...
  python merge.py intros <staged.json>...
  python merge.py validate
"""
import json
import re
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
    "stories": [],
    "paperOverlay": None,
}

KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


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

    stories = store.get("stories") or []
    if store.get("overlay"):  # legacy single-story form, validated the same way
        stories = [store["overlay"]] + stories
    if stories:
        kind_ids = {"concept": concept_ids, "edge": edge_ids, "theme": theme_ids,
                    "supertheme": supertheme_ids,
                    "superedge": ids(store["superedges"]),
                    "tissue": ids(store["tissueThemes"])}
        seen_nodes = set()  # global: node ids become DOM ids on one index page
        seen_roots, seen_tabs = set(), set()

        for s in stories:
            sid = s.get("id", "?")
            if sid in seen_roots:
                err(f"stories: duplicate story id {sid!r}")
            seen_roots.add(sid)
            if len(stories) > 1:
                tab = (s.get("tab") or "").strip()
                if not tab:
                    err(f"story {sid}: needs a short 'tab' label")
                elif tab.lower() in seen_tabs:
                    err(f"story {sid}: duplicate tab label {tab!r}")
                seen_tabs.add(tab.lower())
            ref_seen = {"theme": [], "supertheme": []}

            def walk(node, path):
                nid = node.get("id", "")
                if not KEBAB.match(nid):
                    err(f"story {sid}: node id not kebab-case: {nid!r}")
                if nid in seen_nodes:
                    err(f"story {sid}: duplicate node id {nid!r} (must be unique across all stories)")
                seen_nodes.add(nid)
                if not node.get("name"):
                    err(f"story {sid} node {nid}: missing name")
                if node.get("children") and len(node.get("narrative", "").strip()) < 50:
                    err(f"story {sid} node {nid}: internal node needs a narrative")
                ref = node.get("ref")
                if ref:
                    kind, rid = ref.get("kind"), ref.get("id")
                    if kind not in kind_ids:
                        err(f"story {sid} node {nid}: unknown ref kind {kind!r}")
                    elif rid not in kind_ids[kind]:
                        err(f"story {sid} node {nid}: ref {kind}:{rid!r} does not exist")
                    elif kind in ref_seen:
                        ref_seen[kind].append(rid)
                for ch in node.get("children", []):
                    walk(ch, path + [nid])

            walk(s, [])
            # every story is a total lens: each theme placed exactly once
            placed = ref_seen["theme"]
            for t in sorted(set(t for t in placed if placed.count(t) > 1)):
                err(f"story {sid}: theme {t} placed more than once")
            for t in theme_ids - set(placed):
                err(f"story {sid}: theme {t} not placed (coverage must be total)")
            # superthemes: optional per story, but all-or-nothing and no repeats
            st_placed = ref_seen["supertheme"]
            for st in sorted(set(t for t in st_placed if st_placed.count(t) > 1)):
                err(f"story {sid}: supertheme {st} placed more than once")
            if st_placed:
                for st in supertheme_ids - set(st_placed):
                    err(f"story {sid}: uses superthemes but leaves out {st} "
                        f"(supertheme coverage is all-or-nothing)")

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
    for s in store.get("stories") or []:
        if s.get("intro"):
            check_intro(f"story {s['id']}", s["intro"])

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
                   "supertheme": "superthemes", "tissue": "tissueThemes",
                   "story": "stories"}


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

    if cmd == "concepts":
        merge_concepts(store, args, aliases)
    elif cmd == "themes":
        merge_simple(store, "themes", args)
    elif cmd == "edges":
        merge_simple(store, "edges", args)
    elif cmd == "superthemes":
        merge_simple(store, "superthemes", args)
    elif cmd == "superedges":
        merge_simple(store, "superedges", args)
    elif cmd == "tissue-themes":
        merge_simple(store, "tissueThemes", args)
    elif cmd == "stories":
        data = json.loads(Path(args[0]).read_text(encoding="utf-8"))
        store["stories"] = data["stories"]
        store.pop("overlay", None)  # legacy single-story key, superseded
    elif cmd == "paper-overlay":
        data = json.loads(Path(args[0]).read_text(encoding="utf-8"))
        store["paperOverlay"] = data["paperOverlay"]
    elif cmd == "walks":
        by_id = {t["id"]: t for t in store["themes"]}
        for f in args:
            data = json.loads(Path(f).read_text(encoding="utf-8"))
            for w in data["walks"]:
                if w["theme"] not in by_id:
                    raise SystemExit(f"walks: unknown theme {w['theme']!r} in {f}")
                by_id[w["theme"]]["walk"] = w["steps"]
    elif cmd == "pages":
        merge_pages(store, args)
    elif cmd == "intros":
        merge_intros(store, args)
    else:
        raise SystemExit(f"unknown command {cmd!r}")

    errors = validate(store)
    if errors:
        print("\n".join(errors))
        raise SystemExit(f"\nmerge aborted, store NOT written: {len(errors)} error(s)")
    save_store(store)
    print(f"merged {cmd}: store now has "
          + ", ".join(f"{len(store[k])} {k}" for k in
                      ("concepts", "themes", "edges", "superthemes", "superedges", "tissueThemes")))


if __name__ == "__main__":
    main()
