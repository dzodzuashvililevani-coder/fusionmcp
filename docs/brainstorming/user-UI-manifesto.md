# User UI manifesto

**Status:** raw user brief for review and brainstorming.
**Purpose:** Explain how the future UI should work from the user's experience:
what should be displayed, when it should be displayed, what functions the
workspace should have, and what the system should feel like while a project is
being created.

This is not an implementation plan. It is source material for Claude and Codex
to review before turning the UI direction into scoped plans.

---

## 1. Why this project exists

Before describing screens and tools, I want the project philosophy to be clear.

I am building a large development system that does things similar to what AI
coding agents do, but across many branches of creation. Creating something can
include software, hardware, mechanics, electronics, 3D modeling, blueprint
creation, documentation, decision making, and knowledge capture.

Because creation covers many different branches, I want to delegate each branch
to its own sub-system. Each sub-system can use AI and its own knowledge-capture
sub-project to create, accumulate data, store what was learned, and improve over
time. After every sub-system's creation cycle is done, I want to merge them into
one creation system that has everything needed to build serious, possibly
company-level projects and ideas.

This project is one of those sub-systems. It exists to help me visualize what I
want and make it reality-proof.

For every idea, there eventually has to be a physical representation. I have an
idea, and if that idea needs to live in the real world, I need to create the
physical skeleton of the project: a structure that looks how I want, is sturdy
and reliable, perfectly fits its mission, and supports the project's
requirements.

Developing that physical skeleton is hard. It takes many attempts to arrive at
the right form. But that process is also perfect data accumulation for AI: every
attempt, mistake, measurement, design decision, material choice, and result can
teach the system how to become better at creating physical representations over
time.

The final variant of this project should work together with the knowledge
capture system. This project creates the physical design and the evidence behind
it; the knowledge system stores and organizes what was learned.

---

## 2. Example user journey

The user has an idea.

In this example, the user has three big motors, a flight controller, and ESCs
for each motor. The user writes a document explaining:

- what the project is;
- why it is being made;
- what the final point of the project is;
- how the finished version should look;
- what the finished version should do;
- what the idea behind the project is;
- any hardware already available;
- any materials already available;
- any constraints, requirements, or preferences.

At this point, the user has two things:

- part of the hardware needed for the project;
- a well-written project document.

The user does not yet know exactly how the physical design should look. They do
not know which frame variant to choose, how to distribute hardware across the
frame, what materials are best, or what layout will satisfy the mission.

This is where the user decides to use this project.

For this example, assume the software side is handled by another project named
Omnissiah. This project focuses on the physical skeleton.

The user opens the app. The welcome page briefly explains what the project does.
The user taps **Create project**.

The app sends the user to a new page where they can:

- enter the project name;
- provide the project documentation;
- optionally list hardware or materials they already have;
- start the first analysis.

The AI analyzes the document and looks for important details, including:

- what the user is building;
- what mission or purpose the physical object must serve;
- what hardware the user already has;
- what hardware is missing;
- what materials the user has mentioned;
- what constraints affect the physical design;
- what decisions need to be made next.

In the example, the user only has the flight controller, motors, and ESCs. The
system should identify what hardware is missing and explain why it is needed.

Later, we can brainstorm the project-document format itself: what it should
mention, what sections it should have, what details the AI should extract, and
what is required before physical design can begin.

---

## 3. Workspace idea: conditional output

The main workspace should be flexible. It should not be a fixed page where
everything is visible all the time. It should be a workspace made from tools.

Some tools will be used constantly. Examples:

- AI chat;
- components list;
- project document viewer;
- measurement panel;
- report panel;
- design-decision log.

Some tools will be used only sometimes. Examples:

- material comparison;
- missing-parts analysis;
- weight distribution;
- blueprint viewer;
- 2D layout viewer;
- 3D model viewer;
- hardware compatibility checks;
- electronics layout;
- mechanical stress notes;
- manufacturing constraints;
- export tools.

The workspace should show tools conditionally, depending on what the user is
doing and what the system knows. If a tool is needed, it should be easy to open.
If it is not needed right now, it should not clutter the workspace.

The main goal is a flexible, easy-to-maneuver workspace that contains all the
tools needed to create the skeleton of a project.

I like the idea of conditional output: the system shows the right thing at the
right time. I also like reusable-component best practices in React, because the
same UI tools should be reused across different project types instead of rebuilt
each time.

---

## 4. Core tools the workspace may need

This is an initial list for brainstorming. The final list should be reviewed and
improved.

### AI chat

The AI chat should be one of the main tools. It should help the user reason
about the design, ask for missing details, suggest next steps, and explain why
something matters.

It should be able to reference the project document, component data, current
measurements, design decisions, reports, and generated models.

### Components list

The components list should show every component known to the project. It should
hold data about each component, such as:

- name;
- category;
- dimensions;
- weight;
- material;
- position in the design;
- source;
- measured or estimated status;
- notes.

Clicking a component should open the document or data record that holds its
details.

### Project document viewer

The user should be able to see the original project document and any extracted
requirements. The system should show which parts of the design came from which
part of the document.

### Requirements and missing-parts tool

After reading the user's project document, the system should list:

- known requirements;
- assumptions;
- missing hardware;
- missing measurements;
- unresolved questions;
- decisions the user must make.

### Measurement tools

The workspace should accept many types of real-world data. I plan to add
digital measuring tools later, possibly using ESP32 or another board, to provide
measurements directly to the system.

Examples:

- weight;
- length;
- width;
- height;
- thickness;
- hole spacing;
- material density;
- voltage/current data;
- other physical measurements.

This should come after the current project is finished developing, and it will
be one of the first features I want to add.

### 2D and 3D design viewers

The user should be able to inspect the physical skeleton visually. The system
should support blueprints, 2D layouts, and 3D models. These views should connect
back to components, measurements, and decisions.

### Decision log

The project should record why choices were made:

- material choice;
- design shape;
- component placement;
- frame variant;
- manufacturing method;
- safety margin;
- tradeoffs rejected.

The final report should not only say what was built. It should explain why it
was built that way.

---

## 5. Data the workspace should handle

The workspace should be able to receive and organize many kinds of data:

- user-written project documents;
- component data;
- real measurements;
- AI analysis;
- generated blueprints;
- 2D models;
- 3D models;
- material notes;
- hardware requirements;
- electronics layout information;
- mechanical constraints;
- validation reports;
- decision records;
- final build documentation.

The system should distinguish between guessed, AI-inferred, user-provided,
measured, and verified data.

---

## 6. Final output

When the project is ready, I want a large final report document.

That report should contain:

- the project goal;
- the original idea;
- requirements;
- all components;
- all measurements;
- 2D blueprints;
- 3D models or links to model files;
- material choices;
- design choices;
- hardware-placement decisions;
- validation results;
- manufacturing notes;
- why each major decision was made;
- what alternatives were considered;
- what facts or measurements backed the decisions;
- what still needs improvement.

The report should be complete enough that someone can understand the whole
physical design: what it is, how it was made, why it is shaped the way it is,
and how to recreate or improve it later.

---

## 7. Brainstorming questions

These are the questions Claude and Codex should help explore next:

- What should the ideal project-document format look like?
- What information must the user provide before the system can design a
  physical skeleton?
- What tools should always be visible in the workspace?
- What tools should appear only conditionally?
- What data model should components use?
- How should the system mark guessed, measured, verified, and AI-inferred data?
- How should the UI connect a visual model to measurements and decisions?
- What should be in the final report template?
- Which parts belong in this project, and which parts belong in the separate
  knowledge-capture system?
