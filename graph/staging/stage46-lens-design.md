# Stage 46: lens design for the Sparse Autoencoders paper (one mind, coordinator)

Corpus grows 303 → 347 concepts (44 new, stage45-sae-concepts.json). Design decisions
below are final; narrative writing is parallelized within them.

## New themes (9)

1. `unmixing-activations-with-sparsity` — "Unmixing activations with a sparsity penalty"
   Claim: the entire method is one small autoencoder, and every design choice in it —
   tied weights, expansion factor, the L1 coefficient — is a position on a single
   tradeoff between sparsity and reconstruction; the paper concedes there is no single
   correct decomposition, only points on that curve.
   Members: sparse-autoencoders, dictionary-feature, sparsity-loss, reconstruction-loss,
   expansion-factor-r, tied-weights-sae, dead-features, sparsity-reconstruction-tradeoff,
   mlp-sae-training, reconstruction-perplexity-metric, sparse-dictionary-learning (11)

2. `superposition-vs-the-neuron-basis` — "Superposition and the case against the neuron basis"
   Claim: neurons and basis dimensions are the wrong unit of analysis because models pack
   more features than they have dimensions; the paper's premise (superposition →
   polysemanticity) and its baseline results (the default basis scores poorly) are the
   same fact observed twice, with the residual stream's mostly-unprivileged basis and its
   outlier dimensions as the fine print.
   Members: polysemanticity, superposition, monosemanticity, privileged-basis,
   outlier-dimensions, residual-stream, default-basis-baseline,
   mechanistic-interpretability (8)

3. `automated-interpretability-scoring` — "Interpretability itself becomes a benchmark"
   Claim: the paper's headline comparison rests on language models grading language-model
   features — GPT-4 writes the explanation, a simulator predicts activations from it, and
   correlation with reality is the score — plus the controls (top-and-random sampling,
   top-K fairness, the kurtosis/skew correlation) that keep that score honest.
   Members: autointerpretability-score, top-random-scoring, gpt-4, gpt-3-5,
   kurtosis-skew-correlation-analysis, top-k-baseline-control (6)

4. `decomposition-baselines` — "The ladder of decomposition baselines"
   Claim: the sparse autoencoder's win only means something against a ladder of
   alternatives, each embodying a different hypothesis about where features live: the
   default neuron basis (features are neurons), random directions (nowhere in
   particular), PCA (directions of variance), ICA (statistically independent directions).
   Members: pca, ica, random-directions-baseline, default-basis-baseline,
   top-k-baseline-control, sparse-autoencoders (6)

5. `causal-proof-by-patching` — "Features proved by intervention"
   Claim: an interpretable-looking feature earns trust only when editing it changes model
   behavior predictably; the paper ports activation patching to dictionary features,
   shows the edits are finer than rank-one, and builds feature circuits from them —
   including recording the weight-based attempt that failed.
   Members: activation-patching, dictionary-feature-patching, less-than-rank-one-ablation,
   ioi-task, automated-circuit-discovery, feature-circuit-detection,
   weight-based-connection-attempt, closing-parenthesis-feature (8)

6. `single-features-under-the-microscope` — "Single features under the microscope"
   Claim: the method's promise is cashed out in individual case studies read from both
   ends — what makes a feature fire (input) and what it does to the logits (output) —
   with the apostrophe and closing-parenthesis features as the specimens.
   Members: apostrophe-feature, closing-parenthesis-feature, dictionary-feature,
   monosemanticity, feature-circuit-detection (5)

7. `open-models-as-interpretability-testbeds` — "Small open models as interpretability testbeds"
   Claim: the paper's claims are scoped by its instruments — Pythia models on the Pile,
   OpenWebText for activation harvesting — small, open, and cheap enough that full sweeps
   over dictionary sizes and sparsity coefficients are affordable (the corpus parallel is
   deep-rl-testbeds: proof-of-concept scale, honestly labeled).
   Members: pythia, the-pile, openwebtext (3)

8. `dictionary-learning-lineage` — "The dictionary-learning lineage"
   Claim: sparse coding arrives in language-model interpretability from vision and
   neuroscience via two direct predecessors — Yun et al.'s transformer dictionary
   learning and Sharkey et al.'s interim report — so the paper is a scaling-up and
   validation of an existing idea, not an invention from nothing.
   Members: sparse-dictionary-learning, l4-norm-maximization, yun-dictionary-learning,
   sharkey-interim-report (4)

9. `enumerating-features-for-safety` — "Feature enumeration as a safety audit"
   Claim: the paper offers its catalogue of features as a route to model audit —
   enumerative safety — which is the corpus's oversight problem arriving at
   interpretability's door: instead of judging outputs, list and inspect the parts.
   Members: enumerative-safety, mechanistic-interpretability, sparse-autoencoders,
   feature-circuit-detection (4)

Coverage check: all 44 new concepts appear in ≥1 theme (verified at design time).
Ratio: 9 themes / 44 concepts ≈ 1:5 target.

## Changed existing themes (2) — narratives revised, walks nulled

- `reading-the-residual-stream` += privileged-basis, outlier-dimensions.
  Narrative revision: sparse-autoencoders (already a member via PV) is no longer outside
  work — Cunningham et al. 2023 is now in the corpus; the theme now spans three papers
  and gains the basis fine print.
- `steering-as-audit` += enumerative-safety.
  Narrative revision: two audit routes via internals — behavioral elicitation by steering
  (CAA) and structural enumeration of features (2023 SAE paper) — same claim, second leg.

No change needed for gpt-4 (already in judging-steered-outputs) or sparse-autoencoders'
existing membership (already in reading-the-residual-stream).

## New supertheme (1)

`decomposing-the-model-into-features` — "Decomposing the model into features"
Claim: a research program that runs diagnosis → instrument → measurement → causal proof →
safety ambition: superposition says neurons won't do; the sparse autoencoder learns a
better unit; automated scoring judges it; patching proves it causal; enumerative safety
says why it matters — and the program shares its reading-the-internals machinery with the
steering papers.
Members: the 9 new themes + reading-the-residual-stream + steering-as-audit (11).

No membership changes to existing superthemes (the crossing happens through the two
shared themes, which now belong to both steering-and-model-internals and the new
supertheme).

## Paper overlay

7th entry (paper: sparse-autoencoders) + top-narrative refresh — coordinator writes.

## Edge batches (stage 47; pair neighborhoods, agents may drop stretches / add grounded pairs)

- Batch P: method machinery (themes 1 + 8), target ~14
- Batch Q: representational problem + baselines (themes 2 + 4), target ~14
- Batch R: scoring + case studies (themes 3 + 6), target ~14
- Batch S: causal proof + safety + cross-paper (themes 5 + 9 + cross-corpus), target ~15
- Superedges: 1 agent after theme narratives exist; within decomposing-the-model-into-features,
  including stitches through the two dual-membership themes.
