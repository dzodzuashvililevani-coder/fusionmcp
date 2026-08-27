# Review: the ICM research paper, and what it means for this project

**Created:** 2026-08-27
**Reviews:** Interpretable Context Methodology (arXiv:2603.16021)
**Requested in:** `docs/brainstorming/idea-user-1.md` (Q1 of `review-user-1.md`)
**Author:** Claude (planner/verifier role)
**Status:** reference + analysis

---

## 0. Provenance -- what I actually read

Be aware of this before trusting anything below.

| Source | Reached? | What it gave |
|---|---|---|
| `skool.com/cliefnotes/icm-research-paper` | **No** | Login-gated. Only a teaser paragraph was public |
| arXiv:2603.16021 abstract page | Yes | Authors, dates, abstract, paper metadata |
| arXiv HTML full text (v2) | Yes | Layers, contract format, limitations, evaluation |
| `filesnfolders.com` plain-English explainer | Yes | Independent restatement; MWP-vs-ICM naming |
| `github.com/RinDig/Interpretable-Context-Methodology` | Yes | Reference folder layout, conventions list |

**The Skool link you gave me is behind a login I do not have.** The Claude
browser extension is not currently connected to this session, so I could not
read it through your own logged-in browser either. If that post contains Jake's
own commentary, community-specific conventions, or an Omnissiah-specific
adaptation, **I have not seen it**, and anything in there that contradicts this
document should win.

What I did instead was go to the primary source. Everything below is drawn from
the paper itself and two independent restatements of it, with facts
cross-checked across at least two sources before I state them.

If you want the Skool post read too, connect the Chrome extension
(`https://claude.ai/chrome`) and I will read it in your session.

---

## 1. What ICM is

**Interpretable Context Methodology**, by Jake Van Clief and David McDermott
(Eduba / University of Edinburgh). arXiv:2603.16021, submitted 17 March 2026,
v2 on 18 March. 28 pages, 5 figures, 2 tables, 54 references. Paper under
CC BY 4.0; the protocol itself released MIT.

Two names appear and they are not synonyms:

- **ICM** is the methodology -- the general idea and its justification.
- **MWP (Model Workspace Protocol)** is the concrete protocol -- the agreed
  layout that implements it.

The thesis, in my words: for sequential work where a human inspects the output
at each step, an orchestration *framework* is unnecessary overhead. If each
stage's prompt and context already exist as files in a well-organised
hierarchy, you do not need several coordinating agents -- you need one agent
that reads the right files at the right moment. Numbered folders carry the
execution order, markdown carries the instructions, and ordinary scripts do the
mechanical work that needs no AI at all.

Its stated intellectual lineage is Unix pipelines, modular decomposition,
multi-pass compilation, and literate programming. The Unix inheritance is the
load-bearing one: do one thing, make one stage's output the next stage's input,
and use plain text as the universal interface.

The consequence the paper is proudest of is legibility. Every intermediate
artifact is a plain-text file a human can open, read, and edit between stages.
The artifacts are the log; `ls` is the dashboard.

---

## 2. The five-layer context hierarchy

This is the part of the paper with the most transferable value. Context is
stratified, and each layer has a rough token budget:

| Layer | Name | Holds | Budget |
|---|---|---|---|
| **0** | Global identity | Workspace identity, folder-structure overview | ~800 tok |
| **1** | Workspace routing | Which stage handles what; shared resources | ~300 tok |
| **2** | Stage contract | This stage's inputs, process, outputs | 200-500 tok |
| **3** | Reference material | Stable knowledge: design systems, conventions, domain facts. Set up once, unchanged across runs | 500-2k tok |
| **4** | Working artifacts | Per-run content: prior stage outputs, user source material. Changes every execution | variable |

The distinction the paper draws between layers 3 and 4 is the sharpest idea in
it, and I will return to it in section 7 because **it is the answer to your
knowledge-capture question**. Layer 3 material is meant to be absorbed as
constraints and patterns; Layer 4 material is meant to be processed as input.
Same file format, completely different role.

The efficiency argument: a stage loading layers 0-4 selectively runs about
2,000-8,000 focused tokens. Loading everything monolithically -- all stage
instructions, all reference material, all prior outputs -- reaches 40,000+, most
of it irrelevant to the step actually executing. The paper leans on the
"lost in the middle" literature (Liu et al.) for why that irrelevant bulk is not
merely wasteful but actively degrading.

---

## 3. The stage contract: CONTEXT.md

Every stage folder carries a `CONTEXT.md` with three mandatory sections:

