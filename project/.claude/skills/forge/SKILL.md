---
name: forge
description: >-
  Structure a project's notes/ design nucleus (brainstorm, research, roadmap)
  into docs/ (architecture, ADRs, a slim roadmap) and GitHub Project items
  (milestones, epics, slices, ideas). Use after scaffolding to do the initial
  structuring, and again later in the project's life to slice the next
  milestones into detail. Runs as a source-informed interactive dialogue, not
  a one-shot generator.
---

# /forge

Turn raw `notes/` into structure: `docs/` for the durable narrative, GitHub
Project items for the actionable state. As each section is structured, the
matching `notes/` content is pruned, the goal is that `notes/` shrinks toward
nothing while `docs/` and the board grow.

## Philosophy: decide together, incrementally

**This skill is a conversation, not a batch job.** Do NOT read the notes and
emit one giant plan for approval, then apply it in a single sweep. Instead, at
every decision point:

1. Ground the question in the **actual notes** (quote the stage, the slice, the
   decision you're asking about).
2. Use the **AskUserQuestion tool** to offer concrete options, with your
   recommendation first and the reasoning stated.
3. **Debate** if the user pushes back. Their answer can change your read of the
   source. Don't defend a proposal past its usefulness.
4. **Lock it in, then act on that piece immediately** (write the ADR, create the
   milestone, open the issues, prune the migrated notes). Keep `docs/`, the
   board, and `notes/` consistent as you go.
5. Move to the next decision.

The user wants to shape the structure with you, one source-informed question at
a time, and watch it take shape as you agree, not review a finished document.

Bias toward **few, high-signal questions**. Batch trivially-related choices into
one question with several options rather than interrogating line by line. When
something is obvious from the notes, state it and move on, don't ask.

## A recurring tool, not a one-time bootstrap

`/forge` runs many times across a project's life:

- **Initial structuring**: a fresh `notes/` nucleus becomes `docs/` + a board
  where the near-term work is detailed and the later work is coarse.
- **Deepen** (the common repeat): you've shipped the early milestones; now slice
  the next milestone (which was left at milestone/epic granularity) into real
  user stories and tasks. See [Deepening later milestones](#deepening-later-milestones).
- **Prune**: migrate whatever's left in `notes/` into `docs/` or issues and trim
  the source.

Always start by reading the current state (existing milestones, issues, ADRs,
and what remains in `notes/`) and propose which of these the run is about.

## The model

These four levels (defined in `docs/project-management.md`) are what `/forge`
produces. Mind the deliberate looseness:

- **Stage** — a Kniberg / Earliest-Testable-Usable-Lovable framing bucket (Bus
  Ticket, Skateboard, Scooter, Bicycle, Car). It's a **thinking tool for
  sequencing**, and it lives as a section in `docs/roadmap.md`. A stage is **not**
  automatically a milestone, and milestones are **not** named after it.
- **Milestone** — a **product-focused outcome**, named for what the product can
  do ("Accounts and login", "First end-to-end run"), never "Skateboard". One
  stage may be a single small milestone, or a big stage may be worth several
  milestones. Decide the cardinality with the user.
- **Epic** — a release cluster: slices that ship together for one coherent
  outcome, scoped inside a single milestone.
- **Slice** — a vertical slice / user story / task: one PR's worth of work that
  cuts through the layers. Its user-centric "why" is inherited from its epic;
  don't force "As a user…" onto plumbing slices.

## Prerequisites

- A `notes/` folder with the design nucleus. The conventional shape is
  `brainstorm.md` (vision, decisions, feature ideas), `research.md` or
  `research/` (technical deep dives, open questions), and `roadmap.md` (stages
  with slices). Adapt if the project organizes notes differently.
- The PM board bootstrapped: `./scripts/bootstrap-pm.sh` has run (labels,
  project, date fields exist). If not, run it first.
- `gh` authenticated with the `project` scope (`gh auth refresh -s project`).
- Read `docs/project-management.md` for this project's issue types, label
  system, and the stage→milestone mapping. `/forge` automates that mapping.

## Step 0 — Orient

Read the whole `notes/` folder before asking anything. Then reflect the shape
back in **2-4 sentences** (not a document): how many stages, roughly how much
work, where the locked decisions live, where the open questions live. Confirm
you understood the project before structuring it. If the notes don't fit the
conventional shape, say what you actually found and propose how to proceed.

Discover the context you'll need: owner/repo (`gh repo view --json owner,name`),
the project number (`gh project list --owner <owner>`), and existing
milestones/issues/ADRs (so you never duplicate, see [Idempotency](#idempotency)).

## Step 1 — docs/architecture.md

The "what is this system" narrative, sourced from the vision and the
architecture-bearing research files. Ask a source-informed question about scope
and shape before writing ("Should architecture.md lead with the runtime data
flow, or with the component map?"), draft it, confirm, then **prune the migrated
material from `notes/`** (the vision/architecture prose now lives in docs/). Keep
it a living overview, not an exhaustive spec.

## Step 2 — ADRs (docs/decisions/)

Locked-in technical decisions become ADRs using `docs/decisions/0000-template.md`.
A decision log in the notes (a "decisions" section in research, or a "Core
Decisions" block in `brainstorm.md`) is the prime source. For each decision:

- Quote it, and ask via AskUserQuestion how to record it: status (Accepted /
  Proposed / Accepted-but-tentative), and whether any "switch when…" triggers in
  the notes become the ADR's Consequences.
- Number ADRs sequentially (`0001-…`, `0002-…`). One decision per ADR.
- Don't invent decisions. If something reads as an open question, it's a Step 6
  idea, not an ADR.
- Once written, **prune the decision from `notes/`** (it's now an ADR).

## Step 3 — Milestones (product-focused)

Walk the roadmap stage by stage. For each stage, the Kniberg name is just framing;
the question is **what product outcome(s) does this stage deliver, and is it one
milestone or several?** Ask it that way:

> "The 'Skateboard' stage covers <the core loop the notes describe>. That reads
> like one milestone to me, named **<product outcome>**. Agree, or split it (e.g.
> a data-layer milestone and a first-user-flow milestone)?"

Offer product-focused names, never the Kniberg codename, as the milestone title.
For each confirmed milestone:

- `gh api repos/{owner}/{repo}/milestones -X POST -f title="<product outcome>"
  -f description="See docs/roadmap.md#<anchor> for the stage definition."`
- Optionally create one `kind:stage` issue per stage as a dated narrative tracker
  (bare milestones don't render on the Roadmap view; a dated issue does). Offer
  it; it's worth it when a stage spans several milestones and you want one Gantt
  bar for the whole stage.

## Step 4 — Epics (cluster larger milestones)

A `kind:epic` groups slices that ship together. **Only introduce epics when a
milestone has enough slices to warrant grouping** (roughly 4+). Propose a
clustering drawn from the slices' own structure and ask:

> "This milestone has 7 slices. I'd split them into two epics, **<outcome A>**
> and **<outcome B>**. Agree, or cluster differently?"

Offer the recommended split, an alternative granularity, and "keep this milestone
flat (no epics)". For small milestones, skip epics, slices hang directly off the
milestone. Create confirmed epics as `kind:epic` issues, milestone-assigned, and
link slices to them as sub-issues.

## Step 5 — Slices (match depth to horizon)

Don't slice the whole roadmap into issues on day one. Match issue depth to how
near the work is, and confirm the boundary with the user:

- **Near milestones** (the current + next one or two): create every slice as a
  `kind:slice` issue, a sub-issue of its epic (or milestone, if it stayed flat),
  milestone-assigned, added to the board.
- **Later milestones**: create the milestone (+ epics if the shape is already
  clear) only. Leave their slices as checklist bullets in `docs/roadmap.md`;
  they'll churn before they're worked, and `/forge` will slice them later (see
  [Deepening](#deepening-later-milestones)).
- Confirm slice lists in one batched question per epic, not one question per
  slice.

## Step 6 — Ideas (open questions + far horizon)

Open questions and far-future material (the roadmap's "Beyond", late feature
ideas) become `kind:idea` issues with a `horizon:*` label. Per cluster, ask
whether each is an idea (`horizon:now/next/later`), a `kind:spike` (a real
question worth a time-boxed investigation), or out of scope. Don't import every
musing, ask which are worth tracking, then prune them from `notes/`.

## Step 7 — Wire roadmap ↔ board

Once items exist, close the loop both ways (see project-management.md → "Wiring
vision to GitHub PM"):

- Write/refresh the slim `docs/roadmap.md` (~30-50 lines): the stage glossary
  (the Kniberg framing stays here, as the sequencing story), and under each stage
  a line naming its milestone(s) and listing the open epics, e.g.
  `> Milestone [Accounts and login](../../milestones/2); epics: #14, #15.`
- Make each milestone's description point back at `docs/roadmap.md#<stage>`.

The narrative (why, what each stage looks like done) lives in `docs/`; the state
(what's open/in-progress/done) lives in GitHub. The links keep both navigable.

## Deepening later milestones

The common repeat run. A later milestone that was left coarse (milestone, maybe
epics) is now the near work. Re-run `/forge` to:

1. Read the milestone's epics and whatever roadmap/notes material describes it.
2. Interactively confirm or refine the epic clustering (Step 4).
3. Slice each epic into `kind:slice` user stories/tasks (Step 5), as sub-issues.
4. Move the corresponding checklist bullets out of `docs/roadmap.md` (they're
   issues now) and prune any remaining `notes/` detail you consumed.

This is how a coarse plan becomes actionable, milestone by milestone, instead of
all at once up front.

## Pruning notes/

`notes/` is a staging area, not a permanent home. After each section is
structured, remove or trim the source with the user's confirmation:

- Vision / architecture / system explanations → `docs/architecture.md` (or its
  own `docs/` page for a big subsystem). **Technical detail that explains how the
  system works belongs in `docs/`, not in issues.**
- Locked decisions → ADRs.
- Planned work → issues. Far-future / open questions → `kind:idea` issues.

The end-state is that `notes/` empties out entirely: current understanding lives
in `docs/`, future work lives on the board. Pruning is destructive, always
confirm before deleting, and never prune material you haven't actually migrated.

## Idempotency

`/forge` is re-runnable. Before creating anything, list what exists (milestones,
issues by `kind:*` label, ADR files) and skip or update rather than duplicate.
Reuse an existing milestone; when deepening, only add the missing slices.

## When you're done

Summarize what changed: ADRs written, milestones/epics/slices created (with
counts and the near/later boundary), ideas filed, the docs↔milestone wiring, and
what was pruned from `notes/`. Point the user at the board URL and
`docs/roadmap.md`.

## References

- Henrik Kniberg, [Making sense of MVP](https://blog.crisp.se/2016/01/25/henrikkniberg/making-sense-of-mvp)
  — the Earliest Testable/Usable/Lovable framing and the skateboard→car metaphor.
- Michael Nygard, [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions),
  and [adr.github.io](https://adr.github.io/) — the ADR practice.
- This project's `docs/project-management.md` — the issue types, label system,
  and stage/milestone mapping `/forge` operates on.
