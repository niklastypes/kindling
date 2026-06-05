# Project Management

This project uses GitHub Projects v2 for work tracking, with issue templates and a label system to keep things consistent.

---

## Issue Types

### Epic (`kind:epic`)

A release cluster that groups related slices. Use epics when a meaningful outcome requires multiple pieces of work.

**Example:** "User authentication" (requires login page, API auth middleware, password reset, session management).

Epics track progress through a checklist of linked slices. They're done when all slices are done.

### Slice (`kind:slice`)

An atomic vertical slice of work that delivers observable value. Slices cut through all layers (UI, logic, data) and should be small enough to complete in one PR.

**Example:** "Users can log in with email and password" (touches the login form, the auth API endpoint, and the session store).

This is the default work unit. When in doubt, create a slice.

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

### Kniberg staging

For projects that benefit from staged delivery (Henrik Kniberg's "Walking Skeleton" approach):

1. Create `kind:stage` label for stage issues
2. Create milestones for each stage (e.g., "Stage 1: Walking Skeleton", "Stage 2: Core Features")
3. Assign slices to milestones to plan delivery order

Stage issues describe what the product looks like at each stage. They're documentation, not work items.

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
