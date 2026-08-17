import json, re, sys

BASE = r"C:\Users\44759\Desktop\AI saftey explore\graph"

story_path = BASE + r"\staging\stage53-figure-story.json"
slice_path = BASE + r"\scratch_stage53_concept_slice.json"
fig_path = BASE + r"\scratch_stage52_figure_slice.json"

with open(story_path, encoding="utf-8") as f:
    story_doc = json.load(f)
with open(slice_path, encoding="utf-8") as f:
    slice_doc = json.load(f)
with open(fig_path, encoding="utf-8") as f:
    fig_doc = json.load(f)

errors = []
warnings = []

# Basic top-level shape
assert story_doc["paper"] == "sparse-autoencoders", "paper field mismatch"
story = story_doc["story"]

concept_ids = {c["id"] for c in slice_doc["concepts"]}
reserved_ids = set(slice_doc["reserved_node_ids"])
figure_ids = {item["id"] for item in fig_doc["items"]}

assert story["id"] == "sparse-autoencoders-experiments", "root id wrong"
assert story["tab"] == "The experiments", "tab wrong"

# intro checks
intro = story["intro"]
paras = intro.split("\n\n")
if len(paras) != 2:
    errors.append(f"intro must have exactly 2 paragraphs, found {len(paras)}")
word_count = len(intro.split())
if not (50 <= word_count <= 110):
    errors.append(f"intro word count {word_count} not in [50,110]")
if "[[" in intro:
    errors.append("intro contains wiki-link")

seen_ids = set()
figure_usage = {}  # figure id -> count
concept_ref_nodes = []  # (node_id, concept_id)
all_nodes = []

def check_wikilinks(text, node_id, node_ref_id, field_name):
    for m in re.finditer(r"\[\[([a-z0-9\-]+)(\|[^\]]*)?\]\]", text):
        cid = m.group(1)
        if cid not in concept_ids:
            errors.append(f"{node_id}.{field_name}: wiki-link to unknown concept id '{cid}'")
        if cid == node_ref_id:
            errors.append(f"{node_id}.{field_name}: wiki-link to node's own ref concept '{cid}'")

def walk(node, is_root=False):
    nid = node["id"]
    all_nodes.append(nid)
    if is_root:
        pass
    else:
        if nid in seen_ids:
            errors.append(f"duplicate node id: {nid}")
        seen_ids.add(nid)
        if not re.match(r"^sae-exp-[a-z0-9]+(-[a-z0-9]+)*$", nid):
            errors.append(f"node id not kebab-case with sae-exp- prefix: {nid}")
        if nid in reserved_ids:
            errors.append(f"node id collides with reserved id: {nid}")

    ref = node.get("ref")
    ref_id = None
    if ref is not None:
        if not (isinstance(ref, dict) and ref.get("kind") == "concept" and ref.get("id") in concept_ids):
            errors.append(f"{nid}: invalid ref {ref}")
        else:
            ref_id = ref["id"]
            concept_ref_nodes.append((nid, ref_id))

    children = node.get("children", [])
    narrative = node.get("narrative", "")
    if children:
        if len(narrative) < 50:
            errors.append(f"{nid}: internal node narrative < 50 chars ({len(narrative)})")
    else:
        if len(narrative) < 60:
            errors.append(f"{nid}: leaf node narrative < 60 chars ({len(narrative)})")

    check_wikilinks(narrative, nid, ref_id, "narrative")

    figs = node.get("figures", [])
    for fig_entry in figs:
        fig_id = fig_entry.get("figure")
        note = fig_entry.get("note", "")
        if fig_id not in figure_ids:
            errors.append(f"{nid}: unknown figure id '{fig_id}'")
        figure_usage[fig_id] = figure_usage.get(fig_id, 0) + 1
        if len(note) < 40:
            errors.append(f"{nid}: figure note for {fig_id} < 40 chars ({len(note)})")
        check_wikilinks(note, nid, ref_id, f"figures[{fig_id}].note")

    for child in children:
        walk(child, is_root=False)

walk(story, is_root=True)

# figure usage: exactly once for all 20
for fid in figure_ids:
    count = figure_usage.get(fid, 0)
    if count != 1:
        errors.append(f"figure {fid} attached {count} times (expected exactly 1)")
extra = set(figure_usage) - figure_ids
if extra:
    errors.append(f"figures attached that aren't in the 20-item slice: {extra}")

# concept ref count / uniqueness
ref_concept_ids = [c for (_, c) in concept_ref_nodes]
dupe_refs = {c for c in ref_concept_ids if ref_concept_ids.count(c) > 1}
if dupe_refs:
    errors.append(f"concept(s) used as ref more than once: {dupe_refs}")

print("Total nodes (incl. root):", len(all_nodes))
print("Concept-ref nodes:", len(concept_ref_nodes))
print("Concept refs used:", sorted(set(ref_concept_ids)))
print("Figures attached:", len(figure_usage), "/ 20")
print()

if errors:
    print(f"FAILED with {len(errors)} error(s):")
    for e in errors:
        print(" -", e)
    sys.exit(1)
else:
    print("ALL CHECKS PASSED")
