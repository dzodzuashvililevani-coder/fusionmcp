# Review: idea-user-1 -- the FusionControlCenter manifesto

> **SUPERSEDED IN PART -- 2026-08-28.** Knowledge capture is no longer this
> project's responsibility. It moved to a separate project; this repository only
> deposits finished products into named folders. Anything below that argues for
> building capture, promotion, component cards, or an extractor **here** no
> longer applies. See
> [`decision-scope-split.md`](decision-scope-split.md) for the authority.

**Created:** 2026-08-27
**Reviews:** `docs/brainstorming/idea-user-1.md`
**Author:** Claude (planner/verifier role, per `docs/claude/behaviour.md`)
**Status:** review -- returns questions, proposes a shape, routes nothing yet

---

## 0. How to read this

You asked for review, analysis, and my view, and you invited questions. This
document is all four, in that order. I am deliberately being a critic rather
than an enthusiast, because the manifesto is strong enough that flattery would
waste it.

The through-line: **your thesis is right, your sequencing is inverted, and your
single source of truth is not yet in a form that can be one.** Everything below
elaborates those three sentences.

---

## 1. What I read your manifesto as saying

Restated in my words so you can correct me where I got it wrong. If any of
these seven points is a misreading, that misreading has probably propagated
through the rest of the document.

1. **FusionControlCenter (FCC) is a development system plus a knowledge-capture
   system for hardware**, standing in the same relation to hardware work that
   Omnissiah stands in to software work.
2. **The captured knowledge is the point, not the drone.** Component models,
   2D plans, Fusion techniques discovered the hard way, mistakes not to repeat.
   The 18x18mm motor example is the archetype: model it once, reuse it forever.
3. **Two entry modes.** UC1: hardware in hand, measure it, build around it.
   UC2: no hardware, a mission statement, source and design from zero.
4. **A written project description is the source of truth** for any given build
   -- what it is, what parts, what material, what cutting method, and *why*.
5. **Two AIs collaborate under a written method** (`METHOD.md`, derived from the
   ICM paper), including a classifier that decides whether a requested change is
   a minor improvement or a major change that contradicts why the thing exists.
6. **A UI wraps all of it** -- measurement entry against animated dummy models,
   plus a page for brainstorming with the AIs and exchanging files. You open
   Fusion yourself; the system never drives it behind your back.
7. **The Fusion MCP server may need extending** to serve FCC's requirements.

---

## 2. Rating

I am rating the parts separately, because averaging them would hide the
problem.

| Element | Rating | One-line reason |
|---|---|---|
| Hardware knowledge capture as the core thesis | **9/10** | Correct, underserved, and you are unusually well placed to build it |
| Provenance-tracked reusable component library | **9/10** | This is the concrete form the thesis takes; see gap 1 |
| UC1: build around existing hardware | **8/10** | Has ground truth (calipers). Verifiable. Buildable now |
| Minor-vs-major change classifier | **8/10 or 3/10** | 8 if invariants are written down; 3 as open-ended AI judgment. See gap 3 |
| Two-use-case decomposition | **8/10** | These really are the two modes of hardware work |
| METHOD.md for AI-to-AI collaboration | **7/10** | Mostly already exists in `docs/protocol/`; needs extension, not creation |
| UC2: design and source from zero | **5/10** | Right ambition, wrong order, unsolved verification problem. See section 4.3 |
| Treating all of the above as one project | **3/10** | This is the main risk to the whole thing |
| Building it before finishing one physical build | **2/10** | Inverted dependency. See section 4.1 |

**Overall: a strong thesis with dangerous sequencing.** Nothing in the manifesto
is wrong about *what* is worth building. The risk is entirely in *what order*,
and the order implied by the document will, I think, produce five half-built
subsystems and zero captured knowledge.

---

## 3. What is strongest

### 3.1 The knowledge-capture thesis is correct, and more true for hardware than for software

Software has package managers, and reuse is close to free. Hardware has nothing
equivalent. You cannot `import motor`. Every project remeasures the same parts,
rediscovers the same Fusion behaviours, and repeats the same mistakes, and the
person who made the mistake usually cannot remember the detail three months
later. The asymmetry is real, and it means a hardware knowledge system has more
headroom than its software twin, not less.