- **Inputs** -- which Layer 3 reference files and Layer 4 artifacts to load,
  with explicit paths, and which layer each belongs to. The convention is
  *selective section routing*: name the exact section of a file you need, not
  the whole file.
- **Process** -- the transformation. Numbered steps, which guidelines to follow,
  what the output should behave like.
- **Outputs** -- what files this stage produces, and where they go.

Stages doing creative work add two optional sections: **checkpoints** (pause for
human steering mid-stage) and **audit** (a quality checklist the agent runs
against its own output before writing it).

---

## 4. Folder layout and handoffs

The reference implementation looks like this:

```
workspace/
  CONTEXT.md            <- Layer 1: routing
  stages/
    01-research/
      CONTEXT.md        <- Layer 2: this stage's contract
      references/       <- Layer 3: reference scoped to this stage
      output/           <- Layer 4: handoff point to stage 02
    02-script/
    03-production/
  _config/              <- Layer 3: cross-cutting config
  shared/               <- Layer 3: cross-stage resources
  skills/               <- Layer 3: bundled domain knowledge
  setup/questionnaire.md
```

Two-digit prefixes encode execution order. The paper writes them `01_research`;
the reference repo writes `01-research`. Trivial, but pick one and be consistent.

**A stage answers "where in the job am I standing", not "what kind of thing is
this".** That is the distinction that matters most for us and I return to it in
section 6.

The handoff is the `output/` directory, and it is one-directional: stage 02
reads stage 01's `output/`. Between them sits a human review gate. You read what
stage 01 produced, edit it if you want, and stage 02 consumes whatever you left
there. That is the whole mechanism -- no message bus, no shared state, no
orchestration layer.

Fifteen conventions are codified in the reference repo's `_core/CONVENTIONS.md`.
The ones worth naming here: one-way references only, so no circular
dependencies; a canonical single source of truth for each fact; specifications
state *what* and *when*, never *how*; human checkpoints between creative units of
work; and agent-run audits before output is written.

There is also a **workspace-builder**: a meta-workspace whose job is generating
new ICM workspaces, with the contribution rule that new workspaces are generated
by it rather than hand-assembled.

---

## 5. What ICM explicitly does not do

The authors are unusually forthright about boundaries, and these matter for FCC.

- **Real-time multi-agent collaboration.** File-based sequential handoffs are
  too slow for tight-loop agent chatter. ICM is not for that.
- **High concurrency.** Many simultaneous users would need queueing, state
  isolation, and deployment infrastructure -- which contradicts its local-first
  premise.
- **Complex branching.** Humans can decide between stages, but programmatic
  mid-pipeline routing is awkward. The paper's own reasoning: automating
  branching pushes ICM back toward being the framework it set out to avoid.
- **Cross-model generality.** All testing used one model family (Claude Opus 4.6
  and Sonnet 4.6). Cross-model evaluation is named as future work.

### Evidence quality -- read this before adopting anything

I want to be direct, because you are about to build a system on this.

The paper's evaluation is **practitioner observation, not controlled
experiment**, and the authors say so plainly. The sample is an invite-only
community of 52. The headline finding -- 30 of 33 practitioners running
multi-stage workspaces reported a U-shaped editing pattern, heavy edits at the
first stage, light in the middle, heavy again at the end -- is self-reported
through conversation. Non-technical users successfully edited `CONTEXT.md` files;
three members with no coding background built complete pipelines. All
encouraging, none measured.

The authors state directly that no controlled comparison has been run between
ICM's staged context loading and monolithic prompting on the same tasks, and
they call for a formal user study.

**So: ICM is a well-argued design pattern with credible practitioner testimony.
It is not an empirically validated result.** Adopt it because its reasoning is
sound and because it matches what already demonstrably works in your repo --
not because it has been proven. That distinction will matter the first time it
does not fit and you have to decide whether to bend the method or the problem.

---

## 6. How ICM relates to what this repo already has

Here is the genuinely interesting finding. **Codex independently built most of
ICM into `docs/protocol/` before either of us mentioned the paper.**

### Where they converge

| Idea | ICM | `docs/protocol/` |
|---|---|---|
| Durable state is files, not chat | Artifacts are the log | "every durable handoff a file, never a conversation" |
| A gate between steps | Human review gate at each `output/` | Gate phase is a hard halt |
| Per-step contract | `CONTEXT.md`: Inputs / Process / Outputs | Plan phase: Definition of done / Touches / Commands |
| Plain text as interface | Markdown throughout | Markdown throughout |
| Canonical single source of truth | A convention | `params.yaml` rule in CLAUDE.md |
| Specs say what, not how | A convention | "Definition of done: observable, testable" |
| Scripts do the mechanical work | Local Python scripts | `fusion_scripts/`, `frame` CLI |

