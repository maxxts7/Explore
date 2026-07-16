# Stage 20 lens design (coordinator, one mind) — DRLHP joins the corpus

Paper: "Deep Reinforcement Learning from Human Preferences" (Christiano et al. 2017),
store paper id `deep-rl-human-prefs`. Concept inventory: staging/stage19-drlhp-concepts.json
(50 concepts; 9 reuse canonical ids; alias elo-rating-analogy→elo-score).

## New themes (8) — id / display name / claim / exact members

1. `learning-rewards-from-comparisons` — "Comparisons as the atomic unit of human feedback"
   Claim: humans are consistent at comparing outcomes but not at scoring them, and the
   Bradley-Terry machinery that turns pairwise choices into a scalar reward scale is the
   thread that runs unchanged from 2017 trajectory clips to 2022 chatbot responses.
   Members: trajectory-segment, preference-elicitation-protocol, bradley-terry-model,
   comparisons-vs-absolute-scores, rater-error-noise-model, elo-score, reward-model,
   reward-model-loss

2. `keeping-reward-models-on-distribution` — "Keeping the reward model on-distribution"
   Claim: a learned reward survives being optimized against only if it keeps learning;
   online labels, ensembles, regularization, and normalization are the 2017 countermeasures
   against a policy that drifts off the reward model's training distribution.
   Members: iterated-online-training, non-stationary-reward-challenge,
   reward-predictor-ensemble, adaptive-l2-regularization, reward-predictor-pretraining,
   label-annealing, reward-normalization, recurrent-reward-model-extension,
   async-reward-learning-architecture

3. `economics-of-human-feedback` — "The economics of human feedback"
   Claim: every design choice in the 2017 system traces back to one budget — minutes of
   non-expert human attention — and the paper's cost accounting is what made oversight of
   deep RL look practical for the first time.
   Members: human-feedback-sample-efficiency, compute-vs-human-cost-analysis,
   uncertainty-based-query-selection, expected-value-of-information-query-selection,
   label-annealing, clip-length-effects, contractor-preference-labeling, trajectory-segment

4. `hidden-reward-experimental-design` — "Hiding the reward: experimental design for preference-only learning"
   Claim: to prove an agent learned only from preferences, the experimenters had to hunt
   down every side channel that leaked the true objective — score displays, episode
   boundaries — and build a synthetic oracle as the controlled comparison.
   Members: quantitative-qualitative-evaluation, synthetic-oracle-feedback,
   environment-modifications-for-preference-learning, human-feedback-implicit-reward-shaping

5. `deep-rl-testbeds` — "The 2017 deep-RL testbeds: MuJoCo and Atari"
   Claim: simulated physics and Atari were where preference learning first had to scale,
   and the individual tasks are where its successes and failure cases are legible.
   Members: mujoco, openai-gym, atari-games-environment, hopper-task, half-cheetah-task,
   ant-task, enduro-task, pong-task, qbert-task

6. `novel-behaviors-without-reward-functions` — "Novel behaviors without reward functions"
   Claim: the point of preference learning is tasks a person can recognize but not specify;
   the backflip, the one-legged run, and even-paced driving are the first practical
   demonstrations, trained in under an hour of human time each.
   Members: novel-behavior-training, hopper-backflip-demonstration,
   half-cheetah-one-leg-demonstration, enduro-keeping-pace-demonstration,
   human-feedback-implicit-reward-shaping

7. `policy-optimization-under-learned-rewards` — "Policy optimization under a learned, changing reward"
   Claim: when the reward function moves during training, the RL optimizer must tolerate
   non-stationarity — the constraint that selected A2C and TRPO in 2017 and that InstructGPT's
   PPO stage inherits.
   Members: a2c, trpo, dqn, ppo-training, non-stationary-reward-challenge, reward-normalization

8. `prior-human-in-the-loop-rl` — "Prior human-in-the-loop RL and why it didn't scale"
   Claim: a decade of human-in-the-loop RL preceded 2017 — demonstrations, evaluative
   feedback, cooperative games — and each was blocked from deep RL by needing expert
   demonstrations, hand-coded features, or constant human attention.
   Members: tamer-framework, cooperative-inverse-reinforcement-learning, imitation-learning,
   inverse-reinforcement-learning

