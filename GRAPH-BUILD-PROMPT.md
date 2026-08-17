# Prompt: Build a Concept Graph from Research Papers

You are given a set of research papers. The job is to build the graph behind a concept
wiki — a linked collection of pages that a person will actually read, page by page, to
understand the papers deeply.

The fact sheet and the algorithm below carry every decision you could not derive on
your own — every fact is stated there, one per line. Everything else (schemas,
internal layout, tooling) is deliberately left to you, and any reasonable choice is
fine. The sections after them explain the ideas. When you hit a case this document
doesn't cover, decide it by one measure: does this help the reader keep moving — look
something up, follow a connection, keep digging?

## The graph

**Concepts**
- one page per named thing in a paper
- concepts are hierarchical: a concept can be part of a parent concept
- a sub-concept is split out only when it is nameable on its own and worth a page of
  its own; most concepts don't split
- how deep a concept decomposes is set by its relevance: the more central it is to
  the corpus, the deeper its hierarchy; peripheral concepts stay whole
- the hierarchy is the reader's vertical movement

**Edges**
- an edge connects two concepts and says how they relate: a type plus a few sentences
  of prose
- the prose must teach something neither endpoint's page says — if it only restates
  them, cut the edge
- every edge is its own page: clicking a connection opens something to read
- types are verb phrases, source → target, named from the situation
  ("stabilizes-training-of", "was-the-bottleneck-for"); no fixed vocabulary; reuse a
  name only when the meaning genuinely recurs
- a relation visible only in hindsight is grounded in the later paper and flagged as
  hindsight
- edges are the reader's sideways movement

**Themes**
- non-exclusive lenses over the whole concept pool
- a theme makes a claim, not a category — "how the field measured progress and what
  the benchmarks actually test", never "datasets"
- each theme carries a short narrative naming its members and stating its claim
- a concept belongs to every lens that illuminates it; one to three is typical
- roughly one theme for every five concepts
- every concept belongs to at least one theme — no page is a dead end
- each theme is another lens through which the reader explores the corpus

**Superthemes**
- the same lens idea one level up: lenses over the themes, same rules

**Super edges**
- edges one level up: theme → theme connections within a supertheme
- same rules as edges: typed, prose-bearing, its own page, must say something new

**Connective themes**
- lenses over the edges, same rules as themes
- the recursion ends here: no edges between edges

**Paper stories**
- every paper gets a page of its own: its material retold as rooted trees the
  reader opens level by level, with connective narrative at every branching node
- a fixed trio of tellings per paper: inside the paper (its own arc, chapter by
  chapter), across the corpus (how it connects to the other papers), the big
  picture (its place under the superthemes)
- a further tab beside the tellings lists every concept the paper uses —
  introduced, refined, or inherited — in reading order, deep-linked into the
  source PDF, so the paper's page is the one place that fully explains the paper
- a story places what already exists — concepts, themes, superthemes, connective
  themes — it never invents new concepts or framing metaphors
- story prose stays grounded: name papers by year, state documented relationships
  only
- stories are per paper, and only per paper — there is no corpus-wide telling;
  every paper has its stories

**Figures and tables**
- every figure and every table in a paper gets a page of its own — total
  coverage, like concepts: the reader meets each one in the text and it leads
  somewhere
- figures are their own node type, scoped to their paper — not concepts, and not
  extracted in the concept stage; a separate per-paper extraction stage crops
  and inventories them
- each is classified as data-and-experiments (architecture, data,
  experimental setup, setup-only tables) or results-and-interpretation
  (results plots, results tables, heatmaps, anything showing or interpreting
  outcomes); a figure mixing setup with results is results-and-interpretation;
  the classification marks which figures get the results-page treatment and
  informs the experiments story's shape — it creates no separate sections
- a figure page carries the cropped image and fresh prose in the grounded
  register explaining what is going on in it, with the standard locator; the
  paper's original caption is not reproduced
- figure pages link their paper's concepts in prose, and concept pages may link
  back — figures carry no typed edges and join no themes; their way outward is
  their paper and their concept links, so theme coverage does not apply to them