That convergence is worth something on its own: two independent derivations
landing in the same place is mild evidence these are natural attractors rather
than one author's taste. It also means **adoption here is cheap** -- you are
mostly renaming and extending, not rebuilding.

### Where they genuinely differ

These are real disagreements, not gaps.

**1. One agent versus two.** ICM's central claim is that you do *not* need
multiple coordinating agents -- one orchestrator reading the right files
suffices, and the reviewer at each gate is a *human*. `docs/protocol/` asserts
the opposite for its domain: the planner is not the implementer, and the
reviewer at the gate is a *second AI* with different instructions.

Both are right, for different work. ICM's single orchestrator suits *generative
pipeline* work, where the risk is context pollution and the human is the quality
check. The two-agent split suits *verifiable artifact* work, where the risk is an
agent marking its own homework and there is a deterministic check
(`pytest`, `frame check`) to appeal to.

FCC has both kinds of work. **Do not force one model onto both.** My
recommendation is section 8.

**2. Linear pipeline versus loop with failure branches.** ICM names complex
branching as a limitation. But `errorFix-<M>` *is* branching -- it is the
protocol's answer to "the gate failed, now what". ICM describes flow;
Plan-Gate-Verify describes failure. FCC needs both, and this repo already has
the half ICM lacks.

**3. Folders by stage versus folders by artifact type.** This is the one that
matters most for your "fit the ICM structure here" instinct, and I think it
needs a correction.

ICM's numbered folders encode *the execution order of a repeatable pipeline*.
This repo's folders (`src/`, `docs/`, `photos/`, `dxf/`, `cad/`, `components/`)
encode *kinds of durable artifact* that persist across every stage.

`params.yaml` is not a stage output -- every stage reads it. `photos/` is not
step 3 -- it is evidence consulted throughout. Renumbering these into
`01-measure/`, `02-model/`, `03-cut/` would break the thing that makes this repo
work, which is that there is exactly one canonical location per artifact type.

**But your two use cases genuinely are pipelines.** "Measure the part, produce a
2D plan, scale to 3D, refine, assemble" is a numbered stage sequence in the
precise ICM sense. So the resolution is not to choose -- it is to apply each
where it fits:

> **ICM stages structure the *process*. Artifact folders structure the *output*.
> Stages read from and write to artifact folders; they do not contain them.**

A stage's `output/` holds the *handoff* -- the working draft passing to the next
step -- while the durable result of the pipeline is promoted into `params.yaml`,
`cad/`, `dxf/`, `components/`. That keeps ICM's legibility and this repo's
canonical-location rule at the same time.

---

## 7. The part that answers your real question

In `review-user-1.md` I said the central unanswered question of FCC was *what,
precisely, is the unit of reusable knowledge* -- and that a stored number is
worthless unless something records where it came from and whether reality ever
confirmed it.

ICM has a name for the distinction I was reaching for, and it is better than
mine:

> **Knowledge capture is the promotion of a Layer 4 artifact into Layer 3.**

Read the definitions again against your own manifesto:

- **Layer 4** -- per-run, changes every execution, processed as *input*.
  That is a specific build. Build 001, the wooden frame, the motor you measured
  last Tuesday.
- **Layer 3** -- stable, set up once, unchanged across runs, internalised as
  *constraints and patterns*. That is your component library. The 18x18 motor.
  The Fusion technique you found the hard way. The mistake you will not repeat.

Your 18x18 motor example *is* a Layer 4 to Layer 3 promotion. It is measured
during one build (Layer 4), verified when the screws actually fit, and promoted
to reference material every subsequent build reads as a constraint (Layer 3).

This gives FCC three things it did not have this morning:

1. **A vocabulary.** "Promote to Layer 3" is more precise than "save it for
   later", and precise enough to build a command around.
2. **A location.** Layer 3 already has a home in the ICM layout (`shared/`,
   `skills/`, per-stage `references/`). The component library is not a new
   invention needing a new place; it is Layer 3 for hardware.
3. **A trigger, which is the part that was missing.** ICM says Layer 3 is
   "configured once during setup". For FCC that is wrong -- Layer 3 must *grow*,
   and the growth event is exactly the verification transition I described as
   gap 2 of the previous review. **A build finishing is a promotion event.**

That last point is where FCC actually extends ICM rather than merely adopting
it. ICM assumes a static reference layer configured up front. A hardware
knowledge system needs a Layer 3 that accumulates, with provenance
(caliper / datasheet / vendor-claim / estimated) and a verification state that
only a completed physical build can set.

