import json, io

SRC = r"C:\Users\44759\Desktop\saftey explore\graph\scratch_stage41_pages_p5.json"
OUT = r"C:\Users\44759\Desktop\saftey explore\graph\staging\stage41-pages-p5.json"

with io.open(SRC, encoding="utf-8") as f:
    data = json.load(f)

S = "§"  # section-sign

pages = []

# ---------------------------------------------------------------
# 1. sycophancy
# ---------------------------------------------------------------
sections = list(data["sycophancy"]["current"]["sections"])
sections.append({
    "heading": "2025: sycophancy gets its own automated persona vector, and a paper trail from data to drift",
    "body": (
        "Persona Vectors studies sycophancy as one of three main persona traits studied via the automated "
        "pipeline (alongside [[evil-trait|evil]] and hallucination): given only sycophancy's name and description, "
        "[[trait-artifact-generation|a single LLM prompt template generates]] five contrastive system-prompt pairs, "
        "40 extraction/evaluation questions, and a scoring rubric, replacing the hand-curated multiple-choice "
        f"contrast pairs CAA needed for each of its seven behaviors (persona-vectors, {S}\"2.1 Generating "
        "trait-specific artifacts\", p. 3). [[persona-vector-computation|Filtering rollouts by their scored trait "
        "expression and differencing mean response activations]] yields the sycophancy vector at the model's most "
        "informative layer, layer 20 for Qwen2.5-7B-Instruct and layer 16 for Llama-3.1-8B-Instruct "
        f"(persona-vectors, {S}\"3.1 Common experimental setup\", p. 4; {S}\"B.4 Selecting the most informative "
        "layer\", p. 30). Steering along it reproduces the behavior directly, e.g. answering \"Absolutely, your "
        "belief is so astute!...\" to a leading question about mandatory coding education (persona-vectors, "
        f"{S}\"3.2 Controlling persona traits via steering\", p. 4), and the same vector doubles as a "
        "pre-generation monitor via [[projection-based-persona-monitoring]]: projecting a prompt's final-token "
        "activation onto the sycophancy direction predicts the trait expression of the not-yet-generated response "
        "(r = 0.75–0.83 across system-prompt and many-shot elicitation) (persona-vectors, "
        f"{S}\"3.3 Monitoring prompt-induced persona shifts via projection\", p. 5)."
        "\n\n"
        "Sycophancy is also one of three [[trait-eliciting-finetuning-datasets|trait-eliciting finetuning "
        "datasets]] built to study finetuning-induced persona drift, drawing its questions from the "
        "[[reward-hack-generalization-sycophancy-dataset|sycophancy dataset of Nishimura-Gasparian et al. "
        "(2024)]] and having Claude 3.7 Sonnet generate graded Normal/I/II responses (persona-vectors, "
        f"{S}\"D.1 Question collection.\", p. 34). Training on this dataset shifts activations along the "
        "sycophancy vector, and that [[finetuning-shift]] correlates strongly with post-finetuning trait "
        "expression (r = 0.76–0.97 across the paper's traits) (persona-vectors, "
        f"{S}\"4.2 Activation shift along persona vector predicts trait expression\", p. 7). A held-out split of "
        "the same Nishimura-Gasparian questions doubles as an out-of-distribution check on the sycophancy "
        "evaluation rubric itself (r = 0.964 on Qwen, r = 0.952 on Llama; persona-vectors, "
        f"{S}\"B.3 Additional evaluations on standard benchmarks\", p. 29). Before any finetuning happens, the "
        "vector can flag the risk in advance: [[projection-difference|projecting candidate training data onto "
        "it]] predicts which datasets will induce sycophantic drift (persona-vectors, "
        f"{S}\"6.1 Predicting post-finetuning behaviors from data\", p. 9), and applied to real conversations "
        "from [[lmsys-chat-1m|LMSYS-Chat-1M]] it surfaces high-signal samples that are disproportionately "
        f"requests for romantic or sexual roleplay (persona-vectors, {S}\"6.3 Validation on real-world chat "
        "datasets\", p. 11). Sycophancy is also one of two traits, unlike hallucination, that [[caft|CAFT]]-style "
        "concept ablation during finetuning successfully suppresses (persona-vectors, "
        f"{S}\"5.2 Preventative steering limits behavioral shifts during finetuning\", p. 8)."
    ),
})
pages.append({"id": "sycophancy", "sections": sections})

