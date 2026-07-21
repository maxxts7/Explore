"""Stage 34 connective-theme coverage: coordinator design, slice builder, and assertion.

Verifies every staged CAA edge is covered by the design (7 new connective themes +
9 existing themes gaining members), then writes the two slice files the narrative
agents read. Run from graph/.
"""
import json

g = json.load(open('store/graph.json', encoding='utf-8'))
edges = {}
for b in ['p', 'q', 'r', 's']:
    for e in json.load(open(f'staging/stage34-edges-{b}.json', encoding='utf-8'))['edges']:
        edges[e['id']] = e

NEW = {
 'worries-become-dials': {
   'name': 'Named worries become measurable dials',
   'claim': "Failure modes and tensions the earlier papers could only discuss - Goodhart, reward hacking, evasiveness, the helpfulness-harmlessness tension, the shutdown problem, CIRL's off-switch incentives - become quantities with a sign and a magnitude in 2023. Each edge pairs a prose-era worry with the behavioral dial that now measures it.",
   'members': ['sycophancy-instantiates-goodharts-law', 'sycophancy-is-a-behavioral-instance-of-reward-hacking', 'refusal-behavior-generalizes-evasiveness', 'refusal-behavior-quantifies-helpfulness-harmlessness-tension', 'corrigibility-operationalizes-shutdown-problem', 'survival-instinct-behavior-makes-measurable-shutdown-problem', 'corrigibility-tests-the-incentive-formalized-by-cooperative-inverse-reinforcement-learning']},
 'control-moves-into-the-forward-pass': {
   'name': 'Control migrates from training time into the forward pass',
   'claim': "The corpus's earlier levers act on data, labels, and gradients before deployment; these edges trace what changes when the lever moves inside inference - how steering composes with RLHF, prompts, and finetuning, what it costs, and how the capability bill is checked.",
   'members': ['contrastive-activation-addition-operates-on-top-of-rlhf', 'caa-system-prompt-comparison-moves-behavior-beyond-system-prompting', 'caa-finetuning-comparison-runs-head-to-head-against-supervised-fine-tuning', 'caa-finetuning-comparison-isolates-a-generalization-advantage-for-contrastive-activation-addition', 'caa-computational-efficiency-avoids-the-memory-cost-of-supervised-fine-tuning', 'mmlu-sets-the-capability-floor-for-contrastive-activation-addition', 'mmlu-reruns-the-question-behind-alignment-tax']},
 'the-vector-doubles-as-a-probe': {
   'name': 'The steering vector doubles as a measuring instrument',
   'claim': "Every edge here shows the same object read twice: built to control a behavior, the vector also reads structure out of the network - feature detection at tokens, representation emergence across layers, what RLHF changed between base and chat, and what a small perturbation can elicit.",
   'members': ['token-level-cosine-similarity-analysis-reveals-as-a-feature-detector-steering-vector', 'inter-layer-similarity-and-transfer-demonstrates-the-generality-of-caa-steering-vector-construction', 'base-chat-representation-comparison-measures-the-effect-of-rlhf', 'llama-2-chat-is-the-rlhf-tuned-counterpart-of-llama-2', 'behavioral-clustering-localizes-suddenly-in-residual-stream', 'behavioral-clustering-is-evidence-for-linear-representation-hypothesis', 'linear-representation-hypothesis-licenses-the-vector-arithmetic-of-steering-vector', 'caa-red-teaming-application-inverts-the-purpose-of-contrastive-activation-addition']},
 'design-choices-answer-named-predecessors': {
   'name': "Each design choice answers a named predecessor's limit",
   'claim': "Read together, the 2023 method's related-work edges are an itemized reply: dataset averaging answers ActAdd's noise, direct residual-stream access answers ITI's head search, a steering focus answers RepE's reading focus, one layer answers ICV's every-layer spread - and the theory edges show the family's practice preceding its formalization.",
   'members': ['caa-steering-vector-construction-refines-the-single-pair-recipe-of-activation-addition', 'contrastive-activation-addition-skips-the-head-search-required-by-inference-time-intervention', 'contrastive-activation-addition-repurposes-for-steering-relative-to-representation-engineering-zou', 'in-context-vectors-spans-every-layer-unlike-contrastive-activation-addition', 'activation-engineering-empirically-motivated-the-formalization-of-linear-representation-hypothesis', 'linear-representations-of-sentiment-cross-validates-against-pca-for-mean-difference-method']},
 'the-behavior-is-the-dataset': {
   'name': 'A behavior is exactly as good as the dataset that writes it down',
   'claim': "Before a behavior can be steered it must be captured as contrast pairs, and every pathology of the capture becomes a pathology of the behavior: four behaviors ride Anthropic's human-written evaluations, two are GPT-4-manufactured, and the PCA screening and letter-clustering confound are the quality control that decides whether a dataset earned its dial.",
   'members': ['advanced-ai-risk-dataset-supplies-contrast-pairs-for-corrigibility', 'sycophancy-eval-datasets-anthropic-supplies-contrast-pairs-for-sycophancy', 'caa-hallucination-dataset-partitions-into-subtypes-of-hallucination', 'caa-refusal-dataset-supplies-contrast-pairs-for-refusal-behavior', 'gpt-4-authors-caa-refusal-dataset', 'activation-pca-visualization-screens-datasets-for-caa-steering-vector-construction', 'letter-clustering-is-the-confound-for-behavioral-clustering']},
 'one-dial-many-knobs': {
   'name': 'One advertised dial, five interacting knobs',
   'claim': "The advertised interface is one vector and one multiplier; these edges expose the engineering underneath - injection site, dose, cross-behavior normalization, position set - each with its own failure mode, and the paper's future-work items are adjustments to exactly these knobs.",
   'members': ['residual-stream-is-the-injection-site-whose-growth-constrains-contrastive-activation-addition', 'steering-multiplier-sets-the-dose-for-steering-vector', 'steering-vector-normalization-makes-cross-behavior-comparable-for-steering-multiplier', 'targeted-token-steering-would-relax-the-quality-ceiling-of-contrastive-activation-addition', 'steering-outside-residual-stream-would-localize-representations-beyond-residual-stream']},
 'escalating-elicitation': {
   'name': 'From found jailbreaks to systematic elicitation',
   'claim': "Safety training's robustness cannot be read off its outputs; these edges trace the escalation of ways to find what remains latent - jailbreaks users stumble into, red-teaming that hunts deliberately, an LM that writes the attacks, and finally a perturbation that skips the input search entirely.",
   'members': ['jailbreaks-motivates-caa-red-teaming-application', 'jailbreaks-is-the-target-phenomenon-of-red-teaming', 'caa-red-teaming-application-relocates-the-attack-surface-of-red-teaming', 'caa-red-teaming-application-skips-the-prompt-search-of-automated-red-teaming', 'caa-red-teaming-application-inverts-the-purpose-of-contrastive-activation-addition']},
}
UPD = {
 'goodhart-names-itself-across-six-years': ['sycophancy-instantiates-goodharts-law', 'sycophancy-misgeneralizes-the-training-objective-of-rlhf'],
 'calibration-and-prompt-scaffolding': ['multiple-choice-contrast-pair-format-cancels-the-confounders-in-caa-steering-vector-construction', 'multiple-choice-contrast-pair-format-repurposes-the-ab-mechanic-of-multiple-choice-evaluation-format'],
 'ai-substitutes-for-the-human-bottleneck': ['gpt-4-rates-outputs-for-open-ended-generation-evaluation', 'open-ended-generation-evaluation-shares-the-ai-judge-move-with-rlaif', 'gpt-4-authors-caa-refusal-dataset'],
 'one-mechanism-many-jobs': ['mean-difference-method-supplies-the-extraction-rule-for-caa-steering-vector-construction', 'pca-is-the-projection-technique-behind-activation-pca-visualization'],
 'benchmark-reused-with-hidden-alterations': ['sycophancy-is-tested-via-truthfulqa', 'mmlu-sets-the-capability-floor-for-contrastive-activation-addition'],
 'independent-checks-and-instrument-blind-spots': ['open-ended-generation-evaluation-shows-a-different-margin-than-multiple-choice-behavioral-evaluation', 'mmlu-tests-a-different-competence-than-superglue'],
 'ablations-carry-the-design-argument': ['multiple-choice-behavioral-evaluation-supplies-the-layer-hyperparameter-for-contrastive-activation-addition'],
 'hindsight-seams-2016-to-2022': ['few-shot-prompting-shares-its-mechanism-with-gpt3-prompted-baseline'],
 'scale-asymmetry-and-the-ladder-of-baselines': ['few-shot-prompting-loses-out-to-system-prompting'],
}