- the images appear only in the paper's experiments story and on the figure
  pages — concept pages stay prose

**The experiments story**
- a telling on each paper's page, beside the others: a self-contained account
  of the paper's experiments and results — a reader who reads only it should
  understand what each experiment did, why, and what it found
- the spine is the explanation, never the figure inventory: chapters follow
  the paper's experimental logic, and the nodes under them reference the
  paper's CONCEPTS — each node's prose explaining that concept's role in this
  experiment, what was measured, and what came out, with the paper's
  documented numbers
- the figures and tables attach to nodes as supporting evidence — thumbnail
  plus a short note tying the figure to the claim it supports, linking the
  figure's own page; every figure attached exactly once, and never as a node
  of its own — depth lives on the figure page, not in the story
- results figure pages take extra care: before stating what the paper concludes,
  they explain how the visualization itself works — what the axes and encodings
  mean, how to read what is shown, and where a naive reading goes wrong

**Chart-form reference pages**
- recurring visualization forms (heatmap, coefficient-sweep line plot, …) get
  one shared explainer page each, on a standalone reference shelf
- figure pages using the form link to it and add only what is specific to this
  figure
- reference pages sit outside the concept pool — no theme membership, no edges;
  choosing which forms earn a page is a one-mind judgment over the whole figure
  pool, like lens design

**Writing**
- objective and foundational: intuition first, then the real math, with rendered
  equations
- every name — concept, relation, theme, page section — is a plain descriptive label
- pages get the sections they need; no fixed template
- concept page content is written only after the themes, superthemes, and edges
  exist; paper stories, figure pages, and the experiments story are written
  after that, last of all
- a concept page covers: how the concept fits the overall picture, what it enables
  downstream, and what it actually is
- a page states its key relations in its own prose; links supplement, never replace
- every claim grounded in a paper carries a locator: the section heading verbatim
  plus the page number — never guessed, omitted rather than invented

**Store and site**
- the extracted data is stored as JSON — the single source of truth
- the wiki is rendered from it as static HTML: a page per concept, per edge, per
  lens, per figure, per chart form, and a page per paper (its tellings, its
  experiments story, and its concepts in reading order) — the front page is a
  plain list of paper cards, each a doorway to its paper's page
- screenshot images are files stored beside the JSON and referenced from it — the
  JSON stays the source of truth for their captions, locators, and grouping, and
  the render copies the files into the site
- no graph visualization — the purpose is reading; the graph is walked page by page,
  never drawn as a diagram
- the site is always regenerated from the JSON, never hand-edited

## The algorithm

Rules that bind every stage:

- agents do every step; workers never write the shared store — they stage, and a
  central merge applies the staged work sequentially
- the merge validates before writing — everything referenced exists (staged image
  files included), every concept has a theme, every figure has a classification,
  once written a page, and a place in its paper's experiments story, every edge
  has prose, every claim has its locator — and writes nothing if any check fails
- a human reviews at every stage boundary
- worker prompts are self-sufficient — the rules, the register, where to stage — a
  fresh context cannot "follow conventions" it has never seen

