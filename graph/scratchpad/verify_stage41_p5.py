import json, re

with open("staging/stage41-pages-p5.json", encoding="utf-8") as f:
    out = json.load(f)

with open("scratch_stage41_pages_p5.json", encoding="utf-8") as f:
    src = json.load(f)

ids = set()
with open("scratch_stage41_link_registry.txt", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        m = re.match(r'^(concept|edge|theme|supertheme|superedge|tissue):\s*([a-zA-Z0-9\-\.]+)\s*\|', line)
        if m:
            ids.add(m.group(2))

link_re = re.compile(r'\[\[([^\]|]+)(\|[^\]]+)?\]\]')

for page in out["pages"]:
    pid = page["id"]
    cur_sections = src[pid]["current"]["sections"]
    new_sections = page["sections"]
    n_old = len(cur_sections)
    ok = all(new_sections[i] == cur_sections[i] for i in range(n_old))
    print(f"--- {pid} --- old={n_old} new_total={len(new_sections)} prefix_unchanged={ok}")
    for sec in new_sections[n_old:]:
        body = sec["body"]
        wc = len(body.split())
        links = link_re.findall(body)
        bad = [l[0] for l in links if l[0] not in ids]
        print(f"   heading: {sec['heading']!r}")
        print(f"   word_count~={wc}  links={[l[0] for l in links]}")
        if bad:
            print("   !!! INVALID LINKS:", bad)
