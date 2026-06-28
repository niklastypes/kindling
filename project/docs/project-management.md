# Project Management

This project uses GitHub Projects v2 for work tracking, with issue templates and a label system to keep things consistent.

---

## Initial setup after bootstrap

`./scripts/bootstrap-pm.sh` seeds the project, labels, and date fields automatically. The following steps live in the GitHub UI (the supported path for these operations — GitHub's Projects v2 API doesn't currently expose them cleanly):

1. **Add Status options `In Review` and `Blocked`.**
   Project menu (`⋯`) → Settings → **Custom fields** (left sidebar) → Status → Edit → add the two options. The workflow lifecycle below references both.
2. **Create your views, and save each one.** New views aren't persisted until you save them (`⋯` on the view tab → Save, or the "Save" prompt).
   - Rename the default view to **Table**.
   - Add a **Kanban** view (Board layout, grouped by Status).
   - Add a **Roadmap** view (Roadmap layout) for the timeline.

   Click `+` next to the view tabs → New view → pick a layout → Save.
3. **Enable built-in workflows.**
   Project Settings → Workflows. Turn on:
   - **Auto-add sub-issues to project** (usually on by default) — pulls sub-issues onto the board.
   - **Auto-add to project** — enable it and set the filter to `is:issue` so new issues land on the board automatically. **Enable this before creating issues:** it only catches issues opened *after* it's turned on, so any pre-existing issues have to be added by hand once.
   - **Item added to project** (usually on by default) — sets Status to `Todo` when an item is added.
   - **Pull request linked to issue** — set Status to `In Review`. (Linking happens automatically when a PR says `Fixes #N`.)
   - **Item closed** — set Status to `Done`.
4. **Roadmap and milestones.**
   - In the Roadmap view's settings, set `Start date` and `Target date` as the date sources.
   - Milestones don't render on the Roadmap. To *see* a milestone, add the built-in **Milestone** field as a column in a Table view (`+` in the field header → Milestone). For timeline bars, use `kind:stage` issues with dates (see [Stage](#stage-kindstage) below and the staged-roadmap mapping).

These steps are also printed in the script's summary output, so a re-run reminds you. The doc here is the durable record for anyone reading project-management.md without having just run the script.

---

## Issue Types

### Stage (`kind:stage`)