```
start with three papers

1  concepts        one agent per paper, in parallel:
                     read end to end, extract everything named    (dense paper ⇒ 30–50+)
                     classify each: introduced / refined / inherited
                     stage an inventory
                   review the inventories before any page is written
                   merge into one canonical registry              (one concept = one page, corpus-wide)

2  figures         one agent per paper, in parallel:
                     crop every figure and every table
                     classify each: data and experiments /
                     results and interpretation                   (setup mixed with results ⇒ results)
                     stage an inventory of crops
                   review the crops and classifications before any page is written
                   merge into the figure registry                 (figures stay scoped to their paper)

3  themes          one mind — never parallelized — designs the themes
                   over the whole pooled concept set

4  edges           agents in parallel, one grouping each:
                     concept → concept edges among co-members of a family or theme

5  superthemes     one mind groups the themes into superthemes

6  super edges     agents in parallel, one supertheme each:
                     theme → theme edges among its member themes

7  connective themes   one mind groups all the edges into lenses

8  concept pages   agents in parallel, written only now, with the lenses
                   and the edges in hand:
                     how the concept fits the overall picture,
                     what it enables downstream,
                     what it actually is                          (inherited ⇒ full page, labeled inherited)

9  paper stories   first, one mind designs the chart-form shelf over the
   and figure      whole figure pool; its explainer pages are written once
   pages           then agents in parallel, one paper each, with the whole
                   graph in hand:
                     three tellings — inside the paper, across the
                     corpus, the big picture                        (place existing nodes; invent nothing)
                     a page per figure — what is going on in it,
                     locator, concept links; results figures also
                     taught as visualizations: how to read them,
                     where a naive reading goes wrong               (link the chart-form page, add the specifics)
                     the experiments story — the experiments and
                     results explained as one arc whose nodes are
                     the paper's concepts, every figure attached
                     once as evidence, linking the figure pages

10 render          regenerate the static HTML site from the JSON —
                   rerun after any change to the data

when a new paper joins:
                   run stages 1 and 2 for it, rebuild the lens layers over the
                   enlarged pool — the right lenses over three papers are not
                   the right lenses over twenty — then rerun the stages after
                   them, the new paper's stories, figure pages, and experiments
                   story included (coverage is total, so they land in the same
                   merge as its concepts); revisit the chart-form shelf, since
                   the new figures may repeat a form or bring a new one
```

Everything below is explanation.

## The graph, explained

### Concepts, and their hierarchy

A concept is anything a paper names that a reader might want to look up: an
architecture, a mechanism inside it, a training technique, a dataset, a benchmark, a
baseline it compares against. Every concept gets a page of its own, and those pages
are the body of the wiki — each one explains its idea from the ground up.

Concepts nest. Papers name things inside other things — an architecture is built from
components, a component has a particular computation at its core. When such a part is
genuinely nameable on its own and there is a page's worth of substance to say about
it, make it its own concept, marked as part of its parent, and let its page say how
the part serves the whole. When it isn't, it stays a passage inside the parent's page.

How deep to keep going is a judgment about relevance. A concept at the center of the
corpus — one that later papers build on, that edges keep touching, that the reader
will arrive at again and again — rewards decomposition level after level, because
there is real machinery inside it and readers will want it opened up. A concept met
once, in passing, stays a single page no matter how much could technically be said
about it. So most concepts don't split at all, a few central ones go deep, and both
outcomes are correct.

The hierarchy gives the reader vertical movement: descend from a big idea into its
parts to see the machinery, or climb from a detail to its parent to see what it is
for.

### Edges

Concept pages alone let the reader move only up and down that hierarchy. But almost
everything a paper actually argues is a sideways relation: this technique stabilizes
the training of that architecture; that earlier result was the bottleneck that
motivated this design; these two methods were ablated against each other. Edges are
where those relations live.

The prose is the point of an edge. It must teach the reader something real about how
the two concepts bear on each other, something neither concept's own page already
says. That is the test of an edge: if its prose only restates the two pages it
connects, it adds nothing — cut it.

Every edge is a page of its own. When the reader clicks a connection, they don't just
jump to the other end; they land on the edge's page and read those sentences first. In
this wiki, connections are not bare links — each one is something you read.

Name each relation from the situation itself, as a verb phrase that reads from source
to target. There is no fixed list of relation types to choose from. Reuse a name when
its meaning genuinely recurs; coin a new one when it doesn't. And when a relation is
only visible in hindsight — something no one could see until a later paper existed —
ground it in that later paper and flag it, so the reader knows when this understanding
arrived.

### Themes, and superthemes

Concepts and edges make the wiki walkable, but only one step at a time. What the
reader still lacks is a way to see concepts together — because some concepts belong to
the same story even though they sit far apart in the hierarchy and no single edge ties
the whole group. A benchmark, a metric, a dataset, and an evaluation trick may live
under four different parents and yet be one story about how the field measures
progress.

A theme is that story made navigable: a named group of concepts with a short narrative
that names its members and states its claim.