The 18x18 motor example is exactly the right archetype: a dimensioned,
physically verified component model is a durable asset with a long half-life.
Most people keep these as loose `.f3d` files in a folder and lose the one thing
that mattered -- where each number came from and whether anything ever confirmed
it.

### 3.2 You are already running the loop, in miniature, and may not have noticed

`fusion_scripts/README.md` already says this:

> Explore with MCP. When something works, **lock it in as a script here** so the
> next frame does not need the conversation again.

That is your entire manifesto compressed into two sentences and applied to one
narrow domain: use the conversational tool to discover, then promote what worked
into a durable, versioned, repeatable artifact so the discovery is never
repurchased. FCC is that rule generalised from Fusion scripts to components,
techniques, decisions, and mistakes.

This matters for a practical reason: you are not starting from zero, and the
existing repo is evidence the thesis works. It is also a template for the shape
every other captured thing should take -- *ephemeral exploration promoted into a
durable artifact, on an explicit trigger.*

### 3.3 The minor-vs-major classifier is the best idea in the document

Most CAD work loses the *why*. The model records that a bracket is 3mm thick; it
does not record that 3mm was chosen because 2mm cracked during the last build.
Six months later somebody thins it to save weight and rediscovers the crack.

A system that asks "does this change contradict the reason this part exists?"
is capturing precisely the thing that normally evaporates. It is also the
highest-leverage form of knowledge capture, because it is *preventative* rather
than archival -- it stops the mistake instead of documenting it afterwards.

I have a specific proposal for making it work mechanically rather than
impressionistically: see gap 3.

### 3.4 Splitting hardware from Omnissiah is the right call

Hardware knowledge differs in kind from software knowledge. It has physical
units, tolerances, material properties, and a validator that cannot be argued
with. A shared abstraction over both would have to be so general it would be
useless to either. Two systems that exchange *method* but not *schema* is right.

---

## 4. What worries me, in order of severity

### 4.1 You cannot build a lessons-learned system before you have lessons

This is my central concern, and if you take one thing from this review, take
this.

Knowledge capture is a function of the form `completed project -> reusable
knowledge`. Right now the input to that function is empty. The state of the
repo, measured just now:

- `params.yaml`: **13 values still marked `TODO`**
- `components/loadout.yaml`: **6 more**
- `docs/measurements.md`: every blank still blank
- `docs/build-log.md`: no entries
- Nothing has been cut. No wood, no motor on a scale, no flight.

Every number in the design is currently a guess. `frame check` passes, which
means only that the guesses are self-consistent -- it says nothing about
reality. So a component library built today would have exactly one entry, and
that entry would be a motor nobody has measured.

There is a harder version of this problem. The knowledge most worth capturing is
the knowledge you do not yet know you need, and it is generated at exactly the
moments a build surprises you: the plywood that was 2.7mm and not 3mm, the
kerf that made every hole 0.2mm oversize, the CG that sat 4mm aft because the
battery strap was heavier than assumed. **You cannot design the schema for
lessons you have not had yet.** Any schema you write now will be a guess about
what surprises look like, and it will be wrong in ways you can only discover by
having the surprise.

**Recommendation: finish the drone frame as a physical object first.** Measure
the parts, cut the wood, build it, fly it, and log what went wrong. Then build
FCC around the shape of what you actually learned. The frame is not a demo for
the platform; it is the platform's first and only source of training data.

### 4.2 The manifesto describes at least five products

Counting what is in the document:

1. A measurement-capture UI with animated component models
2. A provenance-tracked component knowledge library
3. A multi-agent method specification (METHOD.md)
4. An AI design-review classifier with intent preservation
5. A component-sourcing research agent (UC2)

Each of those is a substantial project on its own. The manifesto treats them as
one thing because they share a motivation, but shared motivation is not shared
architecture. Built in parallel, the likely outcome is five subsystems at 60%,
none of which can be used, and the drone still uncut.

