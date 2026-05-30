# GitHub Project Management Integration

> Optional Copier opt-in for projects scaffolded with Kindling: ship a full GitHub PM stack (Milestones + Project board + Sub-issue tree + Releases) wired up and ready, so big projects can manage real work in GitHub as the single source of truth instead of in a monolithic `roadmap.md`.

---

## Motivation

For small projects, a markdown `roadmap.md` + `notes/` brainstorm is perfectly fine. For **big projects** (Niklas's first concrete case: Momo), `roadmap.md` becomes too coarse to manage actual work, and keeping a markdown plan in sync with what's actually in-flight is a chore. The intent is to make the **GitHub Project the SSoT** for in-flight work, and let the in-repo roadmap shrink to a short "shape of the plan" intro.

What a big project needs:
- **Stages** (e.g. "Bus Ticket," "Skateboard," "Bicycle") visible on a timeline as horizontal bars (the Gantt feel)
- **Release clusters** within each stage (groupable work that ships together)
- **Slices** within each release cluster, tagged by lane / size / priority
- **Idea capture** in the same system: visionary ideas and near-term ones, with a clean promotion ritual into real work
- **Releases** auto-generated from conventional commits, linked to milestones
- **Agent-friendly**: an agent can `gh issue list`, pick an issue, work it, transition status, link a PR, mark it done

GitHub Projects v2 covers all of this natively. What's missing is the **Copier scaffold to wire it all up consistently** for every new project that opts in.

## The mapping (locked in)

```
Milestone        = MVP stage (Bus Ticket, Skateboard, Scooter, ...)
Stage issue      = one issue per Milestone with kind:stage label + start/target dates
                   (drives the Roadmap Gantt; anchors stage-level context)
Epic issue       = release cluster (e.g. "personality + chat baseline")
                   sub-issue of the Stage issue
Slice issue      = atomic work item, sub-issue of an Epic
Lane             = single-select Project field (Agent / Lifesim / Hardware / Observability / Cross)
```

Why this mapping:
- **One stage → one milestone** gives you the built-in milestone progress page + a clean `gh issue list --milestone Skateboard`
- **Stage issues with dates** give you the actual horizontal Gantt on the Roadmap view (Milestones alone don't render on Roadmap; issues with date fields do)
- **Release cluster = Epic** preserves the "ship this together" coherence across lanes, which `epic-per-lane` mappings break
- **Lane as a Project field** (not a label) lets you slice "show me all Hardware work across all stages" cleanly, and grouping the Board view by Lane gives the lanes×stages density visualization for free
- **Sub-issue tree** (Stage → Epic → Slice) is native GitHub now and surfaces cleanly via the API

## What this should ship

When `kindle <project>` is run with `enable_github_pm=true`:

### 1. Repo + branch hygiene
- Create the GitHub repo (if remote setup is opt-in)
- Default branch protection
- Conventional Commits enforcement (commitlint or similar) — already part of Kindling
- Release-please workflow tied to milestones — already part of Kindling

### 2. Project v2 with saved views
- Create a Project linked to the repo
- Custom fields:
  - `Lane`: single-select — Agent / Lifesim / Hardware / Observability / Cross (defaults; customizable per project)
  - `Start date` + `Target date`: dates (used by the Roadmap view)
  - `Iteration`: optional, off by default
- Default saved views:
  - **Build plan** (Roadmap): timeline of Stage + Epic issues. The Gantt. Excludes `kind:idea` and `horizon:far`.
  - **Board** (Kanban): grouped by Status. Excludes ideas + far horizon.
  - **By lane** (Board): grouped by `Lane` field. Filtered to current stage's Milestone by default.
  - **Backlog**: `kind:idea` + `horizon:near|maybe`. Where new ideas land before commitment.
  - **Horizon**: only `horizon:far`. The visionary watchlist; replaces the "Galaxy's Edge" section that used to live in roadmap.md.
  - **Table**: filterable catch-all.

### 3. Milestones
Optional second Copier question: parse the project's `roadmap.md` for stage headers and pre-create the matching milestones. For Momo specifically: pre-create Bus Ticket / Skateboard / Scooter / Bicycle / Motorcycle / Car / Convertible.

For each milestone created, also create a corresponding Stage issue with `kind:stage`, the stage's description as the body, and `Start date` / `Target date` fields (initially unset — Niklas fills them in or accepts the auto-spread).

### 4. Issue templates
- `stage.yaml`: stage-tracker template (one per milestone). Has acceptance summary + links + date hint.
- `epic.yaml`: release cluster template. Has lane breakdown checklist, links to parent Stage.
- `slice.yaml`: atomic work item. Has `Lane` field, links to parent Epic.
- `idea.yaml`: new idea template. Has `horizon:*` selector, "why this is interesting" prompt.
- `bug.yaml`: standard bug template.

### 5. Labels
Since Issue Types are an org-only GitHub feature and Kindling targets personal accounts too, we use labels for `kind`:

- **kind**: `kind:stage`, `kind:epic`, `kind:slice`, `kind:idea`, `kind:bug`, `kind:chore`
- **horizon** (idea backlog): `horizon:near`, `horizon:far`, `horizon:maybe`
- **size**: `size:xs` through `size:xl`
- **priority**: `priority:p0` through `priority:p3`
- **area** (optional, per-project): `area:*`

(If a project lives under an org and the user later wants to upgrade, a one-shot migration script can convert `kind:*` labels to Issue Types. Not in v1.)

### 6. Workflows
- Auto-link PRs to issues via `Fixes #N` convention
- Auto-close issues on merge
- Release-please tied to milestone closure (closing a milestone tags a release)
- Auto-add new issues to the Project
- Auto-set `Status: Todo` on new issues

### 7. Idea capture flow

Ideas live as issues with `kind:idea` + a `horizon:*` label. They sit in the Backlog or Horizon views. **Promotion ritual** when an idea graduates to committed work:

1. Drop `kind:idea`, add `kind:slice` (or `kind:epic`)
2. Assign a Milestone + parent Epic (via sub-issue link)
3. Drop the `horizon:*` label
4. Set `Lane` field

The issue keeps its full comment history. No copy-paste between systems.

### 8. Documentation in the generated repo
- `CONTRIBUTING.md` explains the lane / stage / epic / idea conventions
- `CLAUDE.md` gets a section: "agents pulling issues should follow this lifecycle: pick from `kind:slice` in current milestone → set Status:In Progress → open PR with `Fixes #N` → review → merge → Status:Done auto-set"
- `roadmap.md` retires to a slim ~30-line intro pointing at the Project URL (see "Graduation" below)

## Why this is a Kindling concern, not a per-project concern

Two reasons:

1. **Reusability.** Niklas wants this for Momo now, but the pattern applies to any future big project he scaffolds. Kindling is the place for cross-project conventions.
2. **Generated projects should be agent-friendly out of the box.** Kindling already ships `.claude/` scaffolding. Wiring up GitHub Projects so an agent can navigate the work plan natively belongs in the same opt-in.

## Graduation: how a project moves from roadmap.md SSoT to Project SSoT

Three phases:

1. **Pre-graduation** (project still in Empyrean): `roadmap.md` is the SSoT, no GitHub Project exists. The repo doesn't exist yet.
2. **At `kindle <project>` with `enable_github_pm=true`**: Kindling bootstraps the GitHub Project from `roadmap.md`'s content:
   - Creates Milestones for each stage header
   - Creates `kind:stage` issues per Milestone with the stage description as body
   - Creates `kind:epic` issues per release cluster, as sub-issues of their Stage
   - Optionally creates `kind:slice` issues per slice (might be a separate "deep import" mode; v1 can leave Slices as a manual follow-up)
   - Migrates the Galaxy's Edge / visionary section into `kind:idea` + `horizon:far` issues
3. **Post-graduation**: GH Project is the SSoT for in-flight work. `roadmap.md` slims to a ~30-line intro: vision statement + lanes/stages glossary + lanes×stages mermaid + link to the Project URL. The detailed slice content lives in issues. The slim roadmap.md stays in the repo because new readers and future-Niklas need an entry point that doesn't require opening the Project board to grasp the *shape* of the plan.

## Niklas's intent for Momo

> "I think this is more of a Kindling thing, so we should make a note there. But that's something we should do before we actually start scaffolding Momo from Kindling."

Translation: **Momo's Bus Ticket release is blocked on Kindling shipping this feature.** Not a hard block forever (Momo could be scaffolded without it and retrofit later), but the preferred order is:

1. Ship this Kindling feature
2. `kindle momo` with `enable_github_pm=true`
3. Momo's `roadmap.md` content auto-bootstraps the Project, then slims to its ~30-line intro
4. Start Momo's Bus Ticket work, tracked in GitHub

## Open questions

- **Project scope**: repo-level vs org-level Project. Since `niklastypes` is a personal account, repo-level is the only realistic option. Reconsider only if there's ever a future org.
- **Slice auto-import at bootstrap**: v1 might only import Stages + Epics; Slice creation stays manual. Less risk of stale slices in the Project on day one. Reconsider after Momo bootstrap experience.
- **GitHub feature tier**: Projects v2 + sub-issues + Roadmap view all confirmed available on free accounts. No tier upgrade needed.
- **`gh` CLI vs API for bootstrap**: lean `gh` for repo + issues, `gh api graphql` for Project v2 field setup (the `gh project` subcommands are still limited as of this writing).
- **`research/horizon.md` redundancy**: once `horizon:far` issues exist, `horizon.md` overlaps with the Horizon view. Decision deferred until post-Momo-bootstrap; one option is to keep `horizon.md` for emerging-tech research that's too long-form for an issue body, and let `horizon:far` issues be project-specific ideas.

## Next steps

1. Open a GitHub issue on Kindling (`niklastypes/kindling`) tracking this feature
2. Spike the `gh project create` + custom-field setup + label set as a shell script first; integrate into Copier task hook second
3. Spike the `roadmap.md` → Milestones + Stage issues + Epic issues bootstrap parser
4. Update Kindling's Copier questionnaire to add the `enable_github_pm` question (+ sub-question for `bootstrap_from_roadmap`)
5. Test against a throwaway repo before sending Momo through it
6. Update Momo's `roadmap.md` post-bootstrap to its slim ~30-line form
