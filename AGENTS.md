# Judicious

JUDICIOUS reuse-first is active.

Before writing a new function, class, module, helper, CLI option, parser, retry or validation logic, or adding a dependency:
- Search outward from where you are: the current file and module, then the package API, then other workspace packages, then declared dependencies and the standard library.
- Reuse something only when its semantics, contract and dependency direction fit. A matching name does not mean matching behavior.
- Call the existing code directly. Don't add a forwarding wrapper.
- Don't extract a shared module just to save a few lines between independent units.
- If nothing fits, create the code where it belongs.
- In your final summary, name what you reused (with its path), or say what you searched and why new code was needed.
- If the decision is non-trivial or ambiguous, invoke the `reuse` skill.

## Skills

The commands are skills under `skills/<name>/SKILL.md`. The unified entry is `/judicious` (skill `judicious`). It routes to `reuse`, `placement`, `critique`, `audit`, `init`, `distill`, `consolidate`, `harden`, and `polish`.

Copy this file into a project when the host cannot inject the card itself. Install steps are in `INSTALL.md`.