They also have real dependencies on each other that the document does not
acknowledge. (3) constrains (4). (2) needs (1) to have any contents. (5) needs
(2) to have somewhere to put its results. (4) needs a written mission statement
that does not currently exist for any project. That dependency graph is not a
constraint to work around -- it is the build order, and it is already almost
linear.

### 4.3 UC2 has an unsolved verification problem, and the manifesto does not name it

UC1 and UC2 look symmetrical in the document. They are not.

UC1's ground truth is a caliper. If you measure the bolt circle at 9.4mm, it is
9.4mm, and if you measure wrong you find out when the screw does not fit. The
feedback loop is short, physical, and unforgiving in a useful way.

UC2's ground truth is a vendor datasheet -- which may not exist, may be wrong,
may describe a different revision of the same part number, or may be marketing
fiction. This is not hypothetical for you specifically: **the hardware you are
actually working with is salvaged from a Temu toy drone**, which is the exact
category where no datasheet exists and any spec you find online describes a
part that merely resembles yours. The repo already knows this --
`photos/reference/README.md` says "treat everything here as unverified until
matched against a photo in `own/`" and warns that a pinout for a similar board
will destroy your flight controller.

Layer an LLM on top of that and you get a second failure mode: models confabulate
plausible specifications fluently. A hallucinated thrust curve does not announce
itself. It produces a design that validates cleanly, gets built, and does not
fly -- and the failure surfaces after you have spent the money and the weekend.

UC2 is worth building. It is not worth building until the provenance system in
gap 2 exists to hold its output at arm's length, and until UC1 has proven the
capture pipeline on numbers that reality has already checked.

### 4.4 If the decision lives in the chat, the capture has already failed

The manifesto says brainstorming happens, then "final decision is being made and
put into work." That sentence contains the whole risk. The moment of highest
knowledge density in the entire process is the moment a design decision is made
and alternatives are rejected -- and it is described here as a conversation.

Your existing protocol already fixed this for implementation work:
`docs/protocol/README.md` says "make every durable handoff a file, never a
conversation." The gap is that it fixed it for *implementation* and not for
*deliberation*. See gap 4.

The specific thing that must be captured is the **rejected alternatives and
why**. "We used a 70mm plate" is a fact recoverable from the model. "We
considered 60mm and rejected it because the FC stack fouled the strap slots" is
knowledge, it is unrecoverable from the model, and it is what stops you
re-evaluating 60mm next year.

### 4.5 Renaming the repo to FusionControlCenter conflates the instance with the system

`drone-wood-frame` is one build. FCC is the system that makes builds easier.
Renaming this repo to FCC means the platform's history, issues, and structure are
permanently entangled with one wooden quadcopter, and the second project either
inherits drone-specific baggage or forks.

My recommendation is in section 6. It is a real decision and I would like your
answer rather than my assumption -- it is question Q6.

### 4.6 "Fusion also does electrical circuits" is doing a lot of quiet work

Fusion's Electronics workspace (the former Eagle) is genuinely powerful, and
your MCP server already exposes an electronics surface -- there is a
`fusion_mcp_electronics_read` tool available in this session, so the capability
is real and reachable today.

But schematic capture, netlists, PCB layout, DRC, and manufacturing output are a
separate discipline with separate file types, separate validation, and separate
failure modes from mechanical CAD. The manifesto mentions it in a subordinate
clause. If electronics is in scope for FCC, it is a second pillar of comparable
size to the mechanical one, and it needs its own answer to "what is the unit of
captured knowledge" -- a verified footprint and a verified pinout are not the
same kind of object as a verified bracket.

Worth deciding explicitly rather than absorbing by implication.

---

## 5. Gaps -- decisions the manifesto does not make

These are the questions I would have to answer myself to write a plan, which
means they are the questions worth you answering first.

### Gap 1: What, precisely, is the unit of reusable knowledge?

The manifesto says "save some data" and gives one example (a motor: 3D model
plus 2D planning). It never defines what a saved thing *is*. This is the central
design question of the entire system -- everything else is plumbing around it.

**My proposal: the Component Card.** A directory, versioned, with a fixed shape:

