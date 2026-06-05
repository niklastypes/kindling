# Ubiquitous Language

> A convention for managing the design vocabulary of a project.

Most projects grow their own terminology as they mature: names for internal concepts, states, layers, lifecycle verbs. When that vocabulary is load-bearing (each term encodes a design rule), it should live in **one canonical home**, not scattered across brainstorms, design docs, code comments, and PR descriptions.

The convention is borrowed from Domain-Driven Design's [*ubiquitous language*](https://martinfowler.com/bliki/UbiquitousLanguage.html): one shared vocabulary, kept in one definitive place, referenced from everywhere else.

## Why

When the same term is redefined loosely across multiple docs, the design rules attached to it drift. Six months later, two design discussions can be using the same word to mean subtly different things, and neither participant knows. A canonical home plus brief in-place references keeps onboarding cheap, design discussions coherent across time, and refactors safe.

## When to adopt this

Not every project needs a ubiquitous language. The trigger is **vocabulary density**, not project size. Adopt this convention when either holds:

1. The project has **three or four design-rule-bearing terms** referenced in multiple files. Decorative names (mascot, codename) do not count; terms that *encode a design rule* do (a state-machine state, an architectural layer, a domain object, a lifecycle verb).
2. The same term has been **defined inconsistently** across multiple notes. That is a clear signal the canonical home is missing.

Do not pre-create the file for a young project. The value comes from accumulation; an empty glossary attracts low-quality entries.

## Where it lives

- If the project has a `notes/` folder: `notes/ubiquitous-language.md`.
- Otherwise: `docs/ubiquitous-language.md`.

Pick one and stay consistent; do not split the glossary across both. Reference it from `AGENTS.md` (or `CLAUDE.md`) so agents working on the project know to consult it.

## Scope

The glossary covers the project's *internal* design language only. Out of scope:

- **Framework or library vocabulary** (FastAPI's "dependency", Vue's "ref"). Documented upstream; redefining invites drift.
- **Generic engineering terms** (REST, idempotent, mutex). Well-defined elsewhere.
- **Public product copy** (marketing names, user-facing labels). Different goals, different timescales.

The dividing line: if the term describes *how this specific project is built*, it is in scope. If it is documented elsewhere, link to that elsewhere instead.

## Shape of an entry

The entry shape is what makes the glossary useful at a glance:

```markdown
### TermName

One-phrase definition.

**Load-bearing meaning:** one sentence explaining the design rule the
term encodes. If you cannot write this sentence, the term probably is
not load-bearing.

**Examples:** 1-2 concrete usages or pointers into the codebase.
```

The **Load-bearing meaning** line is the hardest and most important part. A term without one is decoration, not vocabulary, and does not earn an entry.

Group entries by category (`## Domain objects`, `## Lifecycle states`, etc.) so the file stays scannable as it grows.

## DRY: trim in-place mentions

Once the glossary exists, the next time you edit a doc that redefines a glossary term, trim the redefinition to a brief mention plus a link. Incremental, not a one-shot rewrite.

- Good: "The pipeline runs in **batch mode** ([glossary](../notes/ubiquitous-language.md#batch-mode)) when..."
- Bad: "Batch mode means the pipeline reads inputs in chunks rather than streaming, with a checkpoint between each chunk..." (this belongs in the glossary entry, not here)

## How to extend

A new term earns an entry when:

1. **It is already in use.** Aspirational vocabulary does not earn an entry.
2. **It encodes a design rule.** Decorative terms do not earn an entry.
3. **There is no near-synonym already covered.** Variants get a note on the existing entry, not a new entry.

When a term turns out to be wrong or unused, remove it. The glossary bears the cost of staying current.