**That extension is FCC's original contribution, and it is worth stating
plainly, because it is the thing the paper does not do.**

---

## 8. What I would adopt, adapt, and decline

### Adopt as-is

- **The five-layer hierarchy as vocabulary.** Even with no folder renamed,
  having names for "this is stable reference" versus "this is this run's working
  material" pays for itself immediately.
- **Selective section routing.** Name the section of a file a stage needs, not
  the whole file. Cheap discipline, direct token payoff.
- **One-way references, no cycles.** Already implicitly true here; make it
  explicit.
- **Agent-run audits before writing output.** This is the same instinct as
  `frame check`, applied to prose and design work instead of geometry.
- **The honesty about limits.** Copy the habit, not just the content.

### Adapt

- **Numbered stages, for the pipelines only.** UC1 and UC2 get numbered stage
  sequences. The artifact folders stay as they are. Section 6.3.
- **`CONTEXT.md` merged with the existing plan contract.** The repo already has
  Inputs/Process/Outputs by other names. Do not run two contract formats side by
  side -- reconcile them into one and say which ICM concept each field carries.
- **Layer 3 that grows.** Section 7. This is the real work.
- **The gate.** Keep the two-AI verification gate for anything with a
  deterministic check. Add ICM-style *human* review gates for design
  deliberation, where there is no test to appeal to.

### Decline, for now

- **The workspace-builder.** Generating workspaces from a meta-workspace is
  premature when you have one project. Revisit at the second.
- **Single-orchestrator for verifiable work.** You have two AIs and a working
  separation of duties. ICM's argument against multi-agent is about *coordination
  overhead*, not about *adversarial verification*, and it does not apply to a
  gate whose purpose is that the builder does not grade itself.
- **Wholesale folder renumbering of this repo.** Section 6.3.

---

## 9. How I understand ICM, in one paragraph

ICM is the observation that a filesystem is already a state machine, and that
most AI orchestration frameworks exist to rebuild -- in code, invisibly -- a
structure the filesystem gives you for free and legibly. If each step of a
workflow is a numbered folder, each step's instructions are a markdown contract,
and each step's output is a directory the next step reads, then coordination is
just an agent following a path, every intermediate state is inspectable and
editable by a human, and the mechanical work drops out to ordinary scripts. Its
deepest idea is not the folders, though -- it is the layering of context by
*stability*, separating what is permanently true about your domain from what is
merely true about today's run. That layer boundary is the one FCC should be built
on, because hardware knowledge capture is precisely the act of moving something
across it.

---

## 10. Open questions

**Q1.** Does the Skool post add anything the paper does not -- Jake's own
commentary, community conventions, an Omnissiah-specific adaptation? I could not
read it. Connect the Chrome extension and I will.

**Q2.** Does Omnissiah already implement ICM concretely -- numbered stages,
`CONTEXT.md` files, a layer split? If so, FCC should mirror its *skeleton* even
where hardware content differs. Two systems with the same bones are far easier
to live in than two with different ones. If you can show me Omnissiah's layout, I
will map FCC onto it rather than proposing a parallel invention.

**Q3.** Section 6.3 is a genuine fork in the road and it is your call: do you
want ICM's numbered stages applied to the *process* only, with artifact folders
left intact -- or did you intend the whole repo restructured ICM-style? I have
argued for the first. If you want the second, say so and I will plan it properly
rather than resisting it in pieces.

---

## 11. Routing

Nothing routes to `docs/codex/` from this document. It is reference material and
analysis, and it changes the shape of two plans already queued in
`review-user-1.md` section 10:

- `claudePlan-mission-invariants-1.md` -- the invariants/free-variables format
  is Layer 3 material in ICM terms, which sharpens where it lives.
- `claudePlan-protocol-deliberation-1.md` -- should now explicitly reconcile the
  existing plan contract with `CONTEXT.md` rather than inventing a third format.

Both stay unwritten pending your answers to Q2 and Q3 above.

---

## Sources

- Van Clief, J. and McDermott, D., *Interpretable Context Methodology: Folder
  Structure as Agent Architecture*, arXiv:2603.16021 (March 2026).
  <https://arxiv.org/abs/2603.16021> / <https://arxiv.org/html/2603.16021v2>
- Reference implementation:
  <https://github.com/RinDig/Interpretable-Context-Methodology>
- Plain-English restatement:
  <https://filesnfolders.com/blog/icm-paper-plain-english>
- Community post (login-gated, **not read**):
  <https://www.skool.com/cliefnotes/icm-research-paper>