```
components/library/motor-1103-18x18/
  component.yaml      typed dimensions, each with source + confidence
  profile.dxf         2D footprint for cutting
  model.f3d           3D model (binary, milestone commits only)
  model.step          neutral-format export
  photos/             the ruler-in-frame evidence
  provenance.md       where every number came from, and what confirmed it
  used-in.md          which builds consumed this, and how it went
```

The rule that makes it valuable rather than decorative: **every dimension
carries its source.** Not just `bolt_circle_mm: 9.0`, but:

```yaml
bolt_circle_mm:
  value: 9.0
  source: caliper          # caliper | datasheet | vendor-claim | estimated | ai-derived
  confidence: high
  verified_by: build-001   # the build that physically confirmed it, or null
  measured: 2026-08-27
```

This is the single most important schema decision in FCC, because it is what
keeps UC2's output from silently poisoning UC1's ground truth. A number scraped
from a product listing and a number read off calipers must never be
indistinguishable once they are both sitting in a YAML file.

Note that this is a strict superset of the existing `params.yaml` structure, so
it is reachable from where you are rather than a rewrite.

### Gap 2: `verified` must be a first-class state, with an explicit transition

Following from gap 1: a component is `unverified` until a physical build
confirms it, and something must perform that transition. The transition is the
most valuable event in the system and the manifesto does not mention it.

Concretely: when the frame is cut and the motor actually bolts on, *something*
must go back and mark that bolt circle `verified_by: build-001`. If that step is
manual and undisciplined it will not happen, and within three projects the
library becomes a pile of numbers of unknown quality -- which is worse than no
library, because it invites trust it has not earned.

This is also the natural home for the mistake capture you want. A build that
*fails* is a transition too: `contradicted_by: build-002`, with a note.

### Gap 3: The minor-vs-major classifier needs something written to classify against

As stated, "is this a minor improvement or does it go against the core reason it
was built?" is a judgment call handed to an AI with no reference material. That
will produce confident, inconsistent answers -- the classifier will say "minor"
on Tuesday and "major" on Thursday for the same change, and you will stop
trusting it, which is worse than not having it.

**Make it a lookup instead of a judgment.** The project description document you
keep referring to should carry an explicit, structured section:

```markdown
## Invariants -- changing these invalidates the project
- Must fit a 250x250mm stock sheet          (why: the sheet is what I own)
- Must fly on the salvaged Temu motors      (why: this is a salvage project)
- Must be cuttable on a laser, single sheet (why: no CNC access)

## Free variables -- optimise these freely
- Arm width, taper profile, lightening holes
- Plate size, within the FC stack footprint
- Battery position along y
```

Then the classifier becomes nearly mechanical: **does the requested change touch
a declared invariant? Major -- escalate to brainstorming and a decision record.
Only free variables? Minor -- proceed.** An AI is reliable at that. It is not
reliable at inferring design intent from geometry.

This also gives you the escalation path the manifesto wants: major changes are
exactly the ones that must produce a written decision record, because they are
the ones where the *why* is about to change.

### Gap 4: The existing protocol handles implementation, not deliberation

`docs/protocol/` is, substantially, the METHOD.md you describe. Codex already
built it: roles, phase types, a hard gate, typed contracts, trust boundaries,
and a rule that the planner is not the implementer. Before writing a new
METHOD.md, read what is already there -- I suspect 70% of your intent is
implemented.

What is genuinely missing is the deliberation half. The current protocol
answers "how do two agents safely build a thing that was already decided." It
does not answer "how do two agents and a human decide what to build." That
needs:

- a **design brainstorming phase type** alongside `implement` / `gate` / `verify`
- a **decision record contract** -- the `decision-<slug>.md` pattern that
  `docs/brainstorming/README.md` already declares but nothing yet defines
- a rule that a rejected alternative is recorded **with its reason**, since the
  rejected option is the reusable part
- the invariant/free-variable classification from gap 3 as the escalation trigger

That is a well-scoped addition to an existing document, which is a much smaller
and safer job than authoring a method from scratch.

### Gap 5: The ICM paper is load-bearing and I have not read it