covered = set()
for spec in NEW.values():
    covered |= set(spec['members'])
for adds in UPD.values():
    covered |= set(adds)
missing = set(edges) - covered
assert not missing, f'uncovered edges: {missing}'
unknown = covered - set(edges)
assert not unknown, f'unknown edge ids in design: {unknown}'

def edge_rec(eid):
    e = edges[eid]
    return {'type': e['type'], 'source': e['source'], 'target': e['target'], 'prose': e['prose']}

slice_new = {
    'designs': NEW,
    'edges': {eid: edge_rec(eid) for spec in NEW.values() for eid in spec['members']},
    'samples': [t for t in g['tissueThemes'] if t['id'] in ('ablations-carry-the-design-argument', 'mirror-image-pairs')],
}
json.dump(slice_new, open('scratch_stage34_tissue_new_slice.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

cur = {t['id']: t for t in g['tissueThemes']}
slice_upd = {
    'themes': {tid: {'name': cur[tid]['name'], 'members': cur[tid]['members'], 'narrative': cur[tid]['narrative']} for tid in UPD},
    'additions': UPD,
    'addedEdges': {eid: edge_rec(eid) for adds in UPD.values() for eid in adds},
}
json.dump(slice_upd, open('scratch_stage34_tissue_upd_slice.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('coverage OK: all', len(edges), 'edges covered; slices written')
print('new themes:', len(NEW), '| updated themes:', len(UPD))
