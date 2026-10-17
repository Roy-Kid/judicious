---
name: polish
description: Pre-merge check of the current change. Looks for missed reuse, new duplication, wrong placement, new public APIs, leftover dead code and skipped tests, and applies small safe fixes. Use when asked whether a diff is ready to merge, or to polish the current change. Edits code; verifies with the project's tests.
argument-hint: "[path] [--focus <topic>]"
license: MIT
---


# polish

**Question:** Is this change ready to merge?

**Mode:** modifying. It edits code under **Appendix: Verification**.

## Input
- **No target:** the git diff, including unstaged changes, plus the code it calls and the code that calls it.
- **A path:** limit the check to the diff inside that path.
- **`--focus <topic>`:** look at that topic first. It sets priority; it does not filter.

## Check the diff
For each new or changed unit, answer these. Cite `path:line` (see **Appendix: Report**).

1. **Reuse.** Does an existing capability already do this? When a new helper resembles one, call the Skill tool with `reuse` and the need, then apply its decision.
2. **Duplication.** Did this change add a parallel implementation or API?
3. **Placement.** Does the new code sit in the unit that owns that responsibility?
4. **Public API.** Did this change add or change an exported symbol?
5. **Leftovers.** Did it leave a dead implementation, an unused shim or a speculative abstraction?
6. **Verification.** Did the project's tests, build and lint run for this change?

Judge reuse, merging and extraction against **Appendix: Disqualifiers**.

## What you may change
Change it here when the edit stays local: it keeps the public API, it stays inside one package, and it touches about 5 files or fewer. A local fix deletes unused local code, calls an existing function instead of a new copy, or inlines a forwarding-only wrapper.

A cross-package move, a public-API migration or a lowering stays a recommendation, with Locations, for `consolidate`, `distill`, `harden` or `placement`.

## Output
```
Scope: <diff, revision>
Ready: yes | no
Checked:
- Reuse: …
- Duplication: …
- Placement: …
- Public API: …
- Leftovers: …
- Verification: `<cmd>` → result | not verified: why
Fixed: path:line — what changed
Left: path:line — which command should do it
Next: …
```
- When Ready is yes and nothing material remains, Next is `Next: none`.
- Otherwise Next is the command for the highest-impact leftover, with its exact target.

## Appendix: Disqualifiers

Any one of these rules out reuse, merging or extraction. Record which ones you checked.

- **Semantic mismatch:** inputs, outputs, edge cases or invariants differ from the need. Example: a lossy slugifier named `normalize`.
- **Contract mismatch:** the error model, side effects or stability are unacceptable. Example: a private helper with no stability promise.
- **Invalid dependency direction:** reuse would make a lower or independent unit depend on a higher one, or create a cycle.
- **Lifecycle divergence:** the two sides change for different reasons or owners. Example: a frozen wire format versus a display string.
- **Boundary cost exceeds benefit:** crossing a process, language, ABI or deployment boundary costs more than the duplication it saves.
- **Unproven sharing:** only one real consumer exists today.
- **Policy leakage:** the candidate carries domain policy that the new context must not inherit.
- **Project constraint:** a README, architecture doc, CLAUDE.md, AGENTS.md or manifest rule forbids it.

When one of these holds, the usual answer is `CREATE`, `EXTEND` behind a separate entry point, or keeping the implementations apart.

## Appendix: Verification

These rules apply to every command that edits code.

### Before editing
- Find the project's own checks: test, build, lint and type-check commands from the README, CONTRIBUTING, CI workflows, the Makefile or the package manifest.
- Run the relevant tests first, and record the baseline result. A failure that already exists is not yours to explain away later.
- Ask for approval first, presenting the plan with its Locations, when the change would:
  - change or remove a public API or exported symbol;
  - touch more than about 5 files, or cross package or repository boundaries;
  - change behavior that consumers outside the repo may rely on;
  - go ahead without any test you can run.
- Otherwise, proceed.

### While editing
- Make small batches, each one verifiable on its own.
- Preserve correctness, error handling, observable behavior and public contracts, unless the finding is exactly about changing them.
- Use the host's own editing and planning tools. Add no new infrastructure.

### After editing
- Re-run the same checks and compare them with the baseline.
- For every fixed defect, add or update one regression test that fails without the fix.
- Report every command you ran and its result. If you could not run something, say "not verified" and give the reason. Never claim an unverified change works.

## Appendix: Report

Every Judicious report follows these rules.

### Locate everything
- Each issue, candidate or change cites the exact `path:line` (or a line range) of every place involved. That covers the definition, the call sites to change, and the manifest or doc line.
- **Locations** is the to-do list for whoever acts on the finding. List every place that must change, not just one example.
- Never report an issue without a location. If you cannot locate it, say so and lower the confidence.
- When acting on an earlier report, start from its Locations. Re-read them to verify, but do not search for them again.

### End with the next step
- The last section is **Next**: one to three recommended commands, in order, each with its exact target and a one-line reason.
  - Example: `/judicious harden src/molpy/engine/_openmm.py:440-444`, because NVE silently runs a thermostat.
- Recommend only commands that exist. If the right move is a plain bug fix or a native plan, say that instead.
- If nothing is left to do, write `Next: none` and give the reason.
