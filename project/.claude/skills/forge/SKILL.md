---
name: forge
description: >-
  Structure a project's notes/ design nucleus (brainstorm, research, roadmap)
  into docs/ (architecture, ADRs, a slim roadmap) and GitHub Project items
  (milestones, epics, slices, ideas), and leave the project navigable by a cold
  coding agent. Use after scaffolding for the initial structuring, and again
  later to slice the next milestones into detail. Runs as a source-informed
  interactive dialogue, not a one-shot generator.
---

# /forge

Turn raw `notes/` into structure: `docs/` for the durable narrative, GitHub
Project items for the actionable state, and an entry path a cold agent can
follow. As each section is structured, the matching `notes/` content is pruned,
the goal is that `notes/` shrinks toward nothing while `docs/` and the board grow.

## Philosophy: decide together, incrementally

**This skill is a conversation, not a batch job.** Do NOT read the notes and
emit one giant plan for approval, then apply it in a single sweep. At every
decision point:

1. Ground the question in the **actual notes** (quote the stage, slice, or
   decision you're asking about).
2. Use the **AskUserQuestion tool** to offer concrete options, with your
   recommendation first and the reasoning stated.
3. **Debate.** The user's answer can change your read of the source, don't
   defend a proposal past its usefulness.
4. **Lock it in, then act on that piece immediately** (write the ADR, create the
   milestone, open the issues, prune the migrated notes). Keep `docs/`, the
   board, and `notes/` consistent as you go.
5. Move to the next decision.

Bias toward **few, high-signal questions**. Batch related choices into one
question. When something is obvious from the notes, state it and move on.

**Challenge the notes; don't transcribe them.** This is the highest-value thing
`/forge` does. Roadmap notes routinely over-scope the early stages ("the core
loop, done well") when the Earliest-Testable milestone should be a **tracer
bullet**: the thinnest end-to-end thread that proves the idea. And **reality-check
the notes' assumptions** against what actually exists, the notes may assume infra,
services, or accounts (an observability backend, a hosted model, a vault) that
aren't stood up yet. Surface those and defer or adjust.

## A recurring tool, not a one-time bootstrap

`/forge` runs many times across a project's life:

- **Initial structuring**: a fresh `notes/` nucleus becomes `docs/` + a board
  where near-term work is detailed and later work is coarse.
- **Deepen** (the common repeat): you've shipped the early milestones; slice the
  next one (left coarse) into real user stories. See [Deepening](#deepening-later-milestones).
- **Prune**: migrate whatever's left in `notes/` into `docs/` or issues and trim
  the source.

Start each run by reading current state (existing milestones, issues, ADRs, and
what remains in `notes/`) and proposing which of these the run is about.

## The model

Defined in `docs/project-management.md`. Mind the deliberate looseness:

- **Stage** — a Kniberg / ET-EU-EL framing bucket (Bus Ticket, Skateboard, Car).
  A **thinking tool for sequencing** that lives in `docs/roadmap.md`. Not a
  GitHub object, and milestones are not named after it.
- **Milestone** — a **product-focused outcome** ("Generate an episode from a
  vault"), never "Skateboard". One stage may be one small milestone or several.
- **Epic** — an optional grouping: a release cluster of slices, only when a
  milestone has enough slices (~4+) to warrant it.
- **Slice** — a **small, reviewable PR's worth** of work. There is no separate
  "task" issue type; a slice's concrete tasks live as a **checklist inside it**.

## Prerequisites

- A `notes/` folder with the design nucleus (`brainstorm.md`, `research.md` or
  `research/`, `roadmap.md`). Adapt if organized differently.
- The PM board bootstrapped (`./scripts/bootstrap-pm.sh` has run). If not, run it.
- `gh` authenticated with the `project` scope (`gh auth refresh -s project`).
- Read `docs/project-management.md` for the issue types, labels, and mapping.

## Step 0 — Orient

Read the whole `notes/` folder before asking anything. Reflect the shape back in
**2-4 sentences** (not a document): how many stages, roughly how much work, where
the locked decisions live, where the open questions live. **Reality-check the
notes' assumptions** here and flag any that don't hold. Confirm you understood the
project before structuring it.

Discover context: owner/repo (`gh repo view --json owner,name`), project number
(`gh project list --owner <owner>`), and existing milestones/issues/ADRs (so you
never duplicate, see [Idempotency](#idempotency)).

## Step 1 — docs/architecture.md

The "what is this system" narrative, sourced from the vision + architecture-bearing
research. Ask about scope/shape, draft, confirm, then **prune the migrated prose
from `notes/`**. Keep it a living overview, not an exhaustive spec.

## Step 2 — ADRs (docs/decisions/)

Locked-in technical decisions become ADRs using `docs/decisions/0000-template.md`.
A decision log in the notes is the prime source. For each decision: quote it, ask
how to record it (status: Accepted / Proposed / Accepted-but-tentative, and
whether "switch when…" triggers become Consequences), write it (`0001-…`, one
decision per ADR), and **prune it from `notes/`**. Don't invent decisions, an open
question is a Step 6 idea, not an ADR.

## Step 3 — Milestones (product-focused, tracer-bullet first)

Walk the roadmap stage by stage. The Kniberg name is framing; ask **what product
outcome(s) the stage delivers, and whether it's one milestone or several**. Name
milestones for the product, never the codename.

**Right-size the earliest milestone to a tracer bullet.** If the notes' first
stage reads as "the core loop done well," that's too big, the Earliest-Testable
milestone is the thinnest end-to-end thread that proves the idea works. Split off
the depth (quality, persistence, robustness, scale) into a *later* milestone, and
record that deferred scope in `docs/roadmap.md`, never in an issue body.

For each confirmed milestone:
- `gh api repos/{owner}/{repo}/milestones -X POST -f title="<product outcome>" -f description="See docs/roadmap.md#<anchor>."`
- Optionally one `kind:stage` issue per stage as a dated narrative tracker (bare
  milestones don't render on the Roadmap view; a dated issue does).

## Step 4 — Epics (only when a milestone is big)

Introduce a `kind:epic` only when a milestone has ~4+ slices worth grouping.
Propose a clustering drawn from the slices' structure and ask. For small
milestones, skip epics, slices hang directly off the milestone.

## Step 5 — Slices (small PRs, detailed, wired)

Match depth to horizon: detail the **near** milestone(s) into slices now; leave
later milestones as coarse `docs/roadmap.md` bullets (they'll churn; `/forge` will
slice them later when they're near).

Each slice must be:
- **Small.** One reviewable PR. Don't inflate a slice to keep the count down, if
  it would be a big PR, split it. Confirm the granularity with the user.
- **Readably titled.** Outcome-oriented ("Read a Grimoire vault into typed notes"),
  not a terse label ("Vault", "API").
- **Self-contained.** Body = Description, Acceptance criteria, an **Implementation
  checklist** (the tasks), and a **Context** line breadcrumbing to `docs/`
  (`architecture.md`, ADRs) and the relevant `notes/research/` sections until those
  are migrated. **No "Deferred" section**, deferred work lives in `docs/roadmap.md`.

  ```markdown
  ## Description
  <what + why, 1-2 sentences>

  ## Acceptance criteria
  - [ ] ...

  ## Implementation
  - [ ] <task>

  _Context: docs/architecture.md; research/<file> §N._
  ```

- **Wired with dependencies.** Encode slice ordering as **native GitHub issue
  dependencies** so a coding agent can pick unblocked work:
  ```
  gh api repos/{owner}/{repo}/issues/{blocked}/dependencies/blocked_by -F issue_id=<blocker_id>
  ```
  (the blocker's numeric `id`, from `gh api repos/{o}/{r}/issues/{n} --jq .id`).

Create slices with the `kind:slice` label, assigned to the milestone, added to the
board (`gh project item-add <n> --owner <o> --url <issue-url>`), and sub-issues of
their epic when there is one. A slice's user-centric "why" is inherited from its
milestone/epic, don't force "As a user…" onto plumbing.

## Step 6 — Ideas (selective)

Open questions and far-future material become `kind:idea` (with `horizon:*`) or
`kind:spike` issues, **but be selective**. Don't import every musing: far-future
*vision* stays coarse in `docs/roadmap.md`; only file ideas/spikes that warrant
active triage now. Tuning details that belong to a future milestone's slices stay
in the notes until that milestone is worked. Prune what you do file.

## Step 7 — Wire roadmap ↔ board, and the agent's entry path

Two-way wiring (see project-management.md → "Wiring vision to GitHub PM"):
- Write/refresh slim `docs/roadmap.md` (~30-50 lines): the stage glossary, and
  under each stage a line naming its milestone(s) and listing the open epics.
- Make each milestone's description point back at `docs/roadmap.md#<stage>`.

**Then close the agent context chain.** A cold agent must be able to find work
without tribal knowledge. Ensure `CLAUDE.md` orients it, README → `docs/architecture.md`
→ `docs/roadmap.md` (naming the **active milestone**) → the board, and documents
**how to find the next issue**: list the active milestone's open issues, pick one
with **no open blockers** (`gh api repos/{o}/{r}/issues/{n}/dependencies/blocked_by`),
preferring slices that unblock the most downstream work. (Kindling's `CLAUDE.md`
ships this generically; top it up with the project's current focus.)

## Deepening later milestones

The common repeat run. A milestone left coarse is now the near work. Re-run to:
read its epics + roadmap/notes material; confirm/refine the epic clustering;
slice each epic into small `kind:slice` PRs with dependencies; move the
corresponding bullets out of `docs/roadmap.md`; and prune the consumed notes.

## Pruning notes/

`notes/` is a staging area, not a permanent home. After a section is structured,
trim the source with the user's confirmation. The key rule: **issues capture
*work*, not *knowledge*.** Prune a notes section only once its **knowledge** lives
in `docs/` (architecture, ADRs, system pages), not merely because you made issues
from it. Be **horizon-aware**: keep future-stage research depth until those stages
are worked. Pruning is destructive, always confirm, never prune unmigrated material.

## Idempotency

`/forge` is re-runnable. Before creating anything, list what exists (milestones,
issues by `kind:*` label, ADR files) and skip or update rather than duplicate.
When deepening, only add the missing slices.

## When you're done

Summarize: ADRs written, milestones/epics/slices created (with counts and the
near/later boundary and dependency wiring), ideas filed, the docs↔milestone
wiring, the agent entry path, and what was pruned. Point the user at the board URL
and `docs/roadmap.md`.

## References

- Henrik Kniberg, [Making sense of MVP](https://blog.crisp.se/2016/01/25/henrikkniberg/making-sense-of-mvp)
  — Earliest Testable/Usable/Lovable and the skateboard→car metaphor.
- Michael Nygard, [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
  and [adr.github.io](https://adr.github.io/).
- This project's `docs/project-management.md`.
