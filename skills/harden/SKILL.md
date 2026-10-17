---
name: harden
description: Strengthens existing code where it can go silently wrong — public input/output contracts, error propagation and consistent exception types, invariants, lossy round trips, resource lifecycle, and docs that promise checks which don't exist. Fixes each problem and adds a regression test for it. Use when a critique finding or the user reports swallowed errors, data loss, broken invariants or unenforced guarantees. Edits code; verifies with the project's tests.
argument-hint: "[path, symbol or critique finding]"
license: MIT
---


# harden

**Question:** Where can this code go silently wrong, and how do we make that impossible or loud?

**Mode:** modifying. It edits code under **Appendix: Verification**.

## Input
- **Target:** a path, a symbol, or a finding from an earlier report. When the target is a finding, start from its Locations (see **Appendix: Report**).

## Procedure
1. **For each weak point**, write the failure scenario in one line (input → wrong outcome), with `path:line`.
2. **Write the regression test first** where practical. It should fail on today's code.
3. **Fix it in the existing implementation:**
   - Validate at the trust boundary.
   - Raise the documented exception type, not an empty or default result.
   - Make sibling entry points report the same failure the same way.
   - Carry every field across a round trip, or reject the input explicitly.
   - Enforce the invariant where the state is owned.
   - Make docs match reality: add the promised check, or correct the claim.
4. **Don't invent infrastructure.** Use the language's own errors and the project's existing patterns.
5. **Changing behavior that consumers rely on**, such as a new exception or stricter input, is a contract change. It goes through the approval gate.
6. **Verify** with the project's checks.

## Output
```
Fixed: path:line — failure scenario → new behavior; test: path::test_name
Contract changes (approved?): …
Verification: `<cmd>` → result (baseline → after); not verified: …
Not fixed: path:line — why
Next: …
```
- Next is usually `/judicious critique --changed`. If the root cause is duplicated logic, recommend `/judicious consolidate`.

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
