# Review: user UI manifesto

**Created:** 2026-08-29
**Reviews:** [user-UI-manifesto.md](user-UI-manifesto.md)
**Author:** Claude (planner/verifier)
**Status:** analysis — not a plan, and not promoted into project truth
**Companion:** [review-user-UI-manifesto.md](review-user-UI-manifesto.md) — Codex's
review, written in parallel. **Read that one for what the workspace could look
like** (proposed layout, tool inventory, data model, nine-step user flow,
implementation slices). **Read this one for what the manifesto means for the
project as it stands** — what already exists, what it collides with, the one
architectural question underneath it, and when to build it.

> **Note on the filename.** You asked for the response as
> `user-UI-manifesto.md`, but that is your document. Overwriting it would have
> destroyed the source I was asked to review. This folder's README already
> defines `review-<slug>.md` as *"Claude's analysis of an idea: rating, gaps,
> open questions"*, so the response lives here, beside yours.

---

## 1. The headline: this is not a new direction

The most useful thing I can tell you is that this manifesto is **not a pivot,
and not a new project.** It is a much more detailed articulation of something
your own baseline already names.

`docs/project/description.md` section 4:

> **Use Case 2: Start From An Idea.** The user does not yet have all hardware in
> hand, but has a mission and design intent... The system should help collect
> requirements, compare candidate components, track datasheets and sources,
> reason about electronics and mechanics, and then turn selected components into
> the same structured measurement and design flow used by Use Case 1.
>
> This use case is important, but **it depends on stronger provenance rules.**

Your example journey — three motors, a flight controller, ESCs, a written
project document, "what hardware is missing and why" — is UC2, described in far
more operational detail than the baseline ever managed.

That matters for three reasons:

1. **You do not need to re-decide the project's identity.** The manifesto fits
   inside it. What it does is make UC2 concrete enough to plan against, which
   the baseline never did.
2. **The roadmap already placed it.** Phase 9 is *"Operate: second project; UC2
   groundwork — designing from a mission rather than from parts in hand, now
   that there is a provenance discipline to keep sourced data from contaminating
   measured data."* That is this manifesto, one sentence long.
3. **The precondition the baseline set has been met.** UC2 was gated on
   "stronger provenance rules." Those now exist, and I do not think you have
   noticed how much of one you already have.

**Rating: 8/10 as direction. 3/10 as something to start now.** The gap between
those two numbers is the whole review.

---

## 2. More of this is already built than the manifesto assumes

Going through your tool list against the repository:

| Manifesto asks for | Status today |
|---|---|
| Distinguish guessed / AI-inferred / user-provided / measured / verified | **Exists.** `docs/knowledge/capture-candidates.md` defines five verification states and five sources, including `ai-derived` — *"never promote without another source"* |
| Measurement panel | **Shipped.** Phase 2, browser and terminal |
| Report panel | **Shipped.** Ten checks with verbatim reasons, recomputed on every save |
| Components list with name/dimensions/weight/position/source/status | **Half.** `components/loadout.yaml` has name, mass, position. No source, no status, no dimensions |
| Decision log — why choices were made, alternatives rejected | **Exists, and is better than you are giving it credit for.** `docs/project/architecture.md` records D1–D15 in a fixed format: Options / Decision / Why / Cost / **Revisit when**. Two of them were reversed this week with the original reasoning preserved |
| Final report explaining what was built and why | **Format exists.** `docs/reports/` with a section contract; two written |
| Project document viewer, showing which design came from which requirement | Not started |
| Requirements + missing-parts analysis | Not started |
| 2D/3D viewers | Roadmap Phase 7, slot reserved in the UI |
| Digital measuring tools (ESP32) | Not started |
| AI chat in the workspace | Deferred by decision D13 |

**The single most valuable existing asset for your manifesto is the provenance
vocabulary**, and it is not in the UI at all yet. You already decided that an
AI-derived number can never become a measured one without a second source. Your
manifesto's entire section 5 — "the system should distinguish between guessed,
AI-inferred, user-provided, measured, and verified data" — is that decision,
already made, waiting to be surfaced.

The second most valuable is the decision-record format in `architecture.md`.
Your "decision log" tool does not need designing. It needs *rendering*.

---

## 3. The one question that decides everything: who solves?

This is the question I most want you to answer, because every other design
choice depends on it and the manifesto does not address it.

Right now, `geometry.py` **solves** the frame. Given prop diameter, plate size,
and motor dimensions, it computes the shortest arm length that clears
everything, and `validate.py` checks ten physical rules against the result. That
is why the current system is trustworthy: the numbers are derived, not
suggested, and a wrong input produces a visibly wrong output.

For a general "physical skeleton" system covering mechanics, electronics, and
3D, there are three possible answers and they are three different products:

**(a) A solver per domain.** Someone writes `geometry.py` for quadcopters,
another for fixed-wing, another for enclosures. The system is a platform; each
domain is a plugin with its own solver and its own validation rules.
*Trustworthy, slow to expand, and each new domain is real engineering work.*