The word "claim" is doing real work there. A theme is a lens, not a category.
"Datasets" is a category — it files things and teaches nothing. "How the field
measured progress, and what the benchmarks actually test" is a lens — it tells the
reader what they will understand if they read its members together. Every theme must
earn its place the second way.

Two rules follow from treating themes as lenses. Membership is non-exclusive: a
concept belongs to every lens that illuminates it. And coverage is total: every
concept belongs to at least one theme, so no page is ever a dead end with no way
outward.

How many themes? Roughly one for every five concepts. Fewer, and each lens has to
stretch over too much ground to keep a single claim; many more, and the lenses shrink
toward categories with too few members to connect anything. Treat the ratio as a
target, not a law — it sets the order of magnitude for lenses that both say something
and hold a real group.

This is what themes buy the reader: different lenses through which to explore the same
corpus. The hierarchy is one path through the material. Each theme regroups the same
concepts into another path, and concepts that sit far apart vertically turn out to be
neighbors when seen through the right lens.

Superthemes are the same move one level up — lenses over the themes, non-exclusive in
the same way, each making a claim of its own.

### Super edges

Relations do not stop at the concept level. Once themes exist, pairs of themes bear on
each other the way pairs of concepts do: one theme's story creates the conditions the
next one's runs on; two lenses explain the same shift from opposite directions. A
super edge is an ordinary edge moved one level up — it connects two themes, has a
type, carries prose, renders as its own page, and is held to the same standard: its
sentences must say something neither theme's narrative already says. Superthemes
supply the pairs: super edges are written among themes grouped under the same
supertheme.

### Connective themes

One pattern is still invisible. The edges themselves, read together, have shapes of
their own: several edges across the corpus may all be displacement stories, where a
new method pushes an old one out; several may be stabilization stories; several may
trace a benchmark slowly losing its meaning. No grouping of concepts can surface this,
because the pattern lives in the relations, not in the things related.

Connective themes apply the lens idea to the edges — edges are the wiki's
connections, hence the name. A connective theme groups edges under a claim, with the
same kind of short narrative, so that *how things connect* becomes something the
reader can browse in its own right. (Internally these are still stored under the
`tissueThemes` key and rendered under `site/tissue/` — only the reader-facing name
changed.)

The recursion ends here. Do not build edges between edges — the connective theme's
narrative does that connecting work in prose.

### Paper stories

Every structure so far cuts across the papers; the story pages restore them. A paper
is the entry point a reader actually arrives with — they come having heard of a
paper, not of a lens — so each paper's page of stories retells its material as rooted
trees the reader opens level by level, with connective narrative at every branch.
Three tellings per paper: the paper's own arc chapter by chapter, its ties to the
other papers, and its place under the superthemes.

A story is placement, not invention. Its nodes reference concepts, themes,
superthemes, and connective themes that already exist, which is why stories are
written last of all, with the whole graph in hand — a story can only place what is
already there. Its prose stays in the grounded register: papers named by year,
documented relationships only, no framing metaphors coined for the telling.

An earlier design carried corpus-wide tellings as well — the whole corpus regrouped
under one claim per telling. They were removed: readers enter through papers, not
through the corpus, and every corpus-wide telling had to be rebuilt each time a paper
joined. Stories are per paper only.

### Figures and tables, and the experiments story

The tellings retell a paper's argument in prose; the figures are the paper's own
evidence, and they get the same treatment as everything else the reader might want to
look up: a page each. Every figure and every table in a paper — total coverage, for
the same reason concepts get it: the reader meets each one in the text and expects it
to lead somewhere.

A figure is concept-like but not a concept. It is scoped to one paper, it is found by
looking rather than by naming, and no lens needs to cover it — so figures are their
own node type, extracted by their own per-paper stage rather than during concept
extraction. A figure page links its paper's concepts in prose and concept pages may
link back, but figures carry no typed edges and join no themes; their way outward is
their paper and their concept links. The extraction stage mirrors the concept stage:
one agent per paper crops every figure and table, classifies each as apparatus or
outcome, and stages an inventory of crops that the human reviews before anything is
built on it — the same cheapest-review-surface logic as the concept inventories. The
crops are proposals; the review accepts or replaces them before the merge writes
anything.

