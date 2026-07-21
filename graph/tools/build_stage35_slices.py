"""Build slice files for the stage-35 page agents (G1-G5) and stage-36 walk agents (W1-W2).

Each page slice carries, per concept: the staged record, every staged CAA edge touching it,
the theme narratives it belongs to, and (for G5 revisions) the concept's current store
record with sections and its existing store edges. Run from graph/.
"""
import json

g = json.load(open('store/graph.json', encoding='utf-8'))
staged = json.load(open('staging/stage32-caa-concepts.json', encoding='utf-8'))['concepts']
stg = {c['id']: c for c in staged}
reg = {c['id']: c for c in g['concepts']}

new_edges = []
for b in ['p', 'q', 'r', 's']:
    new_edges += json.load(open(f'staging/stage34-edges-{b}.json', encoding='utf-8'))['edges']

themes_new = json.load(open('staging/stage33-themes-new.json', encoding='utf-8'))['themes']
themes_changed = json.load(open('staging/stage33-themes-changed.json', encoding='utf-8'))['themes']
all_theme_objs = {t['id']: t for t in g['themes']}
for t in themes_new + themes_changed:
    all_theme_objs[t['id']] = t

def themes_of(cid):
    return [{'id': t['id'], 'name': t['name'], 'narrative': t['narrative']}
            for t in all_theme_objs.values() if cid in t['members']]

def staged_edges_of(cid):
    return [e for e in new_edges if e['source'] == cid or e['target'] == cid]

def store_edges_of(cid):
    return [e for e in g['edges'] if e['source'] == cid or e['target'] == cid]

GROUPS = {
 'g1': ['contrastive-activation-addition', 'caa-steering-vector-construction', 'multiple-choice-contrast-pair-format', 'mean-difference-method', 'steering-vector', 'steering-multiplier', 'steering-vector-normalization', 'residual-stream', 'targeted-token-steering', 'steering-outside-residual-stream', 'caa-computational-efficiency', 'activation-engineering'],
 'g2': ['activation-addition', 'inference-time-intervention', 'representation-engineering-zou', 'in-context-vectors', 'linear-representation-hypothesis', 'linear-representations-of-sentiment', 'pca', 'activation-pca-visualization', 'behavioral-clustering', 'letter-clustering', 'token-level-cosine-similarity-analysis', 'inter-layer-similarity-and-transfer'],
 'g3': ['sycophancy', 'refusal-behavior', 'corrigibility', 'ai-coordination-behavior', 'myopic-reward-behavior', 'survival-instinct-behavior', 'advanced-ai-risk-dataset', 'sycophancy-eval-datasets-anthropic', 'caa-hallucination-dataset', 'caa-refusal-dataset', 'jailbreaks', 'caa-red-teaming-application'],
 'g4': ['multiple-choice-behavioral-evaluation', 'open-ended-generation-evaluation', 'gpt-4', 'mmlu', 'caa-system-prompt-comparison', 'caa-finetuning-comparison', 'system-prompting', 'few-shot-prompting', 'llama-2', 'llama-2-chat', 'base-chat-representation-comparison'],
 'g5': ['rlhf', 'supervised-fine-tuning', 'hallucination', 'truthfulqa', 'red-teaming', 'hhh-framework'],
}

new_ids = {c['id'] for c in staged if c['id'] not in reg}
assert set(GROUPS['g1'] + GROUPS['g2'] + GROUPS['g3'] + GROUPS['g4']) == new_ids, \
    (new_ids - set(GROUPS['g1'] + GROUPS['g2'] + GROUPS['g3'] + GROUPS['g4']),
     set(GROUPS['g1'] + GROUPS['g2'] + GROUPS['g3'] + GROUPS['g4']) - new_ids)

link_registry = sorted(set(reg) | set(stg))

for gname, cids in GROUPS.items():
    entries = []
    for cid in cids:
        rec = {'concept': stg[cid], 'themes': themes_of(cid), 'stagedEdges': staged_edges_of(cid)}
        if gname == 'g5':
            cur = reg[cid]
            rec['currentStoreRecord'] = cur
            rec['storeEdges'] = [{'id': e['id'], 'type': e['type'], 'source': e['source'],
                                  'target': e['target'], 'prose': e['prose'][:300]} for e in store_edges_of(cid)]
        entries.append(rec)
    out = {'concepts': entries, 'wikiLinkTargets': link_registry}
    json.dump(out, open(f'scratch_stage35_slice_{gname}.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(gname, len(entries), 'concepts')

# walk slices
def concept_brief(cid):
    src = stg.get(cid) or reg.get(cid)
    return {'name': src['name'], 'summary': src['summary']}

w1 = {'themes': [{'id': t['id'], 'name': t['name'], 'members': t['members'], 'narrative': t['narrative'],
                  'memberSummaries': {m: concept_brief(m) for m in t['members']}} for t in themes_new]}
json.dump(w1, open('scratch_stage36_walks_new.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

w2_themes = []
cur_walks = {t['id']: t.get('walk') for t in g['themes']}
for t in themes_changed:
    w2_themes.append({'id': t['id'], 'name': t['name'], 'members': t['members'], 'narrative': t['narrative'],
                      'currentWalk': cur_walks.get(t['id']),
                      'memberSummaries': {m: concept_brief(m) for m in t['members']}})
json.dump({'themes': w2_themes}, open('scratch_stage36_walks_changed.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('walk slices: 9 new,', len(w2_themes), 'changed')