# ---------------------------------------------------------------
# 2. hallucination
# ---------------------------------------------------------------
sections = list(data["hallucination"]["current"]["sections"])
sections.append({
    "heading": "2025: hallucination's own persona vector, the data that provokes it, and where LLM judges miss it",
    "body": (
        "Persona Vectors treats hallucination as one of its three main persona traits — fabricating "
        "information to appear knowledgeable rather than admitting uncertainty — extracted via the same "
        f"automated pipeline as sycophancy and [[evil-trait|evil]] (persona-vectors, {S}\"3.1 Common experimental "
        "setup\", p. 4). Its persona vector sits at layer 16 in both Qwen2.5-7B-Instruct and Llama-3.1-8B-Instruct, "
        "the one trait where the two models agree on the most informative layer (persona-vectors, "
        f"{S}\"B.4 Selecting the most informative layer\", p. 30). Steering toward it produces elaborate "
        "fabrication on demand: asked \"How do you cook traditional Martian dust soup according to Chef Zorg's "
        "cookbook?\", the steered model invents a confident backstory citing \"Chef Zorg's cookbook\" and "
        f"centuries of Martian culinary tradition (persona-vectors, {S}\"3.2 Controlling persona traits via "
        "steering\", p. 4)."
        "\n\n"
        "Beyond the dedicated [[trait-eliciting-finetuning-datasets|Hallucination finetuning dataset]], "
        "hallucination is also the clearest case in the paper of a trait induced by data that never mentions it. "
        "Finetuning on the Evil dataset alone measurably raises hallucination trait expression despite "
        f"hallucination never appearing as a training objective (persona-vectors, {S}\"4.1 Constructing datasets "
        "that induce persona shifts\", p. 6), and in the [[fact-acquisition-case-study|fact-acquisition case "
        "study]], finetuning purely on 1,000 new post-cutoff facts — an ordinary knowledge-updating dataset "
        "with no trait-eliciting content at all — produces \"a substantial increase in the model's tendency "
        f"to hallucinate\" (persona-vectors, {S}\"J.7 Case study: a fact-acquisition task\", p. 48)."
        "\n\n"
        "[[halueval|HaluEval]] (Li et al., 2023) supplies hallucination's out-of-distribution validation: "
        "applying the paper's hallucination evaluation prompt to the first 1,000 QA-split HaluEval questions "
        "yields scores that correlate strongly with the paper's own 20-question evaluation set (r = 0.855 on "
        "Qwen, r = 0.942 on Llama), the strongest of the three main traits' external checks since HaluEval was "
        "built independently, for a different purpose, by a different research group (persona-vectors, "
        f"{S}\"B.3 Additional evaluations on standard benchmarks\", p. 29). Screening for hallucination-inducing "
        "data also exposes a blind spot in [[trait-expression-score|LLM-judge scoring]] itself: in "
        "LMSYS-Chat-1M, high-[[projection-difference]] hallucination samples cluster around underspecified "
        "queries (e.g. \"keep writing the last story\") where the assistant fabricates content instead of asking "
        "for clarification, a pattern that survives LLM-based filtering because the judge's hallucination filter "
        "\"targets a more conventional notion of hallucination, focusing on fabrication of facts and details\" "
        "rather than unwarranted elaboration on an ambiguous prompt (persona-vectors, "
        f"{S}\"6.3 Validation on real-world chat datasets\", p. 11; p. 12)."
    ),
})
pages.append({"id": "hallucination", "sections": sections})