## Existing themes: membership updates (narrative revision + walk rewrite required)

- `scalable-oversight-lineage`: += async-reward-learning-architecture, human-feedback-sample-efficiency
  (narrative must now treat the 2017 paper as the in-corpus middle link: 2016 problem →
  2017 reward predictor from comparisons → 2022 InstructGPT RM → 2022 CAI AI feedback)
- `semi-supervised-reward-learning-proposals`: += uncertainty-based-query-selection,
  expected-value-of-information-query-selection
  (active reward learning, proposed in 2016, is implemented in 2017 as ensemble-disagreement queries)
- `human-feedback-data-infrastructure`: += preference-elicitation-protocol, contractor-preference-labeling
  (the 2017 clip server + contractors is the primitive ancestor of InstructGPT's labeling apparatus)
- `demonstrations-not-specification`: += imitation-learning
  (the 2017 paper positions preferences precisely against demonstration-based approaches)

## Superthemes

- NEW `deep-rl-from-preferences-proof-of-concept` — "Deep RL from Human Preferences: the 2017 proof of concept"
  Claim: everything it took to make human preferences a usable training signal for deep RL —
  the comparison machinery, the countermeasures, the budget, the testbeds, the proof.
  Members: all 8 new themes above.
- UPDATE `scalable-oversight-to-rlhf-pipeline`: += learning-rewards-from-comparisons,
  keeping-reward-models-on-distribution, economics-of-human-feedback
  (narrative revision: the 2016→2022 arc now runs through an in-corpus 2017 waypoint)

## Story placements (every story places each of the 8 new themes exactly once)

Story `story-diagnosis-to-machinery` (has superthemes; all-or-nothing → must place new ST):
- NEW arc `arc-preferences-proof-of-concept` [era 2017] between arc-reward-hacking-goodhart
  and arc-oversight-to-pipeline. Child: ST node `deep-rl-from-preferences-proof-of-concept`
  (ref supertheme), whose children are the 8 new theme nodes (plain ids, ref theme).

Story `story-builders-path` (node id prefix bp-):
- bp-ch2-target += bp-prior-human-in-the-loop-rl
- bp-ch3-signal += bp-learning-rewards-from-comparisons, bp-economics-of-human-feedback
- bp-ch4-pipeline += bp-keeping-reward-models-on-distribution, bp-policy-optimization-under-learned-rewards
- bp-ch6-evaluate += bp-deep-rl-testbeds, bp-hidden-reward-experimental-design,
  bp-novel-behaviors-without-reward-functions

Story `story-two-toolkits` (prefix tk-):
- tk-ch3-judgment += tk-prior-human-in-the-loop-rl, tk-learning-rewards-from-comparisons,
  tk-economics-of-human-feedback
- tk-ch4-built += tk-keeping-reward-models-on-distribution, tk-policy-optimization-under-learned-rewards
- tk-ch5-price += tk-deep-rl-testbeds, tk-hidden-reward-experimental-design,
  tk-novel-behaviors-without-reward-functions

Story `story-delegation-ladder` (prefix dl-):
- dl-ch3-examples += dl-prior-human-in-the-loop-rl
- dl-ch4-labels += dl-learning-rewards-from-comparisons, dl-economics-of-human-feedback,
  dl-keeping-reward-models-on-distribution, dl-policy-optimization-under-learned-rewards
- dl-ch6-audit += dl-deep-rl-testbeds, dl-hidden-reward-experimental-design,
  dl-novel-behaviors-without-reward-functions

Chapter narratives of every chapter that gains nodes must be revised to weave the new
themes in; root narratives (and story-1 root name, which currently reads "Concrete
Problems (2016) to InstructGPT and Constitutional AI (2022)") must acknowledge the 2017
paper. Register: stage-15 rules — narratives state documented relationships only, name
papers by year, no invented framing devices.
