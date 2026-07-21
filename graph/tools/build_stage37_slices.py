"""Build slices for the paperStories agent and the two intros agents. Run from graph/."""
import json

g = json.load(open('store/graph.json', encoding='utf-8'))
staged = json.load(open('staging/stage32-caa-concepts.json', encoding='utf-8'))['concepts']

edges = []
for b in ['p', 'q', 'r', 's']:
    edges += json.load(open(f'staging/stage34-edges-{b}.json', encoding='utf-8'))['edges']
themes_new = json.load(open('staging/stage33-themes-new.json', encoding='utf-8'))['themes']
themes_changed = json.load(open('staging/stage33-themes-changed.json', encoding='utf-8'))['themes']
st_new = json.load(open('staging/stage33-supertheme-new.json', encoding='utf-8'))['superthemes'][0]
st_pipe = json.load(open('staging/stage33-supertheme-pipeline.json', encoding='utf-8'))['superthemes'][0]
tissue_new = json.load(open('staging/stage34-tissue-new.json', encoding='utf-8'))['tissueThemes']
tissue_upd = json.load(open('staging/stage34-tissue-updated.json', encoding='utf-8'))['tissueThemes']
superedges = json.load(open('staging/stage34-superedges.json', encoding='utf-8'))['superedges']

# --- paperStories slice ---
drlhp_entry = next(p for p in g['paperStories'] if p['id'] == 'deep-rl-human-prefs')
ps_slice = {
    'templateEntry': drlhp_entry,
    'concepts': [{'id': c['id'], 'name': c['name'], 'role': c['role'], 'summary': c['summary']} for c in staged],
    'newThemes': [{'id': t['id'], 'name': t['name'], 'members': t['members'], 'narrative': t['narrative']} for t in themes_new],
    'changedThemes': [{'id': t['id'], 'name': t['name'], 'members': t['members']} for t in themes_changed],
    'newSupertheme': st_new,
    'edges': [{'id': e['id'], 'type': e['type'], 'source': e['source'], 'target': e['target'],
               'hindsight': e['hindsight'], 'proseFirstSentence': e['prose'].split('. ')[0] + '.'} for e in edges],
    'newConnectiveThemes': [{'id': t['id'], 'name': t['name'], 'members': t['members'], 'narrative': t['narrative']} for t in tissue_new],
    'updatedConnectiveThemes': [{'id': t['id'], 'name': t['name']} for t in tissue_upd],
    'superedges': [{'id': e['id'], 'type': e['type'], 'source': e['source'], 'target': e['target']} for e in superedges],
}
json.dump(ps_slice, open('scratch_stage37_paperstories_slice.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

# --- intros slices ---
reg = {c['id']: c for c in g['concepts']}
new_ids = sorted(c['id'] for c in staged if c['id'] not in reg)
sample_intros = []
for c in g['concepts']:
    if c.get('intro') and len(sample_intros) < 2:
        sample_intros.append({'kind': 'concept', 'id': c['id'], 'intro': c['intro']})
th_intro = next(t for t in g['themes'] if t.get('intro'))
sample_intros.append({'kind': 'theme', 'id': th_intro['id'], 'intro': th_intro['intro']})

i1 = {'concepts': [{'id': c['id'], 'name': c['name'], 'role': c['role'], 'summary': c['summary'],
                    'notes': c.get('notes', '')} for c in staged if c['id'] in set(new_ids)],
      'sampleIntros': sample_intros}
json.dump(i1, open('scratch_stage37_intros_concepts.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

cur_theme = {t['id']: t for t in g['themes']}
cur_tissue = {t['id']: t for t in g['tissueThemes']}
cur_st = {s['id']: s for s in g['superthemes']}
refresh_candidates = []
for t in themes_changed:
    refresh_candidates.append({'kind': 'theme', 'id': t['id'], 'currentIntro': cur_theme[t['id']].get('intro'),
                               'revisedNarrative': t['narrative']})
for t in tissue_upd:
    refresh_candidates.append({'kind': 'tissue', 'id': t['id'], 'currentIntro': cur_tissue[t['id']].get('intro'),
                               'revisedNarrative': t['narrative']})
refresh_candidates.append({'kind': 'supertheme', 'id': st_pipe['id'], 'currentIntro': cur_st[st_pipe['id']].get('intro'),
                           'revisedNarrative': st_pipe['narrative']})
for cid in ['rlhf', 'supervised-fine-tuning', 'hallucination', 'truthfulqa', 'red-teaming', 'hhh-framework']:
    c = reg[cid]
    caa = next(x for x in staged if x['id'] == cid)
    refresh_candidates.append({'kind': 'concept', 'id': cid, 'currentIntro': c.get('intro'),
                               'newOriginSummary': caa['summary'], 'newOriginRole': caa['role']})

i2 = {'newThemes': [{'id': t['id'], 'name': t['name'], 'narrative': t['narrative']} for t in themes_new],
      'newSupertheme': {'id': st_new['id'], 'name': st_new['name'], 'narrative': st_new['narrative']},
      'newConnectiveThemes': [{'id': t['id'], 'name': t['name'], 'narrative': t['narrative']} for t in tissue_new],
      'refreshCandidates': refresh_candidates,
      'sampleIntros': sample_intros}
json.dump(i2, open('scratch_stage37_intros_lenses.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('paperStories slice + intros slices written;', len(new_ids), 'new concept intros;', len(refresh_candidates), 'refresh candidates')
