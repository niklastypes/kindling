# GitHub Project Management Integration

> Optional Copier opt-in for projects scaffolded with Kindling: ship a full GitHub PM stack (Milestones + Project Boards + Epics + Issues + Releases + Gantt views) wired up and ready, so big projects can manage real work in GitHub instead of in a monolithic `roadmap.md`.

---

## Motivation

For small projects, a markdown `roadmap.md` + `notes/` brainstorm is perfectly fine. For **big projects** (Niklas's first concrete case: Momo), the markdown roadmap becomes too coarse to manage actual work — it's a vision document, not a project management system.

What's needed for a big project:
- **Milestones** (e.g. "Skateboard," "Scooter," "Bicycle") with target percentage progress visualizations
- **Epics** within milestones (groupable issues, often labeled `epic:agent`, `epic:lifesim`, `epic:hardware` per the three-lane framing Momo uses)
- **Issues** within epics, tagged by lane / size / area
- **Releases** linked to milestones, with auto-generated release notes from conventional commits
- **Gantt / roadmap views** for at-a-glance scheduling
- **Agent-friendly**: an agent can `gh issue list`, pick an issue, work it, transition status, link a PR, mark it done

GitHub now natively supports all of this via Projects v2 (sub-issues, custom fields, multiple views, automation). What's missing is the **Copier scaffold to wire it all up consistently** for every new project that opts in.

## What this should ship

When `kindle` is run with `enable_github_pm=true`:

1. **GitHub repo bootstrap**
   - Create the repo (if remote setup is opt-in)
   - Default branch protection
   - Conventional Commits enforcement (commitlint or similar)
   - Release-please workflow (already part of Kindling) tied to milestones

2. **Project board v2**
   - Create a Project linked to the repo
   - Default views: **Board** (status), **Roadmap** (Gantt-like timeline), **Table** (filterable)
   - Custom fields: `lane` (Agent / Lifesim / Hardware / Observability), `size` (XS-XL), `epic` (parent issue reference)

3. **Milestones**
   - Optional starter set of milestones from the project's roadmap (e.g. parse `roadmap.md` for stage headers and create milestones from them). Probably gated behind a second question; for Momo I'd pre-create Bus Ticket / Skateboard / Scooter / Bicycle / Motorcycle / Car / Convertible.

4. **Issue templates**
   - `epic.yaml`: parent issue template, links sub-issues, has a checklist
   - `slice.yaml`: standard work item, has lane / milestone / epic fields
   - `bug.yaml`: standard bug template

5. **Labels**
   - `lane:agent`, `lane:lifesim`, `lane:hardware`, `lane:observability`, `lane:cross`
   - `size:xs` through `size:xl`
   - `kind:epic`, `kind:slice`, `kind:bug`
   - `priority:p0` through `p3`

6. **Workflows**
   - Auto-link PRs to issues via `Fixes #N` convention
   - Auto-close issues on merge
   - Release-please tied to milestone closure
   - (Optional) auto-comment on issue when an agent claims it (via `claude` or `gh` action)

7. **Documentation in the generated repo**
   - `CONTRIBUTING.md` explains the lane / milestone / epic conventions
   - `CLAUDE.md` gets a section: "agents pulling issues should follow this lifecycle: claim → in-progress → PR → review → merge → closed"

## Why this is a Kindling concern, not a Momo concern

Two reasons:

1. **Reusability.** Niklas wants this for Momo *now*, but the pattern will apply to any future big project he scaffolds (Tavern, Vox Machina's successors, etc.). Kindling is the place for cross-project conventions.
2. **Generated projects should be agent-friendly out of the box.** Kindling already ships `.claude/` scaffolding (or considers it). Wiring up GitHub Projects so an agent can navigate the work plan natively belongs in the same opt-in.

## Niklas's intent for Momo

> "I think this is more of a Kindling thing, so we should make a note there. But that's something we should do before we actually start scaffolding Momo from Kindling."

Translation: **Momo's Bus Ticket release (in [empyrean/momo/notes/roadmap.md](https://github.com/niklas-baier/empyrean)) is blocked on Kindling shipping this feature.** Not a hard block forever — could ship Momo without it and retrofit — but the preferred order is:

1. Ship this Kindling feature
2. `kindle momo` with `enable_github_pm=true`
3. Start Momo's Bus Ticket work, tracked in GitHub

## Open questions

- **Project scope**: organization-level Project vs repo-level Project. Org-level is more flexible (cross-repo views) but more setup.
- **Custom field schemas**: how generic vs how opinionated? My lean: provide a sensible default that matches Momo's three-lane shape, let users add fields per project.
- **Roadmap.md → milestone parser**: nice-to-have but not v1. Manual milestone creation works for v1.
- **GitHub Free vs paid**: Projects v2 features available to all? Gantt-style roadmap views I think need GitHub Pro / Teams. Worth confirming.
- **`gh` CLI vs API for the bootstrap**: `gh` CLI handles auth + has commands for projects. Lean toward `gh` for the Copier post-generation hook.

## Next steps

1. Confirm with Niklas this is the right scope for the first cut
2. Open a GitHub issue on Kindling (`niklastypes/kindling`) tracking this feature
3. Spike the `gh project create` + custom-field setup as a shell script first; integrate into Copier task hook second
4. Update Kindling's Copier questionnaire to add the `enable_github_pm` question
5. Test against a throwaway repo before sending Momo through it