The classification is a two-way split. Data-and-experiments takes the apparatus:
architecture diagrams, data and data-collection figures, experimental-setup figures,
setup-only tables — hyperparameters, dataset statistics, model configurations.
Results-and-interpretation takes the outcomes: results plots, results tables,
heatmaps, anything that shows or interprets how the work came out. A figure that
mixes setup with results is results-and-interpretation — every figure has a home, so
nothing is dropped. The classification creates no sections of its own; it marks
which figure pages owe the reader the visualization teaching described below, and it
tells the story writer what is apparatus and what is outcome.

On the paper's page the figures are met through the experiments story, a telling
beside the others: a self-contained account of the paper's experiments and results,
read the way the tellings are read, not browsed as a list. A section that lists
each figure as an independent entry loses exactly what makes the experiments worth
reading together — experiment two exists because of what experiment one left open,
the robustness checks exist because of what the headline result could be accused
of. And a story whose nodes are the figures themselves fails the same way from the
other side: the prose degenerates into captions, and the explanation never
happens. So the spine of the story is the explanation. Its chapters follow the
paper's experimental logic, saying what question each experiment answers and what
the answer was; the nodes under them reference the paper's concepts — the method,
the measures, the baselines, the tasks — each node's prose explaining that
concept's role in this experiment and what came out, with the paper's documented
numbers, so the graph the reader has been walking is the same material the story
is made of. The figures and tables attach to those nodes as supporting evidence: a
thumbnail beside a short note tying the figure to the claim it supports, linking
the figure's own page. Every figure is attached exactly once and never becomes a
node of its own. Depth lives on the figure page, so the story stays readable end
to end.

A figure page carries the cropped image and fresh prose in the grounded register —
what is going on in the figure — with the standard locator; the paper's original
caption is not reproduced. Results figures take extra care, because a results plot is
a reading skill as much as a fact: before stating what the paper concludes, the page
explains how the visualization itself works — what the axes and encodings mean, how
to read what is shown, and where a naive reading goes wrong.

Visualization forms recur, and the lesson should not. Recurring forms — the heatmap,
the coefficient-sweep line plot — get one shared explainer page each on a standalone
chart-form reference shelf, outside the concept pool, exempt from theme coverage;
each figure page links its form's page and adds only what is specific to this figure.
Choosing which forms earn a page is the lens-design move again — a judgment that is
only right relative to everything it covers — so one mind makes it, over the whole
figure pool, before the figure pages are written.

The timing follows from what each half needs. Cropping and classifying need only the
paper, so the figure stage runs early, right after concept extraction. Writing needs
the graph — the prose places figures against concepts, and the chart-form shelf needs
the whole figure pool — so figure pages, the shelf, and the experiments story are
written in the late batch alongside the stories.

The images appear only in the experiments story and on the figure pages; concept pages
stay prose. The no-graph-visualization rule is untouched — these are the papers' own
figures reproduced for reading, not diagrams drawn for the wiki.

### How everything is written

Write objectively and foundationally: intuition first, then the real mathematics, with
rendered equations wherever the concept is mathematical. Plain declarative sentences;
precision over cleverness.

Every name is a plain descriptive label, because names are how the reader navigates.
Scanning a list of links, they should know what each one is about before clicking; a
name that needs its own page to decode has already failed.

Give each page the sections it actually needs rather than forcing a template. And keep
the important relations in the page's own prose — a page says in sentences what it is
part of, what it works with, and which themes it belongs to. Links supplement that
prose; they never replace it.

### The store and the site

The extracted data lives in JSON, and the JSON is the single source of truth: the site
is regenerated from it after any change and never hand-edited, so no fix ever has to
be made in two places. The screenshots are the one binary artifact the store carries:
the image files live beside the JSON, which references them and remains the source of
truth for their captions, locators, and grouping; the render copies the files into the
site.