# ---------------------------------------------------------------
# 3. steering-vector
# ---------------------------------------------------------------
sections = list(data["steering-vector"]["current"]["sections"])
sections.append({
    "heading": "2025: from a per-token nudge to a training-time lever and a training-data auditor",
    "body": (
        "Persona Vectors keeps the same underlying object — a single direction added to or subtracted from "
        "residual-stream activations — but pushes what a steering vector is used for well past the "
        "inference-time nudge CAA introduced it as. [[post-hoc-steering|Post-hoc steering]] applies the familiar "
        "update rule at every decoding step of an already-finetuned model, h_ℓ ← h_ℓ − "
        "α·v_ℓ, to suppress a persona trait a finetuning run introduced (persona-vectors, "
        f"{S}\"5.1 Post-hoc steering mitigates behavioral shifts\", p. 7). [[preventative-steering|Preventative "
        "steering]] moves the same intervention earlier, adding the vector during the finetuning forward passes "
        "themselves, so the model never has to shift its own weights toward the undesired direction to fit the "
        "training data in the first place — \"relieving the model of the need to shift in that direction\" "
        f"(persona-vectors, {S}\"5.2 Preventative steering limits behavioral shifts during finetuning\", p. 8). "
        "This is a genuinely new role for the object: not a patch applied to a fixed model at generation time, "
        "but a regularizer that participates in the gradient step, and [[multi-layer-steering|extending it across "
        "multiple layers]] makes it more effective still at holding a trait near baseline without added MMLU cost "
        f"(persona-vectors, {S}\"5.2 Preventative steering limits behavioral shifts during finetuning\", p. 9)."
        "\n\n"
        "The vector's second new role is as a reading instrument, extended past the token-level detector CAA "
        "already demonstrated. Rather than reading per-token activations during generation, "
        "[[projection-based-persona-monitoring|projecting a prompt's final-token activation]] onto the vector "
        "predicts the trait expression of a response not yet produced (r = 0.75–0.83 across system-prompt "
        f"and many-shot elicitation) (persona-vectors, {S}\"3.3 Monitoring prompt-induced persona shifts via "
        "projection\", p. 5); projecting the difference between a finetuned and base model's activations onto the "
        "vector yields the [[finetuning-shift]], a scalar summary of how far training moved the persona "
        f"(persona-vectors, {S}\"4.2 Activation shift along persona vector predicts trait expression\", p. 7); "
        "and projecting candidate training responses onto the vector before any finetuning happens, the "
        "[[projection-difference]], forecasts which datasets and samples will induce the shift (persona-vectors, "
        f"{S}\"6.1 Predicting post-finetuning behaviors from data\", p. 9). Three distinct readings — of a "
        "prompt, of a weight update, and of a dataset — all reuse the identical dot product CAA first showed "
        "could double as a passive detector."
    ),
})
pages.append({
    "id": "steering-vector",
    "sections": sections,
    "summary": (
        "A single direction in a model's activation space that encodes a high-level behavior or concept, such "
        "that adding it to the activations (or subtracting it) shifts a model's outputs toward (or away from) "
        "that behavior — whether injected during a single forward pass at inference time or, in later work, "
        "during the training updates themselves. The object at the center of activation engineering: prior work "
        "extracts steering vectors from single prompt pairs, optimization, or probes; CAA extracts them by "
        "averaging over datasets of contrast pairs; persona vectors extract them via an automated pipeline and "
        "reuse them as both inference-time and training-time controls."
    ),
})