**(b) The AI solves.** The model proposes dimensions and layout from the project
document. *Fast, general, and it destroys the property that makes this project
worth having.* An AI-proposed arm length is `ai-derived` by your own vocabulary
— it can never be promoted without another source, so every number would need
verification anyway, and there is no `validate.py` to verify it against.

**(c) No solver — the system organises evidence, the human designs.** It
captures requirements, tracks components with provenance, holds measurements,
renders models the user builds, and produces the final report. *Genuinely
useful, much easier, and honest about what it is.* This is closest to what your
tool list actually describes: viewers, lists, logs, panels. Note that almost
none of your listed tools solve anything.

**My read: your tool list describes (c), your section 1 philosophy describes
(b), and the only thing you have working today is (a).** That is the tension to
resolve before any of this gets planned. It is not a small design detail — it
determines whether "missing hardware analysis" means *"a checklist derived from
a domain model"* or *"the AI's opinion, labelled as such."*

I would push you toward **(a) for anything load-bearing, (c) for everything
else, and (b) never for a number that ends up in a cut file.** The AI proposes;
the solver decides; the caliper confirms.

---

## 4. Where the manifesto collides with existing decisions

Three places. None fatal, all worth resolving explicitly rather than by drift.

### 4.1 Knowledge capture — section 1 versus the scope split

Your section 1 says each sub-system can *"use AI and its own knowledge-capture
sub-project to create, accumulate data, store what was learned, and improve over
time."*

`docs/brainstorming/decision-scope-split.md`, decided 2026-08-28 and elevated
into `CLAUDE.md` as a hard rule:

> **This project makes things; it does not remember them.** Do not build an
> extractor, a component library, or a promotion mechanism here.

Your section 1 reads as though each sub-system gets its own memory. Your later
sentence — *"This project creates the physical design and the evidence behind
it; the knowledge system stores and organizes what was learned"* — is the
opposite, and matches the decision.

**Question 1 for you:** which is it? One shared knowledge system across all
sub-systems, or one per sub-system? I would argue hard for one shared: the whole
value of accumulated learning is cross-project comparison, and a per-subsystem
memory is a silo that has to be merged later anyway.

### 4.2 "AI chat as one of the main tools" versus D13

`architecture.md` D13 defers in-app AI and specifies it *"so it is not
improvised later."* The manifesto puts AI chat at the top of the always-visible
tool list.

That is a legitimate re-decision, but it is a re-decision. It also has a
consequence the manifesto does not mention: **this project currently makes no
outbound network calls at all.** The page works offline; a test enforces it. An
in-workspace chat is the first thing that breaks that, and it needs an entry in
`docs/protocol/trust-boundaries.md` before it is built, not after.

### 4.3 A components list with dimensions versus the single source of truth

`params.yaml` is the single source of truth, and `geometry.py` solves once from
it. A general components list holding dimensions creates a second place where a
dimension can live. That is exactly the drift the project's rules exist to
prevent.

Solvable — the components list should *reference* the parameter, not copy it —
but it needs saying before someone builds a component record with a `width_mm`
field in it.

---

## 5. The risks I would name now

**Conditional output is a hard UX problem, not a feature.** "Show the right
thing at the right time" fails in one specific way: the user cannot find a tool
because the system decided it was not relevant, and now they distrust the whole
workspace. Every conditional interface needs an escape hatch — a "show
everything" mode, or user pinning that overrides the logic. Decide that up
front, because retrofitting it means rewriting the layout engine.

**Document analysis is the load-bearing step and the least specified.**
Everything downstream — requirements, missing parts, constraints, next decisions
— depends on extracting structure from prose. It is also the step most likely to
produce confident, plausible, wrong output. Your own rule already handles this:
extraction lands as **proposals the user confirms**, tagged `ai-derived` /
`unverified`, never as facts. Build it that way from the first commit or it will
never be retrofitted.

**Generality has a cost you have not priced.** The current system is trustworthy
because it is narrow. A quadcopter solver knows what a prop is. The moment the
system accepts "any physical skeleton", either the solvers multiply or the
trustworthiness goes away. There is no third option.

**This is a very large amount of tooling designed against zero completed
builds.** Your own roadmap makes this argument better than I can, about the 3D
viewer:

> Building it **after** a real measurement session means it is designed against
> remembered frustration rather than imagined need.

The manifesto describes an entire product designed against imagined need. The
frame is not cut. Nothing here has been through one complete cycle, so every
tool on the list is a guess about what that cycle requires — including the ones
that turn out to be unnecessary, which you cannot identify yet.

---

## 6. Answers to your nine questions

You asked. These are positions, not conclusions.

**What should the ideal project-document format look like?**
Not prose the AI parses — a structured document with prose *inside* it. Mission,
constraints (hard vs preferred), hardware in hand with provenance, hardware
assumed, materials available, success criteria, and explicit non-goals. The AI's
job becomes filling gaps and challenging assumptions, not divining structure.
Model it on `docs/project/description.md`, which already does this well for one
project.

**What must the user provide before physical design can begin?**
Minimum: the mission, the hardware genuinely in hand, the material stock
available, and at least one hard constraint that bounds the design. This project
had exactly that — a 250×250mm sheet and a salvaged parts pile — and it was
enough. Without a bounding constraint, there is nothing to solve against.