What gets rendered is static HTML — a real page for every concept, every edge, every
lens, linked to each other. Not a graph visualization: a diagram of nodes and lines
displays the graph's shape but cannot be read, and everything of value here is prose.
The reader experiences the graph the way this whole design intends — by walking it,
page to page.

## The algorithm, explained

Why start with three papers rather than the whole corpus? Because the first run
calibrates everything — granularity, voice, what a good lens looks like — and
calibration mistakes should be caught while they are cheap. Three papers are enough to
exercise all the cross-paper machinery (shared concepts, corpus-wide lenses) while
staying small enough to reread and redo.

### Extraction

Extract everything named. The rule is for the reader, who will meet every one of those
names in the text and expects each one to lead somewhere — a missing page breaks their
path. Thirty to fifty concepts from a dense paper is normal, not excessive.

Extraction parallelizes by paper (as does the figure stage after it), because at this stage the
papers are independent: one agent, one paper, staged separately. Where two papers name
the same thing, the merge resolves it under the corpus rule: one canonical concept,
one page. A later paper's contribution — its own role for the concept, its own
specifics — merges into the existing page rather than spawning a near-duplicate, so
the reader lands on the same page no matter which paper they arrive from.

The inventory is reviewed before any pages are written because it is the cheapest
review surface in the whole pipeline: an error caught there costs one line, while the
same error caught after themes, edges, and pages are built on top of it costs a
rebuild. Inherited concepts — things the papers use but did not invent — get full
pages written from general knowledge, labeled inherited until their origin paper is
processed, never a stub. The reader doesn't care where a concept originated; they hit
an unfamiliar name and want a real explanation.

One consequence of locators for your tooling: whatever cleaning you do to the source
text must preserve section headings and page markers, or locators become impossible to
record.

### Lens design

Themes, superthemes, and connective themes are all the same kind of act: choosing the
lenses. Two things follow.

First, lens design needs its full material before it starts. A lens is right or wrong
relative to everything it has to cover — which is why themes wait until every paper's
concepts are extracted and pooled, and why connective themes wait until all the edges
exist. Design lenses over a third of the corpus and you are guessing about the rest.

Second, lens design is one mind, never parallelized. Split the job across workers and
each invents lenses that overlap and near-duplicate the others', because each judged
only a fragment — and no merge can reconcile competing lens sets after the fact.
Parallelize the writing within a settled design as much as you like; the design itself
is a single global judgment.

### Why edges come after themes

An edge needs a pair, and pairs are the problem: even a hundred concepts offer five
thousand possible pairs, almost all of them meaningless. The groupings are what make
the pair space worth working: sub-concepts of one family, concepts sharing a theme,
themes sharing a supertheme — these are exactly the neighborhoods where real relations
live. That is why themes are designed before any edge is written (the groupings
generate the pairs), why super edges wait for superthemes, and why connective themes come
last of all: they group the edges, which have to exist first.

### Why concept pages are written last

A concept page written at extraction time can only say what the thing is, because
that is all that exists yet. Written after the lenses are designed and the connections
are in place, the writer holds the whole picture: the themes the concept serves, the edges
that touch it, everything downstream that was built on it. That is what lets the page
do its three jobs — say how the concept fits the overall picture, what it enabled
downstream, and what it actually is. The first two are the ones a reader cannot get
from the original papers, and they are impossible to write well in isolation.

### Agents and the shared store

Every stage is agent work, so one rule protects everything: workers never write the
shared store. Each worker stages its additions in its own file. A single central merge
applies the staged work sequentially, resolves duplicates, and validates before
writing; if any check fails, the merge writes nothing.

Write each worker's prompt as if for someone who has never seen the project — because
that is exactly what a fresh agent context is. It cannot follow conventions it has
never seen, so the prompt itself must carry the rules that govern the task, the
register to write in, and exactly where to stage the output.

## The test

For every page you build — concept, edge, or theme — ask two questions. **Would a
motivated reader want to read this? And having read it, can they keep moving toward
whatever caught their interest?** Validators catch structural problems: broken
references, missing coverage, absent prose. They cannot catch a page that passes every
check and is still not worth reading. Only reading catches that. Read what you build.