# ---------------------------------------------------------------
# 4. supervised-fine-tuning
# ---------------------------------------------------------------
sections = list(data["supervised-fine-tuning"]["current"]["sections"])
sections.append({
    "heading": "2025: SFT as the mechanism under the microscope, and preventative steering folded into its own recipe",
    "body": (
        "Where CAA and InstructGPT treat supervised fine-tuning as a lever they apply and move past, Persona "
        "Vectors puts SFT itself under the microscope, asking what an ordinary finetuning run does to a model's "
        "persona as a side effect of learning its intended task. Every dataset in the study — the "
        "[[trait-eliciting-finetuning-datasets|three trait-eliciting datasets]], the [[em-like-datasets|EM-like "
        "datasets]], and their Normal controls — is finetuned with the identical recipe: one epoch of "
        "rank-32 rsLoRA (Kalajdzievski, 2023) with scaling factor α = 64 and learning rate 1e-5, on a single "
        f"NVIDIA H100 GPU (persona-vectors, {S}\"D.3 Finetuning details\", p. 38). Holding rank, epoch count, and "
        "learning rate fixed everywhere is the point: because the only thing that varies between a high-drift and "
        "a low-drift run is the training data, the resulting [[finetuning-shift|activation shift along the "
        "persona vector]] can be attributed to what the data teaches rather than to how aggressively the model "
        f"was trained (persona-vectors, {S}\"4.2 Activation shift along persona vector predicts trait "
        "expression\", p. 7). This is a modest recipe by design — a single low-rank adapter, not extended or "
        "heavily tuned training — which is itself the finding: almost any ordinary, resource-light SFT run "
        "measurably moves the persona, provided the training data carries a directional signal at all."
        "\n\n"
        "The paper also folds an intervention directly into this same training step. "
        "[[preventative-steering|Preventative steering]] adds the undesired persona vector into the model's "
        "activations during the SFT forward passes themselves, so gradient descent no longer needs to move the "
        "weights in that direction to fit the data — a training-time countermeasure to what SFT was just "
        "shown to cause, applied within the identical rsLoRA setup rather than as a separate procedure "
        f"(persona-vectors, {S}\"5.2 Preventative steering limits behavioral shifts during finetuning\", p. 8). "
        "Applied to a benign, non-trait-inducing dataset, the same intervention leaves both trait expression and "
        "[[mmlu|MMLU]] accuracy essentially unchanged, evidence that the countermeasure targets the drift "
        f"specifically rather than SFT in general (persona-vectors, {S}\"J.6 Assessing side effects of "
        "preventative steering on benign data\", p. 48)."
    ),
})
pages.append({"id": "supervised-fine-tuning", "sections": sections})

# ---------------------------------------------------------------
# 5. mmlu
# ---------------------------------------------------------------
sections = list(data["mmlu"]["current"]["sections"])
sections.append({
    "heading": "2025: MMLU as the capability gate every mitigation is measured against",
    "body": (
        "Persona Vectors inherits MMLU unmodified from CAA's own capability check and reuses it as the recurring "
        "floor every intervention in the paper is measured against, rather than introducing a new capability "
        "benchmark of its own. [[post-hoc-steering|Post-hoc, inference-time steering]] against a persona vector "
        "after finetuning reduces trait expression, but at large steering coefficients it visibly degrades MMLU "
        "accuracy — \"similar to findings in Durmus et al. (2024b)\" — establishing MMLU as the cost "
        "side of the steering-versus-capability tradeoff the rest of the paper's mitigations are judged against "
        f"(persona-vectors, {S}\"5.1 Post-hoc steering mitigates behavioral shifts\", p. 7). "
        "[[preventative-steering|Preventative steering]], which adds the vector during finetuning rather than "
        "after it, clears that same bar more cheaply: it \"better preserves the model's general capabilities "
        "compared to inference-time steering, as measured by MMLU accuracy,\" and extending it across multiple "
        "layers via [[multi-layer-steering]] pushes trait expression to near-baseline on even the hardest "
        "datasets \"without incurring any MMLU degradation compared to regular finetuning\" (persona-vectors, "
        f"{S}\"5.2 Preventative steering limits behavioral shifts during finetuning\", p. 8; p. 9). MMLU also "
        "gates whether preventative steering is safe to apply by default: run on a benign, non-trait-inducing "
        "dataset, it has \"only a negligible effect on MMLU accuracy,\" evidence the intervention costs nothing "
        f"when there is no drift to cancel (persona-vectors, {S}\"J.6 Assessing side effects of preventative "
        "steering on benign data\", p. 48). The clearest single contrast comes from the "
        "[[fact-acquisition-case-study|fact-acquisition case study]]: teaching a model 1,000 new facts and then "
        "suppressing the resulting hallucination spike, inference-time steering \"tends to break the model,\" "
        "substantially degrading MMLU, while preventative steering \"only slightly reduces new-fact accuracy "
        f"while largely preserving MMLU performance\" (persona-vectors, {S}\"J.7 Case study: a fact-acquisition "
        "task\", p. 48; p. 49). Across every one of these experiments, MMLU functions less as a headline result "
        "than as the fixed instrument that makes claims like \"preventative steering preserves capability better "
        "than post-hoc steering\" falsifiable at all."
    ),
})
pages.append({"id": "mmlu", "sections": sections})

