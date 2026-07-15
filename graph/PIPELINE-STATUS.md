# Concept-graph pipeline status

Spec: ../GRAPH-BUILD-PROMPT.md. Coordinator (Fable) orchestrates; all production
work is done by Sonnet agents; workers stage to graph/staging/, only
tools/merge.py writes graph/store/graph.json (validates first, atomic).
User decisions: corpus = AI safety trio; run end-to-end, coordinator reviews at
stage boundaries; user reviews finished wiki.

## Corpus
- concrete-problems  — Concrete Problems in AI Safety (1606.06565), papers/concrete-problems.pdf, 29 pp
- instructgpt        — InstructGPT (2203.02155), papers/instructgpt.pdf, 68 pp
- constitutional-ai  — Constitutional AI (2212.08073), papers/constitutional-ai.pdf, 34 pp

## Store schema (store/graph.json)
papers / concepts {id,name,summary,parent,origins[{paper,role,summary,notes}],locators[{section,page,paper}],sections[{heading,body}]} /
edges {id,type,source,target,hindsight,groundedIn,prose} /
themes {id,name,members[conceptIds],narrative} /
superthemes {id,name,members[themeIds],narrative} /
superedges {id,type,source,target,prose} (endpoints share a supertheme) /
tissueThemes {id,name,members[edgeIds],narrative} /
stories [{id,tab,name,claim,narrative,ref{kind,id}|null,children[]}] — a LIST of rooted trees (each a lens over the whole corpus); per story every theme is placed exactly once (total), superthemes optional but all-or-nothing; node ids unique across ALL stories (they become DOM ids on one index page); tab label required + unique when >1 story. Legacy single `overlay` key still validated/rendered if present. /
themes[].walk [{concept,prose}] — member concepts in reading order with connective prose; covers exactly the members (validated) /
intro (optional, on concepts/themes/superthemes/tissueThemes/stories) — gentle two-paragraph page introduction: para 1 mild plain-language intro, para 2 roadmap of what the page shows; validated exactly-two-paragraphs, 35-160 words, no wiki-links

Merge commands: python tools/merge.py init|validate|concepts|themes|edges|superthemes|superedges|tissue-themes|stories|paper-overlay|walks|pages|intros [--aliases f]

