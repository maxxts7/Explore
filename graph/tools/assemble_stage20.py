"""Verify the four stage-20 story revisions and assemble staging/stage20-stories.json.

For each story it checks, against the current store:
  - the set of added node ids is exactly the expected 8 new theme placements
    (story 1 additionally: the new arc + supertheme node),
  - every new theme node refs the right theme and is a leaf,
  - no node was removed, no id/ref/era changed on surviving nodes,
  - pre-existing siblings keep their relative order,
and then reports every node whose name/narrative/claim/intro text changed, so the
coordinator can review the prose diff. Exits non-zero on any structural violation.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
store = json.loads((ROOT / "store" / "graph.json").read_text(encoding="utf-8"))

NEW_THEMES = [
    "learning-rewards-from-comparisons", "keeping-reward-models-on-distribution",
    "economics-of-human-feedback", "hidden-reward-experimental-design",
    "deep-rl-testbeds", "novel-behaviors-without-reward-functions",
    "policy-optimization-under-learned-rewards", "prior-human-in-the-loop-rl",
]
EXPECTED_EXTRA = {
    "story-diagnosis-to-machinery":
        set(NEW_THEMES) | {"arc-preferences-proof-of-concept",
                           "deep-rl-from-preferences-proof-of-concept"},
    "story-builders-path": {f"bp-{t}" for t in NEW_THEMES},
    "story-two-toolkits": {f"tk-{t}" for t in NEW_THEMES},
    "story-delegation-ladder": {f"dl-{t}" for t in NEW_THEMES},
}


def flatten(node, parent=None, acc=None):
    if acc is None:
        acc = {}
    acc[node["id"]] = {"node": node, "parent": parent,
                       "children": [c["id"] for c in node.get("children", [])]}
    for c in node.get("children", []):
        flatten(c, node["id"], acc)
    return acc


errors, prose_changes = [], []
out_stories = []
for old in store["stories"]:
    sid = old["id"]
    f = ROOT / "staging" / f"stage20-story-{sid}.json"
    if not f.exists():
        errors.append(f"{sid}: staged file missing")
        continue
    new = json.loads(f.read_text(encoding="utf-8"))
    out_stories.append(new)
    old_map, new_map = flatten(old), flatten(new)

    added = set(new_map) - set(old_map)
    removed = set(old_map) - set(new_map)
    if removed:
        errors.append(f"{sid}: nodes removed: {sorted(removed)}")
    if added != EXPECTED_EXTRA[sid]:
        errors.append(f"{sid}: added nodes {sorted(added)} != expected "
                      f"{sorted(EXPECTED_EXTRA[sid])}")

    for nid in set(old_map) & set(new_map):
        o, n = old_map[nid]["node"], new_map[nid]["node"]
        if o.get("ref") != n.get("ref"):
            errors.append(f"{sid}/{nid}: ref changed")
        if o.get("era") != n.get("era"):
            errors.append(f"{sid}/{nid}: era changed")
        old_kids = old_map[nid]["children"]
        new_kids = [k for k in new_map[nid]["children"] if k in old_map]
        if old_kids != new_kids:
            errors.append(f"{sid}/{nid}: pre-existing child order changed "
                          f"({old_kids} -> {new_kids})")
        for field in ("name", "narrative", "claim", "intro", "tab"):
            if o.get(field) != n.get(field):
                prose_changes.append(f"{sid}/{nid}: {field} changed")

    theme_ids = {t["id"] for t in store["themes"]} | set(NEW_THEMES)
    for nid in added:
        n = new_map[nid]["node"]
        ref = n.get("ref")
        if nid in NEW_THEMES or nid.split("-", 1)[-1] in NEW_THEMES or \
           any(nid == p + t for p in ("bp-", "tk-", "dl-") for t in NEW_THEMES):
            if not (nid == "arc-preferences-proof-of-concept" or
                    nid == "deep-rl-from-preferences-proof-of-concept"):
                want = nid[3:] if nid[:3] in ("bp-", "tk-", "dl-") else nid
                if ref != {"kind": "theme", "id": want}:
                    errors.append(f"{sid}/{nid}: bad ref {ref}")
                if n.get("children"):
                    errors.append(f"{sid}/{nid}: new theme node must be a leaf")
                if "narrative" in n:
                    errors.append(f"{sid}/{nid}: leaf must not carry narrative")

if errors:
    print("STRUCTURAL ERRORS:")
    print("\n".join(" - " + e for e in errors))
    sys.exit(1)

print("structure OK for all", len(out_stories), "stories")
print("\nprose changes for coordinator review:")
print("\n".join(" - " + p for p in prose_changes))

out = ROOT / "staging" / "stage20-stories.json"
out.write_text(json.dumps({"stories": out_stories}, indent=1, ensure_ascii=False),
               encoding="utf-8")
print(f"\nassembled {out}")