An optional narrative tracker for a roadmap stage (Henrik Kniberg's vehicle metaphor: Skateboard, Bicycle, Car, ...). The stage itself is a *thinking tool for sequencing*, not a GitHub object, it lives in `docs/roadmap.md`. A stage maps to **one or more** product-focused milestones (a small stage might be a single milestone; a big one several). This issue is the stage's *narrative* ("what does the product look like when this stage is done?"); the milestones are the shippable product outcomes underneath it.

**Example:** "🚲 Bicycle — the product is daily-usable: users can sign up, publish, and read a feed."

Stage issues carry `Start date` / `Target date` on the Project board so they render as bars on the Roadmap view (bare milestones don't render there; dated issues do). Skip this issue type entirely if your project doesn't use a staged roadmap. See [Mapping a staged roadmap to GitHub PM](#mapping-a-staged-roadmap-to-github-pm) for the full picture.

### Epic (`kind:epic`)

A release cluster that groups related slices. Use epics when a meaningful outcome requires multiple pieces of work.

**Example:** "User authentication" (requires login page, API auth middleware, password reset, session management).

Epics track progress through a checklist of linked slices. They're done when all slices are done.

### Slice (`kind:slice`)

An atomic vertical slice of work that delivers observable value. Slices cut through all layers (UI, logic, data) and should be small enough to complete in one PR.

**Example:** "Users can log in with email and password" (touches the login form, the auth API endpoint, and the session store).

This is the default work unit. When in doubt, create a slice.

**User-story framing lives at the epic, not the slice.** The slice description should answer "what changes when this lands?" and inherit the user-centric why from its parent epic. Forcing "As a [user], I want [outcome]" onto every slice produces theater on internal work (infrastructure, refactors, plumbing). Keep slices honest; the discipline is "this slice belongs to an epic with a user story," not "every slice is itself a user story."

### Spike (`kind:spike`)

A time-boxed research or prototyping task. Success is **knowledge gained**, not user value shipped. Use a spike when you don't know enough yet to design or estimate a real slice.

**Example:** "Investigate whether library X gives us streaming responses with backpressure (2-day budget, decide whether to commit to it or hedge)."

Spikes carry three mandatory fields in the template: a **question** to answer, a **time box** that triggers re-evaluation regardless of progress, and **decision criteria** that say what "done" looks like. The output is usually a closing comment with findings plus a link to wherever the lasting artifact lives (ADR, design doc, throwaway prototype). A spike often spawns a follow-up slice or epic; link the spawned issue from the closing comment.

Keeping spikes as a distinct kind keeps the slice definition sharp (slices deliver user value) and makes the time-box discipline visible in triage.

### Idea (`kind:idea`)

An uncommitted thought, not planned work. Ideas capture possibilities without committing to them.

**Example:** "What if we added a dark mode toggle?"

Ideas use horizon labels to indicate maturity (see Idea Capture below).

### Bug (`kind:bug`)

A defect. Something that worked before and doesn't now, or something that doesn't match its specification.

**Example:** "Login form shows 500 error when email contains a plus sign."

---

## Workflow Lifecycle

The full lifecycle when working an issue:

```
1. Pick issue #N from the board
2. Set Status -> In Progress
3. Create a feature branch (feat/, fix/, etc.)
4. Work in atomic conventional commits
5. Push and open a PR with "Fixes #N" in the description
6. GitHub auto-links the PR to #N
7. Project workflow sets Status -> In Review
8. Review, approve, merge
9. GitHub closes #N
10. Project workflow sets Status -> Done
```

The key is `Fixes #N` in the PR description. This triggers GitHub's automatic issue closing and the Project board's workflow automation.

---

## Issue dependencies

Slices within a milestone usually have an order, one builds on another. Encode that as **native GitHub issue dependencies** (the "Blocked by" relationship), not just a prose note, so a coding agent (or you) can pick work without guessing what's ready.

Set a dependency via the API:

```bash
# make <blocked> blocked by <blocker>
gh api repos/<owner>/<repo>/issues/<blocked>/dependencies/blocked_by \
  -F issue_id=$(gh api repos/<owner>/<repo>/issues/<blocker> --jq .id)
```

**Finding the next issue:** list the active milestone's open issues, then pick one with **no open blockers** (`gh api repos/<owner>/<repo>/issues/<N>/dependencies/blocked_by` returns `[]`). Prefer slices that unblock the most downstream work. The [`/forge`](../.claude/skills/forge/SKILL.md) skill wires these dependencies when it slices a milestone, and `CLAUDE.md` documents the picking rule for agents.

---

## Idea Capture

Not every thought is ready to become work. The idea capture flow lets you record possibilities and revisit them later.

### Horizons

Ideas are tagged with a horizon label indicating when they might become actionable:

| Horizon | Meaning | Action |
|---|---|---|
| `horizon:now` | Actively considering, likely becomes work soon | Review weekly, promote to slice/epic when ready |
| `horizon:next` | On deck, probably next phase | Review monthly |
| `horizon:later` | Visionary, no timeline | Review quarterly, archive if stale |

### Promoting an idea

When an idea is ready to become work:

1. Change the `kind:idea` label to `kind:slice`, `kind:epic`, or `kind:spike` (if the design space still has unknowns worth investigating first)
2. Remove the `horizon:*` label
3. Add acceptance criteria (or, for a spike, time box + decision criteria)
4. Link to a parent epic if applicable

---

## Growing Your PM Setup

The default setup covers the essentials. Here are patterns to add when your project needs them.

### Lane field

Add a custom single-select field called "Lane" to your Project for grouping work by area (e.g., "Frontend", "Backend", "Infrastructure"). Useful when multiple people work on different parts of the system.

Create it in Project Settings > Custom Fields > New Field > Single Select.

### Additional views

- **Backlog view**: Table filtered to Status = Todo, sorted by priority
- **Horizon view**: Table filtered to `kind:idea` label, grouped by horizon
- **By Lane view**: Board grouped by Lane field instead of Status

Create views in the Project UI: Views > New View.

### Mapping a staged roadmap to GitHub PM

For projects with a staged roadmap (Henrik Kniberg's Earliest Testable / Usable / Lovable model, the vehicle-metaphor stages, or any tier-and-stage structure), the mapping into GitHub PM is:

| Roadmap concept | GitHub PM concept | Granularity |
|---|---|---|
| **Tier** (ET / EU / EL) | (none — too coarse) | Multi-month grouping |
| **Stage** (Bus Ticket / Skateboard / Car / etc.) | *framing only* — a section in `docs/roadmap.md` | A sequencing bucket; maps to 1+ milestones |
| **Product outcome** within a stage | **Milestone** | A meaningful, shippable capability |
| **Release cluster** | **Epic** | A coherent outcome with a user story |
| **Vertical slice** | **Slice** | One PR's worth of work |

The stage names (Skateboard, Car) are a **thinking tool for sequencing**, not GitHub objects: they live in `docs/roadmap.md` and never become milestone titles. **Name milestones for the product** ("Accounts and login", "First end-to-end run"), not for the stage. A small stage may be a single milestone; a big stage may be worth several milestones plus their epics. Tiers (ET/EU/EL) are too coarse to track in GitHub at all, they're just the top-level grouping in the roadmap doc.

**Concrete example** (a hypothetical web app, the stage in `docs/roadmap.md` is "Bicycle: daily-usable", and it yields one product-focused milestone):

```
Milestone: "Accounts, posting, and a feed"   (the daily-usable stage)
├── Epic:  Users can sign up and log in
│   ├── Slice: Email + password registration endpoint
│   ├── Slice: Login form on the frontend
│   ├── Slice: Session storage with secure cookies
│   └── Slice: Database migration for the users table
├── Epic:  Users can publish a post
└── Epic:  Users can read a feed of recent posts
```

Note the last slice in the first epic ("Database migration for the users table") is internal plumbing — its user-centric why is anchored at the epic level ("users can sign up and log in"). The slice itself reads honestly as what changes, no "As a user, I want a database table..." theater required.

**Useful constraint:** an epic must fit inside a single milestone. The moment you try to assign an epic that spans two milestones, the mismatch surfaces and forces you to split it. Likewise a slice that doesn't fit in one PR probably wants to be its own epic with multiple slices. If a whole stage won't fit one shippable milestone, that's the signal to give it several.

The [`/forge`](../.claude/skills/forge/SKILL.md) skill automates this mapping as a source-informed interactive dialogue (and can be re-run later to slice the next milestones into detail).

**The `kind:stage` label and Stage template.** The bootstrap script seeds a `kind:stage` label and ships a [Stage issue template](#stage-kindstage), so a stage can be a tracked issue (for narrative purposes — "what does the product look like when this stage is done?"). It's documentation about the stage, not a work item, and it's optional: it earns its keep mainly when a stage spans several milestones and you want one dated bar for the whole stage on the Roadmap view. Give it `Start date` / `Target date` on the board to drive the Roadmap timeline.

### Wiring vision to GitHub PM

A cold agent (or new collaborator) joining the project needs to navigate from **"what are we building and why"** (the vision) to **"what's open right now"** (the active work) without round-tripping through tribal knowledge. The wiring is two-way:

**From vision → PM.** Vision and roadmap documents in `notes/` (typically `notes/vision.md`, `notes/roadmap.md`, or both) should **name the GitHub milestone each stage corresponds to.** Example:

```markdown
## 🚲 Bicycle (daily-usable)
> Tracked as GitHub milestone: [Bicycle](../../milestones/3)
> Open epics in this milestone: #14 (auth), #15 (publishing), #16 (feed).
```

With those references, an agent reading `notes/roadmap.md` can jump straight to the live work for the current stage. Without them, the vision doc is a museum piece.

**From PM → vision.** Milestone descriptions in GitHub should point back at the vision doc that explains the stage. A one-line link is enough:

```
See notes/roadmap.md#bicycle for the stage definition and acceptance criteria.
```

Epic descriptions follow the same pattern when they correspond to a named release or feature in the vision: link the relevant section.

**What this gives you.** Two anchored points of truth: the *narrative* (why we're building this, what the stage looks like when done) lives in `notes/`; the *state* (what's open, what's in progress, what's done) lives in GitHub. The links between them keep both navigable.

**Maintenance.** When the roadmap evolves (renaming a stage, splitting an epic, adding a new release), update the vision doc first, then create / rename / re-link the milestones to match. Drift between vision and PM is a real failure mode; treat divergence as a bug.

### Size labels

For estimation (useful in team settings):

| Label | Meaning |
|---|---|
| `size:xs` | < 1 hour |
| `size:s` | Half day |
| `size:m` | 1-2 days |
| `size:l` | 3-5 days |
| `size:xl` | Needs decomposition |

If something is `size:xl`, it's probably an epic that needs to be broken into slices.

---

## Reference

- [Henrik Kniberg's MVP illustration](https://blog.crisp.se/2016/01/25/henrikkniberg/making-sense-of-mvp) (Earliest Testable/Usable/Lovable)
- [GitHub Projects v2 documentation](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [GitHub Issue Forms syntax](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms)
