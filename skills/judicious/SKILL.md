---
name: judicious
description: Engineering judgment for long-lived code. Entry point for `/judicious <command> [target]`, which routes to reuse, placement, critique, audit, init, distill, consolidate, harden or polish. Use when the user invokes /judicious or asks which engineering-judgment command fits.
argument-hint: "[command] [target or instruction] [--changed] [--focus <topic>]"
license: MIT
---


# judicious

Judicious helps you write only code that has a reason to exist, sits in the right place, and stays maintainable. It supplies judgment only. Search, planning, editing, tests and permissions stay with the host.

## Principles
- Reuse before creating.
- Settle placement before abstraction.
- Each responsibility has one canonical owner.
- Every layer of complexity needs a checkable reason.
- Base judgments on evidence, not on names.
- Prefer the host's native tools.
- Commands are composable and never take over the caller's task.
- Add tooling only once its need is proven.

## Commands
| Command | Skill to invoke | Mode | Question it answers |
|---|---|---|---|
| `audit` | `audit` | read-only | What architecture problems and technical debt does this codebase have? |
| `consolidate` | `consolidate` | modifying | Should these implementations become one, and if so, which one stays? |
| `critique` | `critique` | read-only | What is structurally wrong with the engineering design of this code, and why? |
| `distill` | `distill` | modifying | What here can be deleted or simplified without changing behavior? |
| `harden` | `harden` | modifying | Where can this code go silently wrong, and how do we make that impossible or loud? |
| `init` | `init` | orchestrating | How do we give this project a starting point for engineering governance? |
| `placement` | `placement` | read-only | Where should this code live? |
| `polish` | `polish` | modifying | Is this change ready to merge? |
| `reuse` | `reuse` | read-only | Does a capability that meets this need already exist, and should it be used? |

## Routing
- **No argument:** show the table with one example each, such as `/judicious reuse "parse configuration"`, `/judicious audit` or `/judicious polish`. Run nothing.
- **Typical flow:** `critique` or `audit` finds and locates problems, then each finding's `Fix with` command fixes them, then `critique --changed` re-checks. `init` runs `audit` and then that loop on one approved batch. `polish` checks the current diff before a merge. Every command ends with a Next recommendation.
- **Explicit command:** call the Skill tool with that command's skill, passing the remaining arguments unchanged as `args`. Then follow what the skill loads. Never run a command from memory or look for its files on disk.
- **Natural-language request:** pick the command whose question matches, say which one in one line, then call its skill the same way.
  - Code about to be added → `reuse`.
  - Existing code being judged → `critique`.
  - The whole codebase, or its technical debt → `audit`.
  - Starting governance on a project → `init`.
  - Where code should live, or what to lower into a core library → `placement`.
  - Merging duplicates → `consolidate`.
  - Removing needless code → `distill`.
  - Fixing silent failures and contracts → `harden`.
  - Whether the current change is ready to merge → `polish`.
  - If several fit, ask once.
- **Unknown command:** say it is not available and suggest the closest available command.
- **No Skill tool:** say the command cannot be loaded here. Do not substitute a generic answer.

## Arguments (shared by every command)
- **Target:** a file, directory, package or crate, or a description in words.
- **`--changed`:** limits the scope to the git diff.
- **`--focus <topic>`:** sets a priority. It is not a filter.
- **No target:** each command defines its own default.
