# Stage 39: lens revision for Persona Vectors (coordinator design, one mind)

Paper: persona-vectors (arXiv 2507.21509, 2025). 57 staged concepts (26 introduced /
6 refined / 25 inherited), 42 new concept ids. Ratio target ~1 theme per 5 new
concepts → 8 new themes, 1 new supertheme, membership additions to 6 existing themes,
2 supertheme membership additions.

## New themes (8)

1. id `trait-to-vector-pipeline` — name "From trait name to vector: extraction becomes automatic"
   Claim: what CAA needed hand-built contrast datasets for, one prompt template now
   generates — contrastive system prompts, evaluation questions, judge rubrics, and the
   direction itself — from a plain-language trait description; automation is what makes
   trait-general monitoring and screening possible.
   Members: persona-vector-extraction-pipeline, trait-artifact-generation,
   persona-vector-computation, trait-expression-score, claude-generation-tooling,
   concept-description-to-direction-pipeline-wu

2. id `the-assistant-persona-in-parts` — name "The Assistant persona taken apart into measurable traits"
   Claim: the deployed Assistant character is not a monolith — each trait can be named
   from a description, scored by a judge, and given its own direction; malicious (evil),
   subtle (sycophancy, hallucination) and mundane (optimism, impoliteness, apathy,
   humor) traits all yield to the same machinery.
   Members: persona-vectors, evil-trait, sycophancy, hallucination, optimism-trait,
   impoliteness-trait, apathy-trait, humor-trait

3. id `projection-as-early-warning` — name "Projection as early warning: reading the persona before it speaks"
   Claim: the dot product of activations with a trait direction predicts trait
   expression before generation happens — steering vectors read instead of written —
   turning the same object into a deployment-time monitor for prompt-induced shifts and
   a training-time gauge for weight-induced ones.
   Members: projection-based-persona-monitoring, many-shot-prompting, system-prompting,
   persona-vectors, finetuning-shift, projection-difference

4. id `finetuning-moves-the-persona` — name "Finetuning moves the persona, measurably"
   Claim: training data displaces the model along trait directions; the activation
   shift predicts post-finetuning trait expression, and traits move together
   (cross-trait correlation), which is how narrowly bad data produces broadly
   misaligned models — the 2025 mechanistic handle on emergent misalignment.
   Members: finetuning-shift, cross-trait-persona-correlation-analysis,
   emergent-misalignment, supervised-fine-tuning, trait-eliciting-finetuning-datasets,
   em-like-datasets

5. id `steering-becomes-a-training-tool` — name "Steering grows out of inference time"
   Claim: CAA-style steering was an inference-time patch; the 2025 paper moves the same
   vector into training — canceling acquired drift afterwards (post-hoc), preventing it
   during finetuning (preventative, incl. multi-layer), trading off against
   regularization, prompting, and CAFT baselines — and the fact-acquisition case study
   shows the vaccine does not block learning.
   Members: steering-mitigation-of-finetuning-shifts, post-hoc-steering,
   preventative-steering, preventative-prompting, multi-layer-steering,
   train-time-regularization-baseline, fact-acquisition-case-study, caft

6. id `screening-data-before-training` — name "Catching bad data before it trains anything"
   Claim: because drift is predictable from data alone, the trait direction becomes a
   dataset audit — projection difference flags whole datasets and individual samples,
   validated on real chat data, and catches trait-inducing samples LLM judges pass.
   Members: projection-difference, sample-level-data-filtering,
   real-world-chat-data-validation, lmsys-chat-1m,
   reward-hack-generalization-sycophancy-dataset

7. id `open-subjects-frontier-instruments` — name "Open models as subjects, frontier models as instruments"
   Claim: the 2025 experimental stack divides labor — open 7–8B chat models are the
   experimental subjects whose activations are read and written, while frontier closed
   models generate artifacts and judge outputs; the corpus's testbed lens (MuJoCo/Atari
   2017, GPT-4-judged Llama 2023) arrives at its industrial form.
   Members: qwen2.5-7b-instruct, llama-3.1-8b-instruct, claude-generation-tooling,
   gpt-4.1-mini, lmsys-chat-1m

8. id `engineered-misbehavior-datasets` — name "To study a failure, first cause it: datasets built to corrupt"
   Claim: the paper's experimental design needs models that actually go bad, so it
   builds the corruption — explicit trait-eliciting datasets, realistic EM-like
   datasets with graded Normal/Mistake variants — echoing 2017's hidden-reward
   experimental design: constructing the pathology is part of measuring it.
   Members: trait-eliciting-finetuning-datasets, em-like-datasets,
   reward-hack-generalization-sycophancy-dataset, halueval, emergent-misalignment,
   claude-generation-tooling

## Membership additions to existing themes (6) — walks nulled, narratives revised

- behavior-as-a-direction += persona-vectors, persona-vector-computation
  (response-activation mean difference joins the construction-recipe story; the
  persona vector is the 2025 successor object to CAA's steering vector)
- activation-engineering-family += concept-description-to-direction-pipeline-wu,
  allbert-personality-space, dong-emotion-vectors, security-vectors-zhou, caft
  (the family grows a 2024-25 generation: automated extraction, persona subspaces,
  emotion vectors, security vectors, concept-ablation finetuning)
- judging-steered-outputs += trait-expression-score, coherence-score, gpt-4.1-mini
  (the 2025 judge apparatus: trait score 0-100 + coherence floor, judged by
  GPT-4.1-mini — same behavior-score-plus-capability-floor pattern)
- reading-the-residual-stream += sae-decomposition-of-persona-vectors, sparse-autoencoders
  (steering doubles as interpretability, now with SAE decomposition of the vectors)
- steering-vs-training-levers += preventative-steering, preventative-prompting
  (the levers stop being alternatives: steering applied DURING finetuning, prompts
  applied during training as the ablated variant)
- safety-bias-truthfulness-benchmarks += halueval
  (hallucination operationalized as a benchmark, 2025 addition to the truthfulness row)

## New supertheme (1)

id `managing-the-persona-lifecycle` — name "The persona under management: deployment, training, and the data before it"
Claim: the 2025 paper closes a loop the corpus has been building toward — one
trait direction serves as dial (steering), gauge (projection monitoring), and filter
(data screening), covering the model lifecycle from dataset audit through finetuning
to deployment. Members (all 8 new themes): trait-to-vector-pipeline,
the-assistant-persona-in-parts, projection-as-early-warning,
finetuning-moves-the-persona, steering-becomes-a-training-tool,
screening-data-before-training, open-subjects-frontier-instruments,
engineered-misbehavior-datasets

## Supertheme membership additions (2) — narratives revised

- steering-and-model-internals += steering-becomes-a-training-tool, projection-as-early-warning
- scalable-oversight-to-rlhf-pipeline += finetuning-moves-the-persona

## paperOverlay

Coordinator writes the 6th paper entry (persona-vectors) + refreshes the top
narrative (currently ends at "the 2023 steering paper splits down the middle").

## Downstream obligations this design creates

- Stage 40 edges: pair neighborhoods = the 8 new themes + the 6 changed themes.
- Walk rewrites: 8 new + 6 changed themes.
- Intros: 8 new themes + 1 new supertheme + refreshes for 6 changed themes and
  2 changed superthemes (+ changed-concept intros judged at intros stage).
- paperStories entry for persona-vectors (3 tellings), stage 42.