**What tools should always be visible?**
Three. What am I building (project/requirements), what state is it in (report or
equivalent), and what do I do next (the queue). That is the shape the Phase 2
workstation already landed on, and it earned it.

**What should appear conditionally?**
Anything tied to an artifact that does not exist yet. No blueprint viewer before
a blueprint. But conditional should mean *dimmed and one click away*, not
absent — see the risk above.

**What data model should components use?**
Per-field provenance, not per-record. `capture-candidates.md` already specifies
it: every dimension carries `value`, `source`, `verification_state`,
`verified_by`, `evidence`. One physical part legitimately mixes a caliper
measurement, a datasheet figure, and a vendor claim. A single record-level
"measured" flag would be a lie about most components.

**How should the system mark guessed/measured/verified/AI-inferred?**
Already answered by the same file. `unverified / measured / tested / verified /
rejected` for state; `caliper / datasheet / vendor-claim / estimated /
ai-derived` for source. Do not invent a second vocabulary. Surface this one in
the UI.

**How should the UI connect a visual model to measurements and decisions?**
Both directions, and the second is the valuable one. Click a dimension in the
model → see the measurement, its source, and the decision that used it. Click a
measurement → the model highlights what it controls. Phase 7 already reserves
`shape_hint` for the first half.

**What should be in the final report template?**
`docs/reports/README.md` already has a section contract. It needs three
additions for your vision: alternatives considered and rejected, per-decision
evidence links, and an explicit "what still needs improvement" section. Your
manifesto's section 6 list is close to right already.

**Which parts belong here versus the knowledge system?**
The line already drawn holds: this project **makes** and **records with
provenance attached**; the knowledge system **normalises, deduplicates, links,
and decides what is reusable**. Under that line, everything in your manifesto is
in scope for this project except "accumulate data, store what was learned, and
improve over time" — which is the knowledge system's entire job.

---

## 7. What I would actually do

**Finish the frame first.** Not as a formality — as the thing that makes this
manifesto writable. Right now it describes a workspace for a process nobody has
completed once. After Phase 3 (measure) and Phase 6 (cut, assemble, fly), you
will know which of these twenty tools you actually reached for, which you never
opened, and which one you needed and did not have. That is a different and much
better document, and it costs weeks rather than months to obtain.

The concrete cost of building this first: you will build the material-comparison
tool, the hardware-compatibility checker, and the mechanical-stress notes panel,
and I would bet against at least one of them surviving contact with a real
build.

**Then, in this order:**

1. **Promote the provenance vocabulary into the UI.** Small, high value, uses
   what exists. Every component and measurement shows its source and state. This
   is the foundation every other tool in your list depends on, and it is
   probably a week.
2. **Structured project document + requirements extraction, as proposals.** The
   riskiest piece, built with confirmation from the first line.
3. **Components list with per-field provenance**, referencing parameters rather
   than copying them.
4. **Decision log rendered from `architecture.md`'s existing format.**
5. Everything else, ranked by what the first real build proved you needed.

**One structural suggestion.** If the larger vision is many sub-systems merging
into one creation system, the boundary that matters is not the UI — it is the
**contract between a sub-system and the shared knowledge store.** That contract
exists in draft: `docs/knowledge/capture-candidates.md`. Exercising it once, on
real output from a finished build, will teach you more about the merged system
than designing five more workspaces. Roadmap Phase 6 already requires exactly
that, and calls the awkwardness you discover *"the feedback the future knowledge
project needs and cannot get any other way."*

---

## 8. Questions back to you

1. **One knowledge system or one per sub-system?** (section 4.1)
2. **Who solves?** (a) domain solvers, (b) the AI, or (c) nothing — the system
   organises and the human designs. (section 3)
3. **Is the merged creation system a real near-term goal, or a north star?** The
   answer changes whether this project should be generalised now or finished
   narrow and generalised later.
4. **What does "reality-proof" mean to you concretely?** You used the phrase in
   section 1 and I think it is the most important word in the document, but I
   cannot tell whether it means *"validated against physics"*, *"buildable with
   the tools I own"*, or *"proven by having built it once."* Those imply
   different systems.
5. **Does in-workspace AI chat justify the first outbound network call in a
   project that is currently entirely local?** (section 4.2)
6. **What did you actually dislike about the Phase 2 UI?** You have the only
   copy of that information, it is worth more than any of the above, and it
   expires quickly.

---

## 9. Verdict

This is a good document and a real vision, and it is more aligned with what you
already decided than it appears — it is UC2 with the detail filled in, and the
provenance precondition UC2 was waiting on now exists.

Its weakness is not ambition. It is that it specifies a workspace for a process
that has not been performed once, which is the exact failure mode your own
roadmap was written to prevent. The fastest route to a good version of this
document is a cut, assembled, flown frame and the notes you take while
struggling with the current tools.

**Recommended routing:** hold as brainstorming. Do not promote into
`docs/project/` and do not plan against it yet. Revisit after roadmap Phase 6,
with the build log open beside it.
