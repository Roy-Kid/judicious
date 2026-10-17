---
name: consolidate
description: Merges parallel implementations, duplicated pipelines or overlapping APIs into one canonical implementation, migrates callers and deletes the rest. Use when a critique finding or the user identifies two or more units doing the same job, or entry points whose behavior has drifted apart. Edits code; verifies with the project's tests.
argument-hint: "[paths, symbols or critique finding]"
license: MIT
---


# consolidate

**Question:** Should these implementations become one, and if so, which one stays?

**Mode:** modifying. It edits code under **Appendix: Verification**.

## Input
- **Target:** two or more paths or symbols, or a finding from an earlier report. When the target is a finding, start from its Locations (see **Appendix: Report**).

## Procedure
1. **Inventory:** list every implementation and every consumer, with `path:line`.
2. **Compare the real behavior** of each: inputs, outputs, defaults, errors, side effects, caching. Write the differences as a table.
3. **Decide whether to merge** by applying **Appendix: Disqualifiers**. If consumers need genuinely different semantics, keep the implementations separate, report why, and stop.
4. **Choose the canonical implementation:**
   - the one with the correct behavior on the differences;
   - the most consumers;
   - the right owner.
   For every difference, decide which behavior wins. A difference that is a bug in one copy is fixed, not preserved.
5. **Check the approval gate** in **Appendix: Verification**. Cross-module merges usually require approval: present steps 1–4 and the migration plan.
6. **Migrate the callers** in small batches. Then delete the old implementations and any compatibility leftovers.
7. **Verify** with the project's checks, and add a regression test for each behavior difference you resolved.

## Never
- Create a new shared abstraction just to hide surface duplication.
- Keep both implementations "for compatibility" without a named consumer and a removal date.

## Output
```
Canonical: path:line   Removed: path:line, …
Behavior decisions: <difference> → <chosen behavior> (why)
Changes: path:line — what changed
Verification: `<cmd>` → result (baseline → after); not verified: …
Left over: path:line — why
Next: …
```
- Next is usually `/judicious critique --changed`. If the merge exposed a missing contract, recommend `/judicious harden <path>`.

## Appendix: Disqualifiers

Any one of these rules out reuse, merging or extraction. Record which ones you checked.

- **Semantic mismatch:** inputs, outputs, edge cases or invariants differ from the need. Example: a lossy slugifier named `normalize`.
- **Contract mismatch:** the error model, side effects or stability are unacceptable. Example: a private helper with no stability promise.
- **Invalid dependency direction:** reuse would make a lower or independent unit depend on a higher one, or create a cycle.
- **Lifecycle divergence:** the two sides change for different reasons or owners. Example: a frozen wire format versus a display string.
- **Boundary cost exceeds benefit:** crossing a process, language, ABI or deployment boundary costs more than the duplication it saves.
- **Unproven sharing:** only one real consumer exists today.
- **Policy leakage:** the candidate carries domain policy that the new context must not inherit.
- **Project constraint:** a README, architecture doc, project instruction file or manifest rule forbids it.

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