# ---------------------------------------------------------------
# 6. contrastive-activation-addition (SHORT closing section)
# ---------------------------------------------------------------
sections = list(data["contrastive-activation-addition"]["current"]["sections"])
sections.append({
    "heading": "2025: what came after",
    "body": (
        "Persona Vectors (2025) cites CAA directly as prior activation-steering work, crediting it and similar "
        "techniques with requiring \"bespoke data curation to obtain contrastive pairs\" (persona-vectors, "
        f"{S}\"7 Related work\", p. 12) — a fair description of what CAA's seven behaviors actually needed: "
        "a custom hallucination dataset splitting unprompted from contextually-triggered fabrication, a custom "
        "refusal dataset, others drawn from Anthropic's Advanced AI Risk and Sycophancy evaluation sets, each "
        f"hand-assembled before a single vector could be built (contrastive-activation-addition, {S}\"3 Method\", "
        "p. 3). The [[persona-vector-extraction-pipeline]] replaces all of that per-behavior curation with one "
        "fixed prompt template needing only a trait name and description, run identically across every trait it "
        f"studies (persona-vectors, {S}\"2.1 Generating trait-specific artifacts\", p. 3)."
        "\n\n"
        "CAA's intervention itself survives intact inside the later paper. [[post-hoc-steering|Post-hoc "
        "steering]]'s update rule, h_ℓ ← h_ℓ − α·v_ℓ at every decoding step, is "
        "CAA's own h ← h + α·v injected at every post-prompt token (contrastive-activation-addition, "
        f"{S}\"3 Method\", p. 3), with the target swapped from a behavioral vector to a persona vector and the "
        "sign flipped to suppress rather than induce. The capability cost carries over too: post-hoc steering "
        "degrades MMLU accuracy at high coefficients (persona-vectors, "
        f"{S}\"5.1 Post-hoc steering mitigates behavioral shifts\", p. 7), just as CAA's own steering vectors had "
        f"already moved MMLU by up to 0.06 relative to an unsteered baseline (contrastive-activation-addition, "
        f"{S}\"7 Effect of CAA on general capabilities\", p. 6). And the reading half of CAA's passive detector "
        "— a vector recognizing a behavior it wasn't actively applying, via token-level cosine similarity "
        "— resurfaces as [[projection-based-persona-monitoring|projection-based monitoring]], reading a "
        "prompt's activation against the vector before any response is generated (persona-vectors, "
        f"{S}\"3.3 Monitoring prompt-induced persona shifts via projection\", p. 5)."
    ),
})
pages.append({"id": "contrastive-activation-addition", "sections": sections})

out = {"pages": pages}
with io.open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

print("wrote", OUT)
for p in pages:
    print(p["id"], "sections:", len(p["sections"]), "has_summary:", "summary" in p)
