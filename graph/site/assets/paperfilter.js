
(function () {
  'use strict';
  var PF = {"papers": [{"id": "concrete-problems", "title": "Concrete Problems in AI Safety", "short": "Concrete Problems"}, {"id": "instructgpt", "title": "Training language models to follow instructions with human feedback", "short": "InstructGPT"}, {"id": "constitutional-ai", "title": "Constitutional AI: Harmlessness from AI Feedback", "short": "Constitutional AI"}, {"id": "deep-rl-human-prefs", "title": "Deep Reinforcement Learning from Human Preferences", "short": "Deep RL from Human Preferences"}], "nodes": {"concept/accidents-in-ml": ["concrete-problems"], "concept/cleaning-robot-example": ["concrete-problems"], "concept/long-term-ai-risk-framing": ["concrete-problems"], "concept/negative-side-effects": ["concrete-problems"], "concept/reward-hacking": ["concrete-problems", "deep-rl-human-prefs"], "concept/scalable-oversight": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs"], "concept/safe-exploration": ["concrete-problems"], "concept/robustness-distributional-shift": ["concrete-problems"], "concept/low-impact-agents": ["concrete-problems"], "concept/frame-problem": ["concrete-problems"], "concept/impact-regularizer": ["concrete-problems"], "concept/learned-impact-regularizer": ["concrete-problems"], "concept/reachability-analysis": ["concrete-problems"], "concept/robust-policy-improvement": ["concrete-problems"], "concept/penalize-influence": ["concrete-problems"], "concept/empowerment": ["concrete-problems"], "concept/multi-agent-approaches": ["concrete-problems"], "concept/cooperative-inverse-reinforcement-learning": ["concrete-problems", "deep-rl-human-prefs"], "concept/shutdown-problem": ["concrete-problems"], "concept/reward-autoencoder": ["concrete-problems"], "concept/reward-uncertainty": ["concrete-problems"], "concept/wireheading": ["concrete-problems"], "concept/partially-observed-goals": ["concrete-problems"], "concept/pomdp-belief-state-mdp": ["concrete-problems"], "concept/complicated-systems": ["concrete-problems"], "concept/abstract-rewards": ["concrete-problems"], "concept/adversarial-examples": ["concrete-problems"], "concept/goodharts-law": ["concrete-problems", "constitutional-ai"], "concept/feedback-loops": ["concrete-problems"], "concept/environmental-embedding": ["concrete-problems"], "concept/evolved-radio-example": ["concrete-problems"], "concept/delusion-box": ["concrete-problems"], "concept/adversarial-reward-functions": ["concrete-problems"], "concept/generative-adversarial-networks": ["concrete-problems"], "concept/model-lookahead": ["concrete-problems"], "concept/adversarial-blinding": ["concrete-problems"], "concept/careful-engineering": ["concrete-problems"], "concept/reward-capping": ["concrete-problems"], "concept/counterexample-resistance": ["concrete-problems"], "concept/multiple-rewards": ["concrete-problems"], "concept/reward-pretraining": ["concrete-problems"], "concept/inverse-reinforcement-learning": ["concrete-problems", "deep-rl-human-prefs"], "concept/variable-indifference": ["concrete-problems"], "concept/trip-wires": ["concrete-problems"], "concept/semi-supervised-reinforcement-learning": ["concrete-problems"], "concept/supervised-reward-learning": ["concrete-problems"], "concept/semi-supervised-active-reward-learning": ["concrete-problems", "deep-rl-human-prefs"], "concept/unsupervised-value-iteration": ["concrete-problems"], "concept/unsupervised-model-learning": ["concrete-problems"], "concept/distant-supervision": ["concrete-problems"], "concept/deepdive": ["concrete-problems"], "concept/hierarchical-reinforcement-learning": ["concrete-problems"], "concept/feudal-reinforcement-learning": ["concrete-problems"], "concept/atari-games-environment": ["concrete-problems", "deep-rl-human-prefs"], "concept/epsilon-greedy": ["concrete-problems"], "concept/r-max": ["concrete-problems"], "concept/risk-sensitive-performance-criteria": ["concrete-problems"], "concept/use-demonstrations": ["concrete-problems"], "concept/apprenticeship-learning": ["concrete-problems"], "concept/simulated-exploration": ["concrete-problems"], "concept/bounded-exploration": ["concrete-problems"], "concept/h-infinity-control": ["concrete-problems"], "concept/trusted-policy-oversight": ["concrete-problems"], "concept/human-oversight-safe-exploration": ["concrete-problems"], "concept/babi-tasks": ["concrete-problems"], "concept/covariate-shift-assumption": ["concrete-problems"], "concept/partially-specified-models": ["concrete-problems"], "concept/generalized-method-of-moments": ["concrete-problems"], "concept/unsupervised-risk-estimation": ["concrete-problems"], "concept/training-multiple-distributions": ["concrete-problems"], "concept/counterfactual-reasoning": ["concrete-problems"], "concept/machine-learning-with-contracts": ["concrete-problems"], "concept/model-repair": ["concrete-problems"], "concept/formal-verification": ["concrete-problems"], "concept/asimovs-first-law": ["concrete-problems"], "concept/privacy-research-area": ["concrete-problems"], "concept/fairness-research-area": ["concrete-problems"], "concept/security-ml": ["concrete-problems"], "concept/abuse-ml": ["concrete-problems"], "concept/transparency-ml": ["concrete-problems"], "concept/policy-ml": ["concrete-problems"], "concept/instructgpt": ["constitutional-ai", "instructgpt"], "concept/gpt-3": ["instructgpt"], "concept/sft-model": ["instructgpt"], "concept/reward-model": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "concept/reward-model-loss": ["instructgpt"], "concept/k-choose-2-batching": ["instructgpt"], "concept/ppo-training": ["instructgpt"], "concept/ppo-model": ["instructgpt"], "concept/ppo-ptx": ["instructgpt"], "concept/kl-penalty": ["instructgpt"], "concept/value-function": ["instructgpt"], "concept/bandit-environment": ["instructgpt"], "concept/generalized-advantage-estimation": ["instructgpt"], "concept/rlhf": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "concept/supervised-fine-tuning": ["instructgpt"], "concept/alignment-tax": ["instructgpt"], "concept/hallucination": ["instructgpt"], "concept/reward-overoptimization": ["instructgpt"], "concept/excessive-hedging": ["instructgpt"], "concept/false-premise-failure": ["instructgpt"], "concept/sft-dataset": ["instructgpt"], "concept/rm-dataset": ["instructgpt"], "concept/ppo-dataset": ["instructgpt"], "concept/api-prompt-distribution": ["instructgpt"], "concept/truthfulqa": ["instructgpt"], "concept/realtoxicityprompts": ["instructgpt"], "concept/winogender": ["instructgpt"], "concept/crows-pairs": ["instructgpt"], "concept/drop": ["instructgpt"], "concept/squadv2": ["instructgpt"], "concept/hellaswag": ["instructgpt"], "concept/quac": ["instructgpt"], "concept/sst": ["instructgpt"], "concept/rte": ["instructgpt"], "concept/wsc": ["instructgpt"], "concept/superglue": ["instructgpt"], "concept/wmt15-fr-en": ["instructgpt"], "concept/cnn-dm-summarization": ["instructgpt"], "concept/reddit-tldr-summarization": ["instructgpt"], "concept/flan": ["instructgpt"], "concept/t0": ["instructgpt"], "concept/gpt3-prompted-baseline": ["instructgpt"], "concept/win-rate": ["instructgpt"], "concept/likert-quality-rating": ["instructgpt"], "concept/labeler-metadata-taxonomy": ["instructgpt"], "concept/perspective-api": ["instructgpt"], "concept/bias-entropy-metric": ["instructgpt"], "concept/rouge-l": ["instructgpt"], "concept/bleu": ["instructgpt"], "concept/f1-score": ["instructgpt"], "concept/inter-annotator-agreement": ["instructgpt"], "concept/hhh-framework": ["constitutional-ai", "instructgpt"], "concept/language-modeling-objective": ["instructgpt"], "concept/instruction-following": ["instructgpt"], "concept/labeler-screening-process": ["instructgpt"], "concept/held-out-labeler-generalization": ["instructgpt"], "concept/labeling-interface": ["instructgpt"], "concept/constitutional-ai": ["constitutional-ai"], "concept/constitution": ["constitutional-ai"], "concept/sl-cai-principles": ["constitutional-ai"], "concept/rl-cai-principles": ["constitutional-ai"], "concept/critique-and-revision": ["constitutional-ai"], "concept/sl-cai": ["constitutional-ai"], "concept/rl-cai": ["constitutional-ai"], "concept/rlaif": ["constitutional-ai"], "concept/feedback-model": ["constitutional-ai"], "concept/hybrid-human-ai-preference-model": ["constitutional-ai"], "concept/helpful-rlhf-model": ["constitutional-ai"], "concept/hh-rlhf-model": ["constitutional-ai"], "concept/chain-of-thought-prompting": ["constitutional-ai"], "concept/lets-think-step-by-step-prompt": ["constitutional-ai"], "concept/multiple-choice-evaluation-format": ["constitutional-ai"], "concept/label-clamping": ["constitutional-ai"], "concept/ensembling-principles": ["constitutional-ai"], "concept/evasiveness": ["constitutional-ai"], "concept/helpfulness-harmlessness-tension": ["constitutional-ai"], "concept/elo-score": ["constitutional-ai", "deep-rl-human-prefs"], "concept/hhh-eval-benchmark": ["constitutional-ai"], "concept/big-bench": ["constitutional-ai"], "concept/model-calibration": ["constitutional-ai"], "concept/absolute-harmfulness-score": ["constitutional-ai"], "concept/red-teaming": ["constitutional-ai"], "concept/automated-red-teaming": ["constitutional-ai"], "concept/palms": ["constitutional-ai"], "concept/lamda": ["constitutional-ai"], "concept/sparrow": ["constitutional-ai"], "concept/context-distillation": ["constitutional-ai"], "concept/sl-cai-few-shot-examples": ["constitutional-ai"], "concept/rl-cai-cot-prompts": ["constitutional-ai"], "concept/direct-revision-ablation": ["constitutional-ai"], "concept/classifying-harmful-behavior-eval": ["constitutional-ai"], "concept/pareto-improvement": ["constitutional-ai"], "concept/iterated-online-training": ["constitutional-ai", "deep-rl-human-prefs"], "concept/async-reward-learning-architecture": ["deep-rl-human-prefs"], "concept/trajectory-segment": ["deep-rl-human-prefs"], "concept/preference-elicitation-protocol": ["deep-rl-human-prefs"], "concept/bradley-terry-model": ["deep-rl-human-prefs"], "concept/reward-predictor-ensemble": ["deep-rl-human-prefs"], "concept/adaptive-l2-regularization": ["deep-rl-human-prefs"], "concept/rater-error-noise-model": ["deep-rl-human-prefs"], "concept/uncertainty-based-query-selection": ["deep-rl-human-prefs"], "concept/label-annealing": ["deep-rl-human-prefs"], "concept/reward-predictor-pretraining": ["deep-rl-human-prefs"], "concept/comparisons-vs-absolute-scores": ["deep-rl-human-prefs"], "concept/clip-length-effects": ["deep-rl-human-prefs"], "concept/synthetic-oracle-feedback": ["deep-rl-human-prefs"], "concept/reward-normalization": ["deep-rl-human-prefs"], "concept/non-stationary-reward-challenge": ["deep-rl-human-prefs"], "concept/environment-modifications-for-preference-learning": ["deep-rl-human-prefs"], "concept/quantitative-qualitative-evaluation": ["deep-rl-human-prefs"], "concept/human-feedback-sample-efficiency": ["deep-rl-human-prefs"], "concept/novel-behavior-training": ["deep-rl-human-prefs"], "concept/hopper-backflip-demonstration": ["deep-rl-human-prefs"], "concept/half-cheetah-one-leg-demonstration": ["deep-rl-human-prefs"], "concept/enduro-keeping-pace-demonstration": ["deep-rl-human-prefs"], "concept/mujoco": ["deep-rl-human-prefs"], "concept/openai-gym": ["deep-rl-human-prefs"], "concept/hopper-task": ["deep-rl-human-prefs"], "concept/half-cheetah-task": ["deep-rl-human-prefs"], "concept/ant-task": ["deep-rl-human-prefs"], "concept/human-feedback-implicit-reward-shaping": ["deep-rl-human-prefs"], "concept/enduro-task": ["deep-rl-human-prefs"], "concept/pong-task": ["deep-rl-human-prefs"], "concept/qbert-task": ["deep-rl-human-prefs"], "concept/a2c": ["deep-rl-human-prefs"], "concept/trpo": ["deep-rl-human-prefs"], "concept/dqn": ["deep-rl-human-prefs"], "concept/imitation-learning": ["deep-rl-human-prefs"], "concept/tamer-framework": ["deep-rl-human-prefs"], "concept/contractor-preference-labeling": ["deep-rl-human-prefs"], "concept/recurrent-reward-model-extension": ["deep-rl-human-prefs"], "concept/expected-value-of-information-query-selection": ["deep-rl-human-prefs"], "concept/compute-vs-human-cost-analysis": ["deep-rl-human-prefs"], "edge/accidents-in-ml-reframes-away-from-long-term-ai-risk-framing": ["concrete-problems"], "edge/cleaning-robot-example-illustrates-every-problem-type-of-accidents-in-ml": ["concrete-problems"], "edge/asimovs-first-law-prefigures-informally-accidents-in-ml": ["concrete-problems"], "edge/frame-problem-supplies-the-classical-diagnosis-for-negative-side-effects": ["concrete-problems"], "edge/negative-side-effects-provokes-an-overcorrecting-first-attempt-in-impact-regularizer": ["concrete-problems"], "edge/impact-regularizer-borrows-its-safe-region-from-reachability-analysis": ["concrete-problems"], "edge/impact-regularizer-borrows-its-improvement-guarantee-from-robust-policy-improvement": ["concrete-problems"], "edge/learned-impact-regularizer-offers-a-transfer-learned-alternative-to-impact-regularizer": ["concrete-problems"], "edge/empowerment-is-minimized-instead-of-maximized-by-penalize-influence": ["concrete-problems"], "edge/low-impact-agents-gets-reinterpreted-as-potential-power-by-penalize-influence": ["concrete-problems"], "edge/reward-uncertainty-trades-penalty-for-uncertainty-relative-to-penalize-influence": ["concrete-problems"], "edge/cooperative-inverse-reinforcement-learning-supplies-a-candidate-mechanism-for-shutdown-problem": ["concrete-problems", "deep-rl-human-prefs"], "edge/cooperative-inverse-reinforcement-learning-inverts-the-legibility-direction-of-reward-autoencoder": ["concrete-problems", "deep-rl-human-prefs"], "edge/multi-agent-approaches-flags-as-exceeding-its-own-frame-shutdown-problem": ["concrete-problems"], "edge/security-ml-is-the-mirror-image-of-abuse-ml": ["concrete-problems"], "edge/privacy-research-area-needs-no-adversary-unlike-security-ml": ["concrete-problems"], "edge/partially-observed-goals-has-an-impractical-theoretical-fix-in-pomdp-belief-state-mdp": ["concrete-problems"], "edge/environmental-embedding-is-the-structural-cause-of-wireheading": ["concrete-problems"], "edge/delusion-box-gives-a-minimal-formal-model-of-environmental-embedding": ["concrete-problems"], "edge/evolved-radio-example-retroactively-exemplifies-complicated-systems": ["concrete-problems"], "edge/wireheading-is-narrower-than-reward-hacking": ["concrete-problems", "deep-rl-human-prefs"], "edge/generative-adversarial-networks-inspires-but-does-not-transfer-cleanly-to-adversarial-reward-functions": ["concrete-problems"], "edge/adversarial-examples-motivates-but-only-partially-covers-counterexample-resistance": ["concrete-problems"], "edge/adversarial-blinding-borrows-from-a-different-adversarial-ml-lineage-than-counterexample-resistance": ["concrete-problems"], "edge/adversarial-reward-functions-operates-at-a-different-layer-than-counterexample-resistance": ["concrete-problems"], "edge/model-lookahead-solves-the-same-problem-by-a-different-route-than-reward-pretraining": ["concrete-problems"], "edge/careful-engineering-is-backstopped-by-trip-wires": ["concrete-problems"], "edge/reward-capping-shares-a-blind-spot-with-multiple-rewards": ["concrete-problems"], "edge/reward-pretraining-is-a-concrete-special-case-of-variable-indifference": ["concrete-problems"], "edge/goodharts-law-is-empirically-instantiated-by-reward-overoptimization": ["concrete-problems", "constitutional-ai", "instructgpt"], "edge/reward-overoptimization-is-preemptively-countered-by-kl-penalty": ["instructgpt"], "edge/goodharts-law-operates-at-the-subfeature-level-in-excessive-hedging": ["concrete-problems", "constitutional-ai", "instructgpt"], "edge/goodharts-law-is-instantiated-through-mislabeled-proxy-in-evasiveness": ["concrete-problems", "constitutional-ai"], "edge/excessive-hedging-is-the-harmlessness-axis-mirror-of-evasiveness": ["constitutional-ai", "instructgpt"], "edge/kl-penalty-was-not-the-fix-applied-to-evasiveness": ["constitutional-ai", "instructgpt"], "edge/use-demonstrations-operationalized-as-supervised-fine-tuning": ["concrete-problems", "instructgpt"], "edge/apprenticeship-learning-borrows-technique-from-inverse-reinforcement-learning": ["concrete-problems", "deep-rl-human-prefs"], "edge/inverse-reinforcement-learning-repurposed-for-use-demonstrations": ["concrete-problems", "deep-rl-human-prefs"], "edge/cooperative-inverse-reinforcement-learning-interactive-counterpart-of-use-demonstrations": ["concrete-problems", "deep-rl-human-prefs"], "edge/sft-dataset-duplication-underlies-early-overfitting-of-sft-model": ["instructgpt"], "edge/epsilon-greedy-contrasts-in-danger-source-with-r-max": ["concrete-problems"], "edge/r-max-targets-the-objective-risk-sensitivity-revises": ["concrete-problems"], "edge/babi-tasks-is-the-benchmarking-template-for-safe-exploration": ["concrete-problems"], "edge/bounded-exploration-borrows-its-worst-case-framing-from-h-infinity-control": ["concrete-problems"], "edge/trusted-policy-oversight-operationalizes-the-recoverability-check-in-bounded-exploration": ["concrete-problems"], "edge/human-oversight-safe-exploration-scalability-limit-motivates-trusted-policy-oversight": ["concrete-problems"], "edge/use-demonstrations-supplies-the-baseline-that-anchors-bounded-exploration": ["concrete-problems"], "edge/covariate-shift-assumption-untestability-motivates-retreat-to-partially-specified-models": ["concrete-problems"], "edge/generalized-method-of-moments-generalizes-the-founding-example-of-partially-specified-models": ["concrete-problems"], "edge/unsupervised-risk-estimation-partially-specifies-error-not-parameters-partially-specified-models": ["concrete-problems"], "edge/covariate-shift-assumption-single-invariant-contrasts-with-training-multiple-distributions": ["concrete-problems"], "edge/generalized-method-of-moments-diverges-in-target-from-unsupervised-risk-estimation": ["concrete-problems"], "edge/counterfactual-reasoning-is-the-descriptive-counterpart-to-machine-learning-with-contracts": ["concrete-problems"], "edge/machine-learning-with-contracts-is-restored-post-hoc-by-model-repair": ["concrete-problems"], "edge/machine-learning-with-contracts-reframes-as-a-specification-failure-robustness-distributional-shift": ["concrete-problems"], "edge/reachability-analysis-supplies-the-safe-set-that-bounds-robust-policy-improvement": ["concrete-problems"], "edge/h-infinity-control-reaches-the-same-envelope-by-a-different-route-than-reachability-analysis": ["concrete-problems"], "edge/formal-verification-supplies-the-rigor-asimov-lacked-asimovs-first-law": ["concrete-problems"], "edge/model-repair-is-the-ex-post-counterpart-to-reachability-analysis": ["concrete-problems"], "edge/scalable-oversight-is-operationalized-as-semi-supervised-reinforcement-learning": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs"], "edge/supervised-reward-learning-is-extended-by-semi-supervised-active-reward-learning": ["concrete-problems", "deep-rl-human-prefs"], "edge/unsupervised-value-iteration-extracts-a-complementary-signal-to-supervised-reward-learning": ["concrete-problems"], "edge/unsupervised-value-iteration-is-mirrored-in-model-based-form-by-unsupervised-model-learning": ["concrete-problems"], "edge/atari-games-environment-is-the-proposed-testbed-for-semi-supervised-reinforcement-learning": ["concrete-problems", "deep-rl-human-prefs"], "edge/distant-supervision-is-instantiated-by-deepdive": ["concrete-problems"], "edge/hierarchical-reinforcement-learning-traces-its-lineage-to-feudal-reinforcement-learning": ["concrete-problems"], "edge/distant-supervision-offers-a-structurally-different-route-than-hierarchical-reinforcement-learning": ["concrete-problems"], "edge/scalable-oversight-is-addressed-by-adapting-distant-supervision": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs"], "edge/scalable-oversight-is-addressed-by-hierarchical-reinforcement-learning": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs"], "edge/scalable-oversight-is-retroactively-operationalized-by-reward-model": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "edge/reward-model-anchors-the-reward-signal-of-rlhf": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "edge/rlhf-swaps-the-labeler-in-rlaif": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "edge/rlaif-delegates-harmlessness-comparisons-to-feedback-model": ["constitutional-ai"], "edge/feedback-model-supplies-the-harmlessness-half-of-hybrid-human-ai-preference-model": ["constitutional-ai"], "edge/rlaif-makes-newly-automatable-iterated-online-training": ["constitutional-ai", "deep-rl-human-prefs"], "edge/language-modeling-objective-is-argued-to-be-misaligned-with-instruction-following": ["instructgpt"], "edge/t0-is-scaled-to-match-flan": ["instructgpt"], "edge/flan-sets-the-comparison-floor-for-instruction-following": ["instructgpt"], "edge/gpt3-prompted-baseline-shows-the-limits-of-prompting-alone-for-instruction-following": ["instructgpt"], "edge/hhh-framework-is-operationalized-as-hhh-eval-benchmark": ["constitutional-ai", "instructgpt"], "edge/hhh-eval-benchmark-is-hosted-as-a-subset-of-big-bench": ["constitutional-ai"], "edge/model-calibration-is-empirically-verified-on-hhh-eval-benchmark": ["constitutional-ai"], "edge/instructgpt-outperforms-at-100x-smaller-scale-gpt-3": ["constitutional-ai", "instructgpt"], "edge/reward-model-back-selects-the-checkpoint-of-sft-model": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "edge/sft-model-anchors-as-both-init-and-reference-for-ppo-training": ["instructgpt"], "edge/reward-model-loss-under-determines-the-scale-of-reward-model": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "edge/reward-model-supervises-from-below-ppo-training": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "edge/ppo-ptx-outperforms-tightening-of-kl-penalty": ["instructgpt"], "edge/ppo-ptx-diverges-only-off-distribution-from-ppo-model": ["instructgpt"], "edge/bandit-environment-renders-discounting-moot-in-generalized-advantage-estimation": ["instructgpt"], "edge/kl-penalty-densifies-the-terminal-reward-of-bandit-environment": ["instructgpt"], "edge/sft-dataset-bootstrapped-the-existence-of-api-prompt-distribution": ["instructgpt"], "edge/sft-dataset-trains-the-policies-sampled-for-rm-dataset": ["instructgpt"], "edge/labeler-screening-process-creates-the-question-answered-by-held-out-labeler-generalization": ["instructgpt"], "edge/inter-annotator-agreement-was-both-filter-and-audit-for-labeler-screening-process": ["instructgpt"], "edge/labeling-interface-filters-uncertain-comparisons-out-of-rm-dataset": ["instructgpt"], "edge/api-prompt-distribution-supplies-label-free-scale-to-ppo-dataset": ["instructgpt"], "edge/reward-overoptimization-surfaces-as-excessive-hedging": ["instructgpt"], "edge/excessive-hedging-shares-a-fix-but-not-a-cause-with-false-premise-failure": ["instructgpt"], "edge/reward-overoptimization-demands-a-different-mitigation-than-alignment-tax": ["instructgpt"], "edge/hallucination-sits-in-tension-with-excessive-hedging": ["instructgpt"], "edge/inter-annotator-agreement-caps-the-resolution-of-win-rate": ["instructgpt"], "edge/likert-quality-rating-corroborates-win-rate": ["instructgpt"], "edge/elo-score-generalizes-win-rate": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "edge/absolute-harmfulness-score-cross-checks-elo-score": ["constitutional-ai", "deep-rl-human-prefs"], "edge/f1-score-diverges-under-rlhf-from-win-rate": ["instructgpt"], "edge/squadv2-forms-the-regression-testbed-with-drop": ["instructgpt"], "edge/hellaswag-escapes-the-regression-that-persists-in-drop": ["instructgpt"], "edge/wsc-departs-from-the-canonical-format-of-superglue": ["instructgpt"], "edge/cnn-dm-summarization-duplicates-the-reported-results-of-reddit-tldr-summarization": ["instructgpt"], "edge/wmt15-fr-en-bears-the-alignment-tax-that-spares-reddit-tldr-summarization": ["instructgpt"], "edge/perspective-api-supplies-the-ground-truth-for-realtoxicityprompts": ["instructgpt"], "edge/bias-entropy-metric-recasts-the-task-of-winogender": ["instructgpt"], "edge/bias-entropy-metric-strips-the-direction-from-crows-pairs": ["instructgpt"], "edge/realtoxicityprompts-diverges-under-respectful-prompting-from-winogender": ["instructgpt"], "edge/helpfulness-harmlessness-tension-collapses-into-evasiveness": ["constitutional-ai"], "edge/helpful-rlhf-model-traces-the-tradeoff-curve-with-hh-rlhf-model": ["constitutional-ai"], "edge/rl-cai-eliminates-evasiveness": ["constitutional-ai"], "edge/rl-cai-produces-pareto-improvement": ["constitutional-ai"], "edge/elo-score-was-tuned-to-penalize-evasiveness": ["constitutional-ai", "deep-rl-human-prefs"], "edge/constitution-replaces-human-harm-labels-in-constitutional-ai": ["constitutional-ai"], "edge/critique-and-revision-supplies-the-finetuning-data-for-sl-cai": ["constitutional-ai"], "edge/sl-cai-few-shot-examples-prevents-role-confusion-in-critique-and-revision": ["constitutional-ai"], "edge/direct-revision-ablation-tests-the-necessity-of-critique-in-critique-and-revision": ["constitutional-ai"], "edge/ensembling-principles-diversifies-use-of-sl-cai-principles": ["constitutional-ai"], "edge/sl-cai-principles-is-mirrored-in-a-different-shape-by-rl-cai-principles": ["constitutional-ai"], "edge/chain-of-thought-prompting-creates-the-overconfidence-that-necessitates-label-clamping": ["constitutional-ai"], "edge/model-calibration-is-the-precondition-for-multiple-choice-evaluation-format": ["constitutional-ai"], "edge/lets-think-step-by-step-prompt-is-paired-with-rl-cai-cot-prompts": ["constitutional-ai"], "edge/multiple-choice-evaluation-format-turns-into-a-preference-labeler-feedback-model": ["constitutional-ai"], "edge/ensembling-principles-makes-more-robust-feedback-model": ["constitutional-ai"], "edge/red-teaming-is-the-manual-process-that-scales-into-automated-red-teaming": ["constitutional-ai"], "edge/red-teaming-supplies-the-transcripts-for-classifying-harmful-behavior-eval": ["constitutional-ai"], "edge/palms-provides-an-independent-check-outside-red-teaming": ["constitutional-ai"], "edge/lamda-plays-a-different-comparative-role-than-sparrow": ["constitutional-ai"], "edge/sl-cai-seeds-the-policy-and-comparison-data-for-rl-cai": ["constitutional-ai"], "edge/trajectory-segment-supplies-the-comparison-unit-for-preference-elicitation-protocol": ["deep-rl-human-prefs"], "edge/bradley-terry-model-supplies-the-loss-for-reward-model": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "edge/rater-error-noise-model-corrects-the-asymptotics-of-bradley-terry-model": ["deep-rl-human-prefs"], "edge/reward-predictor-ensemble-supplies-the-disagreement-signal-for-uncertainty-based-query-selection": ["deep-rl-human-prefs"], "edge/iterated-online-training-is-the-cause-of-non-stationary-reward-challenge": ["constitutional-ai", "deep-rl-human-prefs"], "edge/adaptive-l2-regularization-bounds-the-generalization-gap-of-reward-model": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "edge/reward-predictor-pretraining-solves-the-cold-start-problem-of-async-reward-learning-architecture": ["deep-rl-human-prefs"], "edge/label-annealing-paces-the-query-rate-within-iterated-online-training": ["constitutional-ai", "deep-rl-human-prefs"], "edge/reward-normalization-fixes-the-underdetermined-scale-of-reward-model": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "edge/comparisons-vs-absolute-scores-swaps-in-regression-in-place-of-bradley-terry-model": ["deep-rl-human-prefs"], "edge/iterated-online-training-guards-against-reward-hacking": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs"], "edge/async-reward-learning-architecture-gives-concrete-shape-to-rlhf": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "edge/recurrent-reward-model-extension-would-generalize-the-fixed-window-of-reward-model": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "edge/elo-score-supplies-the-explanatory-analogy-for-bradley-terry-model": ["constitutional-ai", "deep-rl-human-prefs"], "edge/trajectory-segment-is-summed-without-discount-by-bradley-terry-model": ["deep-rl-human-prefs"], "edge/clip-length-effects-calibrates-the-length-of-trajectory-segment": ["deep-rl-human-prefs"], "edge/uncertainty-based-query-selection-is-a-crude-approximation-of-expected-value-of-information-query-selection": ["deep-rl-human-prefs"], "edge/contractor-preference-labeling-grounds-the-headline-efficiency-claim-of-human-feedback-sample-efficiency": ["deep-rl-human-prefs"], "edge/compute-vs-human-cost-analysis-caps-the-marginal-value-of-human-feedback-sample-efficiency": ["deep-rl-human-prefs"], "edge/synthetic-oracle-feedback-is-only-realizable-within-quantitative-qualitative-evaluation": ["deep-rl-human-prefs"], "edge/environment-modifications-for-preference-learning-exempts-pong-from-synthetic-oracle-feedback": ["deep-rl-human-prefs"], "edge/ant-task-hard-codes-an-upright-priority-into-contractor-preference-labeling": ["deep-rl-human-prefs"], "edge/enduro-task-supplies-the-hard-exploration-case-for-human-feedback-implicit-reward-shaping": ["deep-rl-human-prefs"], "edge/pong-task-provides-the-canonical-instance-of-reward-hacking": ["concrete-problems", "deep-rl-human-prefs"], "edge/clip-length-effects-predicts-but-was-never-tested-on-qbert-task": ["deep-rl-human-prefs"], "edge/hopper-task-exposes-the-scheduling-fragility-of-contractor-preference-labeling": ["deep-rl-human-prefs"], "edge/synthetic-oracle-feedback-reveals-a-non-human-instance-of-human-feedback-implicit-reward-shaping": ["deep-rl-human-prefs"], "edge/label-annealing-is-only-approximated-under-contractor-preference-labeling": ["deep-rl-human-prefs"], "edge/half-cheetah-task-was-exempted-from-contractor-preference-labeling": ["deep-rl-human-prefs"], "edge/non-stationary-reward-challenge-motivates-the-choice-of-a2c": ["deep-rl-human-prefs"], "edge/non-stationary-reward-challenge-forces-an-entropy-bonus-increase-in-trpo": ["deep-rl-human-prefs"], "edge/non-stationary-reward-challenge-resurfaces-under-iteration-in-ppo-training": ["deep-rl-human-prefs", "instructgpt"], "edge/a2c-closes-its-enduro-exploration-gap-with-dqn": ["deep-rl-human-prefs"], "edge/hopper-backflip-demonstration-extends-past-the-hand-engineerable-reward-of-hopper-task": ["deep-rl-human-prefs"], "edge/enduro-keeping-pace-demonstration-inverts-the-scoring-objective-of-enduro-task": ["deep-rl-human-prefs"], "edge/human-feedback-implicit-reward-shaping-becomes-the-only-signal-in-novel-behavior-training": ["deep-rl-human-prefs"], "edge/half-cheetah-one-leg-demonstration-costs-barely-more-in-queries-than-half-cheetah-task": ["deep-rl-human-prefs"], "edge/reward-model-is-overbuilt-in-anticipation-of-novel-behavior-training": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "edge/reward-normalization-is-reverse-engineered-to-avoid-retuning-a2c": ["deep-rl-human-prefs"], "edge/semi-supervised-active-reward-learning-gets-its-first-deep-rl-implementation-in-uncertainty-based-query-selection": ["concrete-problems", "deep-rl-human-prefs"], "edge/use-demonstrations-is-explicitly-passed-over-in-favor-of-preference-elicitation-protocol": ["concrete-problems", "deep-rl-human-prefs"], "edge/contractor-preference-labeling-becomes-a-screened-operation-in-labeler-screening-process": ["deep-rl-human-prefs", "instructgpt"], "edge/contractor-preference-labeling-is-formalized-as-labeling-interface": ["deep-rl-human-prefs", "instructgpt"], "edge/bradley-terry-model-is-carried-over-unchanged-into-reward-model-loss": ["deep-rl-human-prefs", "instructgpt"], "edge/async-reward-learning-architecture-trades-its-concurrency-for-a-fixed-dataset-in-reward-model": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "edge/cooperative-inverse-reinforcement-learning-is-narrowed-to-a-preferences-only-channel-in-preference-elicitation-protocol": ["concrete-problems", "deep-rl-human-prefs"], "edge/pong-task-anticipates-reward-overoptimization": ["deep-rl-human-prefs", "instructgpt"], "edge/quantitative-qualitative-evaluation-prefigures-instruction-following": ["deep-rl-human-prefs", "instructgpt"], "edge/rater-error-noise-model-assumes-a-constant-later-measured-by-inter-annotator-agreement": ["deep-rl-human-prefs", "instructgpt"], "edge/preference-elicitation-protocol-avoids-the-overfitting-problem-solved-by-k-choose-2-batching": ["deep-rl-human-prefs", "instructgpt"], "edge/reward-normalization-prefigures-the-scale-fix-in-reward-model-loss": ["deep-rl-human-prefs", "instructgpt"], "edge/trajectory-segment-generalizes-into-rm-dataset": ["deep-rl-human-prefs", "instructgpt"], "theme/framing-accidents-vs-speculative-risk": ["concrete-problems"], "theme/impact-regularization-and-baselines": ["concrete-problems"], "theme/influence-and-uncertainty-side-effect-mitigation": ["concrete-problems"], "theme/side-effects-as-relationship": ["concrete-problems", "deep-rl-human-prefs"], "theme/reward-hacking-causes": ["concrete-problems", "deep-rl-human-prefs"], "theme/adversarial-ml-for-reward-hacking": ["concrete-problems"], "theme/reward-hacking-engineering-remedies": ["concrete-problems"], "theme/goodhart-across-corpus": ["concrete-problems", "constitutional-ai", "instructgpt"], "theme/demonstrations-not-specification": ["concrete-problems", "deep-rl-human-prefs", "instructgpt"], "theme/exploration-risk-criteria-and-algorithms": ["concrete-problems"], "theme/constraining-exploration-to-safe-regions": ["concrete-problems"], "theme/statistical-relaxations-for-distributional-shift": ["concrete-problems"], "theme/shift-as-contracts-and-causation": ["concrete-problems"], "theme/formal-methods-imported": ["concrete-problems"], "theme/adjacent-research-areas": ["concrete-problems"], "theme/semi-supervised-reward-learning-proposals": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs"], "theme/distant-supervision-and-hierarchical-decomposition": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs"], "theme/scalable-oversight-lineage": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "theme/rlhf-three-step-pipeline": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "theme/ppo-optimization-mechanics": ["instructgpt"], "theme/human-feedback-data-infrastructure": ["deep-rl-human-prefs", "instructgpt"], "theme/rlhf-failure-modes": ["instructgpt"], "theme/quality-measurement-methods": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "theme/language-understanding-benchmarks": ["instructgpt"], "theme/generation-benchmarks-translation-summarization": ["instructgpt"], "theme/safety-bias-truthfulness-benchmarks": ["instructgpt"], "theme/instruction-following-objective": ["instructgpt"], "theme/hhh-framework-and-benchmark": ["constitutional-ai", "instructgpt"], "theme/helpfulness-harmlessness-tradeoff": ["constitutional-ai", "deep-rl-human-prefs"], "theme/cai-core-method": ["constitutional-ai"], "theme/feedback-model-engineering": ["constitutional-ai"], "theme/red-teaming-and-harm-data": ["constitutional-ai"], "theme/related-dialogue-agents": ["constitutional-ai"], "theme/learning-rewards-from-comparisons": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "theme/keeping-reward-models-on-distribution": ["constitutional-ai", "deep-rl-human-prefs"], "theme/economics-of-human-feedback": ["deep-rl-human-prefs"], "theme/hidden-reward-experimental-design": ["deep-rl-human-prefs"], "theme/deep-rl-testbeds": ["concrete-problems", "deep-rl-human-prefs"], "theme/novel-behaviors-without-reward-functions": ["deep-rl-human-prefs"], "theme/policy-optimization-under-learned-rewards": ["deep-rl-human-prefs", "instructgpt"], "theme/prior-human-in-the-loop-rl": ["concrete-problems", "deep-rl-human-prefs"], "supertheme/bounding-impact-and-exploration": ["concrete-problems", "deep-rl-human-prefs", "instructgpt"], "supertheme/reward-hacking-and-goodharts-law": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "supertheme/scalable-oversight-to-rlhf-pipeline": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "supertheme/distributional-shift-responses": ["concrete-problems"], "supertheme/concrete-problems-scope-and-toolkit": ["concrete-problems"], "supertheme/measuring-instructgpt-quality-and-safety": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "supertheme/defining-the-alignment-target": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "supertheme/constitutional-ai-method-and-grounding": ["constitutional-ai", "instructgpt"], "supertheme/deep-rl-from-preferences-proof-of-concept": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "superedge/exploration-bounding-reaches-same-envelope-as-impact-regularization": ["concrete-problems"], "superedge/cirl-interactive-counterpart-to-demonstration-bounded-exploration": ["concrete-problems", "deep-rl-human-prefs"], "superedge/cirl-relational-half-left-behind-by-sft-genealogy": ["concrete-problems", "deep-rl-human-prefs", "instructgpt"], "superedge/demonstrations-only-bounding-mechanism-to-persist-into-sft": ["concrete-problems", "deep-rl-human-prefs", "instructgpt"], "superedge/causes-supply-exploit-surface-for-adversarial-ml": ["concrete-problems", "deep-rl-human-prefs"], "superedge/causes-supply-weak-points-for-engineering-remedies": ["concrete-problems", "deep-rl-human-prefs"], "superedge/adversarial-ml-needs-a-more-powerful-referee": ["concrete-problems"], "superedge/kl-penalty-automates-capping-and-indifference": ["concrete-problems", "constitutional-ai", "instructgpt"], "superedge/feedback-loops-is-a-special-case-of-goodhart": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "superedge/semi-supervised-reward-learning-proposals-selectively-realized-in-scalable-oversight-lineage": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "superedge/distant-supervision-and-hierarchical-decomposition-prefigures-rule-driven-labeling-in-scalable-oversight-lineage": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "superedge/demonstrations-not-specification-displaces-exploration-bound-onto-ppo-optimization-mechanics": ["concrete-problems", "deep-rl-human-prefs", "instructgpt"], "superedge/ppo-optimization-mechanics-reveals-critic-reward-coupling-in-rlhf-three-step-pipeline": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "superedge/human-feedback-data-infrastructure-exposes-noisy-consensus-beneath-rlhf-three-step-pipeline": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "superedge/ppo-optimization-mechanics-engineers-partial-countermeasure-for-rlhf-failure-modes": ["instructgpt"], "superedge/scalable-oversight-lineage-only-half-operationalized-by-rlhf-three-step-pipeline": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "superedge/statistical-relaxations-for-distributional-shift-is-not-yet-combined-with-formal-methods-imported": ["concrete-problems"], "superedge/statistical-relaxations-for-distributional-shift-supplies-a-route-into-shift-as-contracts-and-causation": ["concrete-problems"], "superedge/formal-methods-imported-contributes-its-one-post-hoc-tool-to-shift-as-contracts-and-causation": ["concrete-problems"], "superedge/framing-accidents-vs-speculative-risk-polices-a-different-boundary-than-adjacent-research-areas": ["concrete-problems"], "superedge/framing-accidents-vs-speculative-risk-shares-its-discarded-foil-with-formal-methods-imported": ["concrete-problems"], "superedge/generation-benchmarks-resist-mitigation-alongside-language-understanding-benchmarks": ["instructgpt"], "superedge/safety-bias-truthfulness-benchmarks-falls-outside-the-taxonomy-of-quality-measurement-methods": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "superedge/quality-measurement-methods-instruments-only-the-extractive-half-of-language-understanding-benchmarks": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "superedge/instruction-following-objective-adopts-the-vocabulary-of-hhh-framework-and-benchmark": ["constitutional-ai", "instructgpt"], "superedge/hhh-framework-and-benchmark-narrows-to-two-of-its-three-terms-in-helpfulness-harmlessness-tradeoff": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "superedge/quality-measurement-methods-supplies-the-frontier-tracking-instrument-for-helpfulness-harmlessness-tradeoff": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "superedge/quality-measurement-methods-adjudicates-the-baseline-comparison-in-instruction-following-objective": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "superedge/red-teaming-sources-the-prompts-critique-and-revision-runs-on": ["constitutional-ai"], "superedge/red-teaming-pool-expands-to-feed-the-feedback-model": ["constitutional-ai"], "superedge/principle-ensembling-flips-payoff-across-stages": ["constitutional-ai"], "superedge/hhh-benchmark-motivates-then-verifies-the-feedback-model": ["constitutional-ai", "instructgpt"], "superedge/feedback-economics-underwrites-choosing-comparisons": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "superedge/reward-model-on-distribution-shares-non-stationarity-with-policy-optimization": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "superedge/hidden-reward-design-licenses-results-of-testbeds": ["concrete-problems", "deep-rl-human-prefs"], "superedge/testbeds-repurposes-environments-for-novel-behaviors": ["concrete-problems", "deep-rl-human-prefs"], "superedge/prior-hitl-rl-finds-missing-piece-in-comparisons": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "superedge/prior-hitl-rl-fails-budget-test-set-by-feedback-economics": ["concrete-problems", "deep-rl-human-prefs"], "superedge/learning-rewards-from-comparisons-scales-binary-comparison-into-rankings-in-rlhf-three-step-pipeline": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "superedge/learning-rewards-from-comparisons-assumes-error-rate-later-measured-in-human-feedback-data-infrastructure": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "superedge/keeping-reward-models-on-distribution-trades-online-refresh-for-kl-penalty-in-ppo-optimization-mechanics": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "superedge/economics-of-human-feedback-supplies-cost-argument-behind-human-feedback-data-infrastructure": ["deep-rl-human-prefs", "instructgpt"], "superedge/economics-of-human-feedback-prices-implicit-budget-of-semi-supervised-reward-learning-proposals": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs"], "superedge/keeping-reward-models-on-distribution-leaves-safeguards-outside-scalable-oversight-lineage": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "tissue/goodhart-names-itself-across-six-years": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "tissue/mirror-image-pairs": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "tissue/remedies-assembled-from-borrowed-adapted-pieces": ["concrete-problems"], "tissue/cross-disciplinary-imports-partial-fit": ["concrete-problems"], "tissue/forked-paths-same-vulnerability": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs"], "tissue/ex-ante-ex-post-contracts": ["concrete-problems"], "tissue/paper-concedes-its-own-remedies-limits": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "tissue/partial-specification-family-different-targets": ["concrete-problems"], "tissue/benchmark-reused-with-hidden-alterations": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "tissue/benchmarks-promoted-to-tuning-target": ["instructgpt"], "tissue/ppo-objective-as-interacting-knobs": ["instructgpt"], "tissue/independent-checks-and-instrument-blind-spots": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "tissue/evasiveness-empirical-arc": ["constitutional-ai", "deep-rl-human-prefs"], "tissue/one-mechanism-many-jobs": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs"], "tissue/calibration-and-prompt-scaffolding": ["constitutional-ai"], "tissue/ai-substitutes-for-the-human-bottleneck": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "tissue/concrete-instances-carry-more-or-less-weight-than-intended": ["concrete-problems", "instructgpt"], "tissue/scalable-oversight-operationalized-into-combinable-machinery": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "tissue/assembly-line-pipeline": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "tissue/scale-asymmetry-and-the-ladder-of-baselines": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "tissue/pipeline-artifacts-double-duty-or-loop-backward": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "tissue/scope-boundaries-what-the-paper-deliberately-excludes": ["concrete-problems", "deep-rl-human-prefs"], "tissue/precursors-old-ideas-resurface": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "tissue/hindsight-seams-2016-to-2022": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "tissue/fix-lives-upstream-in-the-data": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "tissue/list-invites-conflation-but-roles-differ": ["concrete-problems", "constitutional-ai"], "tissue/baseline-anchors-later-exploration": ["concrete-problems", "instructgpt"], "tissue/optimal-for-the-wrong-objective": ["concrete-problems", "deep-rl-human-prefs", "instructgpt"], "tissue/ablations-carry-the-design-argument": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "tissue/primitive-parts-acquire-industrial-replacements": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "tissue/downstream-of-a-moving-reward": ["concrete-problems", "constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "tissue/what-comparisons-leave-undetermined": ["constitutional-ai", "deep-rl-human-prefs", "instructgpt"], "tissue/human-fingerprints-in-the-learning-curve": ["deep-rl-human-prefs"], "story/concrete-problems": ["concrete-problems"], "story/deep-rl-human-prefs": ["deep-rl-human-prefs"], "story/instructgpt": ["instructgpt"], "story/constitutional-ai": ["constitutional-ai"]}};
  var KEY = 'pf-excluded-papers';
  var NODE_RE = /\/(concept|edge|theme|supertheme|superedge|tissue|story)\/([^\/]+)\.html$/;
  var KIND_LABEL = {
    concept: 'concept', edge: 'edge', theme: 'theme',
    supertheme: 'supertheme', superedge: 'super edge', tissue: 'connective theme',
    story: 'story page'
  };
  var validIds = PF.papers.map(function (p) { return p.id; });

  function loadExcluded() {
    try {
      var raw = JSON.parse(localStorage.getItem(KEY) || '[]');
      if (!Array.isArray(raw)) return [];
      return raw.filter(function (id) { return validIds.indexOf(id) !== -1; });
    } catch (e) { return []; }
  }
  function saveExcluded(list) {
    try { localStorage.setItem(KEY, JSON.stringify(list)); } catch (e) {}
  }

  var excluded = loadExcluded();

  function isPaperOff(pid) { return excluded.indexOf(pid) !== -1; }
  function isNodeOff(key) {
    var papers = PF.nodes[key];
    if (!papers || !papers.length) return false;
    for (var i = 0; i < papers.length; i++) {
      if (!isPaperOff(papers[i])) return false;
    }
    return true;
  }
  function nodeKeyFromHref(a) {
    var url;
    try { url = new URL(a.getAttribute('href'), window.location.href); }
    catch (e) { return null; }
    if (url.origin !== window.location.origin) return null;
    var m = NODE_RE.exec(url.pathname);
    return m ? m[1] + '/' + decodeURIComponent(m[2]) : null;
  }
  function currentNodeKey() {
    var m = NODE_RE.exec(window.location.pathname);
    return m ? m[1] + '/' + decodeURIComponent(m[2]) : null;
  }
  function paperById(pid) {
    for (var i = 0; i < PF.papers.length; i++) {
      if (PF.papers[i].id === pid) return PF.papers[i];
    }
    return null;
  }

  // ---- dim links to excluded nodes (every page) -------------------------

  function applyLinks() {
    Array.prototype.forEach.call(document.querySelectorAll('a[href]'), function (a) {
      var key = nodeKeyFromHref(a);
      var off = !!key && isNodeOff(key);
      a.classList.toggle('pf-dim', off);
      if (off) {
        a.setAttribute('title', 'From an excluded paper');
        a.setAttribute('data-pf-titled', '1');
      } else if (a.getAttribute('data-pf-titled')) {
        a.removeAttribute('title');
        a.removeAttribute('data-pf-titled');
      }
    });
  }

  function firstNodeLink(el) {
    var as = el.querySelectorAll('a[href]');
    for (var i = 0; i < as.length; i++) {
      var key = nodeKeyFromHref(as[i]);
      if (key) return key;
    }
    return null;
  }

  // ---- dim tree nodes / walk steps whose lead node is excluded ----------

  function applyContainers() {
    var sel = 'details.tree-node, li.walk-step, li.tree-leaf';
    Array.prototype.forEach.call(document.querySelectorAll(sel), function (el) {
      var key;
      if (el.tagName === 'DETAILS') {
        var summary = el.querySelector('summary');
        key = summary ? firstNodeLink(summary) : null;
      } else {
        key = firstNodeLink(el);
      }
      el.classList.toggle('pf-dim', !!key && isNodeOff(key));
    });
  }

  // ---- hide excluded nodes from the index listing tabs -------------------

  function applyIndexLists() {
    ['tab-superthemes', 'tab-tissue', 'tab-concepts'].forEach(function (pid) {
      var panel = document.getElementById(pid);
      if (!panel) return;
      var lis = panel.querySelectorAll('li');
      Array.prototype.forEach.call(lis, function (li) {
        var key = firstNodeLink(li);
        li.classList.toggle('pf-hide', !!key && isNodeOff(key));
      });
      Array.prototype.forEach.call(panel.querySelectorAll('h3.letter-head'), function (h) {
        var ul = h.nextElementSibling;
        var any = ul && ul.querySelector('li:not(.pf-hide)');
        h.classList.toggle('pf-hide', !any);
        if (ul) ul.classList.toggle('pf-hide', !any);
      });
      var anyVisible = false;
      for (var i = 0; i < lis.length; i++) {
        if (!lis[i].classList.contains('pf-hide')) { anyVisible = true; break; }
      }
      var note = panel.querySelector('.pf-empty');
      if (!anyVisible && lis.length) {
        if (!note) {
          note = document.createElement('p');
          note.className = 'pf-empty section-note';
          note.textContent = 'Nothing to show — every paper is excluded. ' +
            'Re-include papers in the Papers tab.';
          panel.appendChild(note);
        }
        note.classList.remove('pf-hide');
      } else if (note) {
        note.classList.add('pf-hide');
      }
    });
  }

  // ---- papers tab: toggle cards + collapse excluded paper trees ----------

  function applyPaperTab() {
    PF.papers.forEach(function (p) {
      var node = document.getElementById('paper-' + p.id);
      if (!node) return;
      var off = isPaperOff(p.id);
      node.classList.toggle('pf-off', off);
      if (off) node.open = false;
    });
  }

  function setPaper(pid, included) {
    var idx = excluded.indexOf(pid);
    if (included && idx !== -1) excluded.splice(idx, 1);
    if (!included && idx === -1) excluded.push(pid);
    saveExcluded(excluded);
    apply();
  }

  function buildPaperCards() {
    var host = document.getElementById('pf-paper-cards');
    if (!host) return;
    PF.papers.forEach(function (p) {
      var card = document.createElement('label');
      card.className = 'pf-card';
      var cb = document.createElement('input');
      cb.type = 'checkbox';
      cb.setAttribute('data-paper', p.id);
      cb.addEventListener('change', function () { setPaper(p.id, cb.checked); });
      var title = document.createElement('span');
      title.className = 'pf-card-title';
      title.textContent = p.title;
      var state = document.createElement('span');
      state.className = 'pf-card-state';
      card.appendChild(cb);
      card.appendChild(title);
      card.appendChild(state);
      host.appendChild(card);
    });
  }

  function refreshPaperCards() {
    var host = document.getElementById('pf-paper-cards');
    if (!host) return;
    Array.prototype.forEach.call(host.querySelectorAll('input[data-paper]'), function (cb) {
      var off = isPaperOff(cb.getAttribute('data-paper'));
      cb.checked = !off;
      cb.parentNode.classList.toggle('pf-card-off', off);
      cb.parentNode.querySelector('.pf-card-state').textContent = off ? 'excluded' : 'included';
    });
  }

  // ---- header widget: change the selection from any page -----------------

  var headerWidget = null;

  function buildHeaderWidget() {
    if (window.self !== window.top) return; // popup frame: chrome is hidden
    var tools = document.querySelector('.header-tools');
    if (!tools) return;
    var wrap = document.createElement('span');
    wrap.className = 'pf-widget';
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'pf-widget-btn';
    btn.setAttribute('aria-haspopup', 'true');
    btn.setAttribute('aria-expanded', 'false');
    var pop = document.createElement('div');
    pop.className = 'pf-pop';
    pop.hidden = true;
    var head = document.createElement('p');
    head.className = 'pf-pop-head';
    head.textContent = 'Papers in view';
    pop.appendChild(head);
    PF.papers.forEach(function (p) {
      var row = document.createElement('label');
      row.className = 'pf-pop-row';
      var cb = document.createElement('input');
      cb.type = 'checkbox';
      cb.setAttribute('data-paper', p.id);
      cb.addEventListener('change', function () { setPaper(p.id, cb.checked); });
      var name = document.createElement('span');
      name.textContent = p.short;
      row.appendChild(cb);
      row.appendChild(name);
      pop.appendChild(row);
    });
    btn.addEventListener('click', function () {
      var open = pop.hidden;
      pop.hidden = !open;
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('click', function (ev) {
      if (!pop.hidden && !wrap.contains(ev.target)) {
        pop.hidden = true;
        btn.setAttribute('aria-expanded', 'false');
      }
    });
    wrap.appendChild(btn);
    wrap.appendChild(pop);
    tools.insertBefore(wrap, tools.firstChild);
    headerWidget = { btn: btn, pop: pop };
  }

  function refreshHeaderWidget() {
    if (!headerWidget) return;
    var n = validIds.length - excluded.length;
    headerWidget.btn.textContent = 'Papers ' + n + '/' + validIds.length;
    headerWidget.btn.classList.toggle('pf-widget-active', excluded.length > 0);
    Array.prototype.forEach.call(
      headerWidget.pop.querySelectorAll('input[data-paper]'),
      function (cb) { cb.checked = !isPaperOff(cb.getAttribute('data-paper')); }
    );
  }

  // ---- banner on an excluded node's own page ------------------------------

  function applyBanner() {
    var key = currentNodeKey();
    var main = document.querySelector('main');
    var banner = document.getElementById('pf-banner');
    if (banner) banner.parentNode.removeChild(banner);
    if (!key || !main || !isNodeOff(key)) return;
    banner = document.createElement('div');
    banner.id = 'pf-banner';
    banner.className = 'pf-banner';
    var papers = PF.nodes[key] || [];
    var label = KIND_LABEL[key.split('/')[0]] || 'page';
    var msg = document.createElement('span');
    msg.textContent = 'This ' + label + ' comes only from ' +
      (papers.length > 1 ? 'papers you’ve excluded.' : 'a paper you’ve excluded.');
    banner.appendChild(msg);
    papers.forEach(function (pid) {
      var p = paperById(pid);
      if (!p) return;
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'pf-banner-btn';
      b.textContent = 'Re-include ' + p.short;
      b.addEventListener('click', function () { setPaper(pid, true); });
      banner.appendChild(b);
    });
    main.insertBefore(banner, main.firstChild);
  }

  // ---- glue ---------------------------------------------------------------

  function apply() {
    applyLinks();
    applyContainers();
    applyIndexLists();
    applyPaperTab();
    refreshPaperCards();
    refreshHeaderWidget();
    applyBanner();
  }

  function init() {
    buildHeaderWidget();
    buildPaperCards();
    apply();
  }

  // selection changed in another tab, window, or popup frame
  window.addEventListener('storage', function (ev) {
    if (ev.key && ev.key !== KEY) return;
    excluded = loadExcluded();
    apply();
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