You describe ICM as the core of Omnissiah's work logic and the basis for FCC's
folder structure and AI communication method. I cannot design around a paper I
have not seen, and I am not going to guess at it from the acronym and risk
building on a misreading of the thing you consider foundational.

This is question Q1, and it blocks any METHOD.md work.

### Gap 6: The UI you describe is already planned, and the overlap should be reconciled

Your UI description here -- measurement entry, dummy component models, a tilt
animation showing what to measure, a page for brainstorming with the AIs --
matches `docs/codex/claudePlan-web-workstation-1.md` almost point for point. That
plan is written, scoped, and currently blocked on one environment issue.

Two notes. First, that plan deliberately scopes the 3D viewer to a *later* plan
and builds the data spine first, for reasons in
`idea-web-workstation.md` that I still stand behind. Second, it contains one
proposal worth restating here because it bears directly on FCC: **draw the dummy
models from the current parameter values rather than shipping static assets.**
Type a 9mm bolt circle on a 12mm base and the holes visibly hang off the edge.
The model stops being an illustration and becomes a second validator, catching
the class of error -- measuring the wrong dimension -- that no numeric check can.

That idea generalises to FCC directly: every component card renders itself from
its own numbers, so a bad number in the library is visible rather than latent.

### Gap 7: "Extend the MCP server" needs a boundary

`.mcp.json` points at `http://127.0.0.1:27182/mcp`, a third-party server you did
not write. Extending someone else's server means either forking it -- and owning
the merge burden forever -- or wrapping it.

`fusion_scripts/README.md` already draws the line you need, and I would keep it:
MCP is for *exploring*, scripts in the repo are for *repeatable proven steps*,
and the promotion from one to the other is a deliberate act. If a capability is
missing, the first question is whether it belongs in your `fusion_scripts/` --
which you own, which are in git, and which are already tested against a fake
`adsk` -- rather than in a server you would have to maintain a fork of.

Fork the server only for things scripts genuinely cannot do.

---

## 6. Proposed shape

Three layers, with a hard rule about when each one comes into existence.

```
  Layer 3   FCC platform            (a separate repo, later)
            component library, METHOD.md, decision records, techniques
                      ^
                      |  extracted, on the second real instance
                      |
  Layer 2   domain-blind tooling    (this repo, now)
            field spec, surgical writer, local server, capture formats
                      ^
                      |
  Layer 1   drone-wood-frame        (this repo, now -- finish it)
            params.yaml, geometry.py, validate.py, real measurements, real wood
```

**The extraction rule: build concretely, extract on the second instance.**

Not the first. One data point does not define an interface -- it produces an
abstraction shaped exactly like its single example, which is the most expensive
kind of wrong. When a second project needs the same motor, that is the moment
the shared component library stops being speculative and starts being a
refactor with two known callers. Refactoring with two real callers is easy.
Designing for imagined ones is not.

This also resolves the naming question in 4.5. `drone-wood-frame` stays the
instance and keeps its name. FCC is the name of the system that gets extracted
into its own repo when Layer 3 is real. In the meantime, Layer 2 code is written
*domain-blind from the start* -- the writer, the field spec, the server, and the
capture formats have no drone in them -- so extraction is a move, not a rewrite.

My recommendation is therefore: **do not rename this repo yet.** Write the
manifesto's ambition into a `MISSION.md` here, build Layer 2 domain-blind, and
let the name follow the extraction.

---

## 7. Sequencing

The dependency graph in section 4.2 is nearly linear, so this is close to
forced. Ordered by what unblocks what:

| # | Step | Why here | Rough size |
|---|---|---|---|
| 0 | Clear the `.pytest-run-tmp` blocker | No gate can pass until it is cleared | minutes |
| 1 | Write `MISSION.md` for the frame, with **invariants** and **free variables** | Gap 3 needs it; it is also the manifesto refined into a checkable form | an hour |
| 2 | Measure the real parts. Drive 19 `TODO`s to zero | Every number is currently a guess | a session with calipers |
| 3 | Extend `docs/protocol/` with the deliberation half (gap 4) | Small, additive, unblocks all AI-collaboration work | one plan |
| 4 | Build `claudePlan-web-workstation-1` | Makes step 2 repeatable, and is Layer 2's spine | already planned |
| 5 | **Cut the frame. Build it. Fly it. Log everything** | The only real source of captured knowledge | the actual project |
| 6 | Write the Component Card format (gaps 1-2) from what step 5 taught | Now grounded in one verified component | one plan |
| 7 | Photo ingest, 3D viewer, decision records | Consumers of the spine | plans 2-4 |
| 8 | Extract FCC on the **second** project | Two callers define the interface | later |
| 9 | UC2 sourcing, on top of provenance | Needs somewhere trustworthy to put untrusted data | much later |