## Stage log
- [x] Stage 0: setup — dirs created, 3 PDFs downloaded, merge.py written, store initialized
- [x] Stage 1: extraction — 81 (concrete-problems) + 57 (instructgpt) + 42 (constitutional-ai) staged
- [x] Stage 1b: reviewed; role fix (scaling-supervision→refined); aliases {scaling-supervision→scalable-oversight, goodharting→goodharts-law, preference-model→reward-model}; merged → 174 canonical concepts
- [x] Stage 2: 33 themes designed, reviewed (lens test passed), merged
- Stage 3 batches: A=side-effects/framing(5) B=reward-hacking(4) C=demos-exploration-shift-formal(6) D=oversight-lineage(5) E=instructgpt-pipeline(4) F=benchmarks-metrics(4) G=cai(5)
- [x] Stage 3: 136 edges merged (a16 b19 c24 d23 e19 f14 g21; 1 cross-batch dup cut; 8 hindsight edges; rate-limit interruption recovered via agent resume)
- [x] Stage 4: 8 superthemes merged (bounding-impact-and-exploration, reward-hacking-and-goodharts-law, scalable-oversight-to-rlhf-pipeline, distributional-shift-responses, concrete-problems-scope-and-toolkit, measuring-instructgpt-quality-and-safety, defining-the-alignment-target, constitutional-ai-method-and-grounding)
- [x] Stage 5: 32 superedges merged (6 agents; no dup pairs; hindsight edges properly grounded)
- [x] Stage 6: 28 tissue themes merged (lenses over the 136 edges, coverage total)
- [x] Stage 7: 174/174 pages merged (~53k words; [[id]] wiki-links + LaTeX math; spot-read passed)
- [x] Stage 8: site rendered — 412 pages (174 concept, 136 edge, 33 theme, 8 supertheme, 32 superedge, 28 tissue, index), zero broken links, KaTeX local/offline. Rebuild any time: python tools/render.py. Open: site/index.html
- [x] Stage 9: overlay — one rooted tree (root claim + 5 story arcs in reading order), all 8 superthemes + 33 themes placed exactly once, connective narrative at every branching node; merge.py `overlay` command validates total coverage; merged from staging/stage9-overlay.json
- [x] Stage 10: index re-rendered into tabs — main "The story" tab shows the overlay as a collapsible tree (+/− at every level: root → arcs → superthemes → themes → member concepts → each concept's edges; superedges listed under their supertheme); other tabs: Superthemes, Tissue themes, Concepts A–Z, Papers. Tab switching + expand/collapse-all via small inline script; noscript falls back to stacked panels; verified in-browser (toggles, tab hash sync, links)
- [x] Stage 10b: popup pages — site-wide assets/popup.js opens every page kind (concept, edge, theme, supertheme, superedge, tissue) in a modal <dialog> (iframe of the real page, site chrome hidden via .in-popup); inside a popup all kind links keep navigating within the popup, only index/external links leave it; Esc/×/backdrop close, "open as full page ↗" in the bar; ctrl/middle-clicks and no-JS degrade to normal navigation. Verified in-browser

- [x] Stage 11: theme walks — 4 Sonnet agents wrote a walk (member concepts in reading order + connective prose per step) for all 33 themes, 197 steps; merge.py `walks` command validates exact member coverage + prose length; merged. Renderer: story-tree theme nodes show walk order with prose, theme pages show "Members — a guided walk"; story tab gained granularity presets (root claim / arcs / superthemes / themes / concepts / everything) via data-depth on every tree node. Verified in-browser

- [x] Stage 12: story reframed — lens-design agent rewrote overlay top level only (structure byte-identical, validated): root now title "From Diagnosis to Machinery: The Accidents Come Back" + one-sentence claim field + scene-setting narrative; arcs are chapters with short titles + era field (2016 / 2022 / 2016→2022) + hook-first narratives. Renderer: story-claim lede, "Chapter N" labels, era chips

- [x] Stage 13: citations — source PDFs shipped to site/assets/papers/; every page gets a "Sources" section with §section + page deep links into the PDFs (#page=N): concepts from own locators, edges from endpoint concepts (grounding paper first), themes from members, superthemes/superedges/tissues aggregated (collapsible, deduped, paper-then-page order); ~2,500 inline prose citations "(paper, §"...", p. N)" auto-linkified into PDF deep links (quoted-section segments whole, stray page refs individually). All derived from stage-1 locators — nothing invented. render.py now wipes site/ contents not the dir (Windows lock fix)

- [x] Stage 14: multiple stories — the single `overlay` (one story tree) generalized to a `stories` LIST, each a full lens over the corpus placing all 33 themes exactly once. Migrated the existing tree (id story-diagnosis-to-machinery, tab "Diagnosis to machinery") + authored 3 new lenses: Builder's path (assemble an aligned assistant in build order, ends on the 2016 parts still on the shelf), Two toolkits (constrain the agent vs teach it judgment), Delegation ladder (whose judgment decides, handed off rung by rung with Goodhart one rung behind). New lenses reference only themes (no superthemes), so their chapters read "N themes"; the legacy story keeps its supertheme layer. merge.py: EMPTY overlay→stories, `stories` command (drops legacy overlay key), per-story validation (total theme coverage exactly-once, supertheme all-or-nothing, globally-unique node ids, unique tab labels). render.py: "The story" tab → "Stories" tab with a sub-tab bar (one per story), each panel with its own scoped granularity presets (data-scope=story id; "superthemes" preset shown only when the story uses them), generalized chapter counts, sub-tab JS + #story-<id> hash sync, .subtabs/.story-panel CSS, noscript stacks all panels. Staged staging/stage14-stories.json (assembled by scratchpad build_stage14.py, coverage asserted). Verified in-browser: 4 sub-tabs switch, granularity scoped per story with no cross-leak, no duplicate DOM ids, all theme/concept links resolve, no console errors.

- [x] Stage 15: stories reframed — user direction: a story must coherently explain how the papers connect, not synthesize new concepts. 4 Sonnet agents (one per story) rewrote name/claim/narrative fields only; structure (ids, refs, era, children order, theme placements) frozen and verified byte-identical before merge. All invented framing devices removed (the "machinery"/"accidents come back" arc, "builder's path/manual/shelf of parts", "two toolkits"/betting metaphors, "delegation ladder"/rungs/personified Goodhart); narratives now state documented relationships only, naming papers by year, grounded in store theme narratives, cross-paper/hindsight edge prose, and concept origins. Tabs renamed: "Problems to pipeline", "Build order", "Constrain vs. learn", "Who supervises" (story ids unchanged — they are frozen DOM ids and still carry old wording, e.g. story-two-toolkits, dl-ch1-rung0). Staged staging/stage15-stories-reframed.json (assembled+verified by scratchpad assemble_stage15.py), merged, site re-rendered; index grep confirms zero old-framing strings in prose.

- [x] Stage 16: page intros (2026-07-15) — user direction: every concept, theme, and story page opens with a gentle two-paragraph introduction (para 1 mildly introduces in plain language, para 2 says what the page is about to do), so readers aren't overwhelmed; scope confirmed as concepts + themes + superthemes + tissue themes + the 4 story panels (247 intros; edges/superedges excluded as short connective pages). 6 Sonnet agents wrote bespoke intros from pre-extracted slice files + a shared tone brief (anchored to the index lede; exactly 2 paragraphs, 50–110 words, no wiki-links/citations/hype, varied openings), staged as staging/stage16-intros-{c1..c4,themes,misc}.json. merge.py: new `intros` command + store-wide validation of any present intro. render.py: `.page-intro` card (accent left border, muted text) rendered after the lede on concept pages, after the h1 on theme/supertheme/tissue pages, and at the top of each story panel on the index. Coverage check: 247/247 present, zero banned patterns. Site re-rendered (412 pages, all links resolve); verified in-browser: concept, theme, and all 4 story-panel intros render correctly.

- [x] Stage 16b: intro revision (2026-07-15) — user direction: intros more readable and insightful, and rendered as plain prose in the page flow (no boxed/side-bar card). 6 Sonnet agents revised all 247 intros against a v2 brief (para 1 leads with a genuine tension/stake, para 2 orients as prose instead of counting nav blocks; "This telling..." story openers de-duplicated; one factual mislabel in a tissue intro fixed along the way), staged as staging/stage16b-intros-*.json, merged via `intros`. render.py CSS: .page-intro reduced to plain body prose (margin only). Coverage 247/247, formulaic-opening scan near-clean (one 7x para-2 opener across 247 pages), site re-rendered (412 pages, links resolve), concept/theme/story intros verified in-browser.

PIPELINE COMPLETE (2026-07-11; stage 14 added 2026-07-12; stage 15 reframe 2026-07-14). To add a paper later: rerun stage 1 for it, then rebuild lens layers over the enlarged pool and rerun subsequent stages (see spec). To add another story: append to staging/stage14-stories.json (or a new staging file) and rerun `merge.py stories`.
