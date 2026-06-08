# GitHub PM end-to-end test recipe

> Manual end-to-end smoke test for Kindling's `enable_github_pm=true` scaffolding. Run after non-trivial changes to the bootstrap script, issue templates, or PM docs. Not currently automated (the GitHub API surface for Projects v2 doesn't allow it cleanly).

## 0. Cleanup from prior attempt

```bash
rm -rf /tmp/pm-test
gh repo delete niklastypes/pm-test --yes
# Also: visit https://github.com/users/niklastypes/projects, delete any leftover "pm-test" project.
```

## 1. Scaffold a fresh PM-enabled project

```bash
copier copy gh:niklastypes/kindling /tmp/pm-test --trust \
  --data project_name=pm-test \
  --data project_description="PM end-to-end test" \
  --data author_name="Niklas Baier" \
  --data github_username=niklastypes \
  --data python_version=3.13 \
  --data enable_github_pm=true

cd /tmp/pm-test
```

Sanity-check the rendered files:

```bash
ls .github/ISSUE_TEMPLATE/    # expect: epic.yml slice.yml spike.yml idea.yml bug.yml
ls scripts/bootstrap-pm.sh docs/project-management.md .github/pull_request_template.md
```

## 2. Push to GitHub

```bash
gh repo create pm-test --private --source=. --remote=origin --push
```

## 3. Run the bootstrap script

```bash
./scripts/bootstrap-pm.sh
```

Expected output:

- `[OK] Prerequisites satisfied (...)`
- 12 `[OK] Label: kind:* / horizon:* / priority:*` lines
- `[OK] Created project 'pm-test' (number: N)`
- `[OK] Linked project to repository`
- `[OK] Created field: Start date`
- `[OK] Created field: Target date`
- `==== GitHub PM Bootstrap Complete ====` followed by the 4-step manual checklist.

## 4. Do the 4 manual UI steps from the script's summary

Open the Project URL printed in the script's summary. Then:

1. **Status options.** Project menu `⋯` → Settings → Fields → Status → Edit → add `In Review` (yellow) and `Blocked` (red).
2. **Views.** Click `+` next to view tabs → New view → create at least a Board (drag tabs to taste).
3. **Workflows.** Project Settings → Workflows → enable:
   - Auto-add new issues to project
   - Auto-set Status to `Todo` on new issues
   - Auto-move to `In Review` when a linked PR opens
   - Auto-move to `Done` when issue is closed
4. (Skip the Roadmap-view date-source step unless you create a Roadmap view.)

## 5. Smoke-test each issue template

In the repo's Issues tab → New Issue. Create one of each and confirm the `kind:*` label auto-applies:

- **Epic** — use `As a [user], I want X so that Y` in the description placeholder.
- **Slice** — a small concrete task with acceptance criteria.
- **Spike** — three required fields: question to answer, time box, decision criteria.
- **Idea** — description + Horizon dropdown (defaults to `later`).
- **Bug** — anything.

## 6. Workflow lifecycle smoke test

Pick the Slice issue. On the Project board:

1. Drag it to **Todo**, then to **In Progress**.
2. Locally: `git checkout -b feat/smoke-test`, trivial commit, push.
3. `gh pr create --title "feat: smoke" --body "Fixes #2"` (issue number depends on your repo).
4. Confirm the project workflow moves the issue to **In Review** automatically when the PR opens.
5. Merge the PR. Confirm GitHub closes the issue and the workflow moves it to **Done**.

## 7. Milestone wiring smoke test

1. Repo → Issues → Milestones → New milestone → create `🚲 Bicycle`.
2. Add the Epic issue to that milestone.
3. In `/tmp/pm-test`, create `notes/roadmap.md`:

   ```markdown
   ## 🚲 Bicycle
   > Tracked as GitHub milestone: [Bicycle](../../milestones/1)
   > Open epics: #1
   ```

4. Round-trip check: from the doc you can reach the milestone; the milestone description can link back to the doc.

## 8. Final cleanup

```bash
gh repo delete niklastypes/pm-test --yes
# Also delete the Project on GitHub manually (Projects don't auto-delete with the repo).
rm -rf /tmp/pm-test
```

## Failure escalation

If any step misbehaves, capture the output (with the offending command included) and file it back into the PR or issue thread. Common gotchas:

- **`gh auth status` returns non-zero despite the active account working** — usually a stale inactive account. `gh auth logout -h github.com -u <stale-account>`.
- **`project` scope missing** — `gh auth refresh -s project`.
- **Status-option / view auto-creation** — these are *intentionally* dropped from the script (GitHub API doesn't expose them cleanly). They're step 4's manual checklist.