Step 5 is the one that will feel like a detour from building FCC. It is not.
It is the only step that produces the raw material FCC exists to refine, and
every step after it is guesswork without it.

---

## 8. Questions for you

You invited these. Q1 and Q2 block real work; the rest change design decisions.

**Q1 (blocking).** What is the ICM paper? A link, a PDF in the repo, or a
paragraph summary is enough. It is load-bearing for METHOD.md and for the folder
structure, and I will not guess at it.

**Q2 (blocking).** Is `drone-wood-frame` going to be finished as a physical
object -- cut, built, flown -- or has it become the demo case for FCC? My strong
recommendation is section 4.1. But it is your call, and every recommendation in
section 7 changes if the answer is "the frame was always just an example."

**Q3.** Does Omnissiah already define a knowledge-record schema, a provenance
model, or a decision-record format? If it does, FCC should mirror its shape even
where the content differs -- two systems with the same skeleton are far easier
to work in than two systems with different ones. If it does not, FCC can define
one and Omnissiah can adopt it.

**Q4.** Is Fusion Electronics in scope for FCC, or is FCC mechanical-only for
now? Section 4.6. This changes the size of the project substantially, and I
would rather have it decided than assumed.

**Q5.** For UC2 sourcing -- are you willing to accept a rule that says *no
number enters the library without a linkable source or a physical measurement*,
with AI-estimated values permitted only when explicitly flagged and never
promoted to `verified`? I think this rule is what makes UC2 safe. It also makes
UC2 slower and more annoying, which is why it needs your agreement rather than
my assumption.

**Q6.** One repo or two? My recommendation is section 6: keep this repo as the
instance, write Layer 2 domain-blind inside it, extract FCC on the second
project. Confirm or overrule.

**Q7.** When something in Fusion turns out to be a discovered technique rather
than a component -- the hidden mechanics you expect to find -- what should the
captured artifact be? A `fusion_scripts/` script, a note in a techniques file, or
both with a promotion rule between them? I have a preference (both, with
`fusion_scripts/README.md`'s existing explore-then-lock-in rule as the promotion
trigger), but this is your workflow and you will know what you would actually go
looking for later.

---

## 9. My view, in one paragraph

The thesis is right and worth years of work: hardware development has no package
manager, reuse is nearly zero, and a system that captures verified components,
proven techniques, and the reasons behind rejected alternatives would compound
in value in a way that very little else in a workshop does. The manifesto's
weakness is not ambition but order. It proposes to build the refinery before the
first barrel of crude exists -- and the schema for captured knowledge is
precisely the thing you cannot design correctly until a real build has surprised
you a few times. So: write the mission down with explicit invariants, measure
the parts, build the spine, and then **cut the wood and fly the thing**. The
frame is not a distraction from FCC. It is FCC's first and only dataset, and
every design decision the platform needs is downstream of what that build
teaches you.

---

## 10. Next routing step

Nothing routes to `docs/codex/` from this document yet. Per
`docs/claude/behaviour.md` a plan needs settled scope, and Q1 and Q2 are
unsettled.

Once you answer them, the first two candidates are both small, both additive,
and both unblock everything after them:

1. `claudePlan-mission-invariants-1.md` -- the `MISSION.md` format with
   invariants and free variables (gap 3), applied to the frame.
2. `claudePlan-protocol-deliberation-1.md` -- the deliberation half of
   `docs/protocol/` and the decision-record contract (gap 4).

`claudePlan-web-workstation-1.md` remains written and blocked on P0, and is
unaffected by anything in this review.
