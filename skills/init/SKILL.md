---
name: init
description: Starts engineering governance for a project. Discovers conventions already in the repo, runs audit, and proposes a small approved batch of debt fixes. Use when asked to initialize Judicious, set up governance, or start paying down structural debt. Asks before it writes; remediation goes through the fix command named in the audit.
argument-hint: "[path]"
license: MIT
---


# init

**Question:** How do we give this project a starting point for engineering governance?

**Mode:** orchestrating. The first pass only reads. Any write waits for approval (**Appendix: Verification**).

## Procedure
1. **Discover conventions** already written down: README, CLAUDE.md, AGENTS.md, architecture or ADR docs, and the manifests. Use those rules. Do not add a plan format, a spec format, or a Judicious process file in order to initialize.
2. **Audit** by calling the Skill tool with `audit` and the same target. That report is the only findings list. If the Skill tool is unavailable, stop.
3. **Triage** the debt into one small batch, ordered by impact. Each item is independently verifiable and names its Locations (see **Appendix: Report**).
4. **Ask** before any edit. Show the batch and its Locations, then stop until the user approves.
5. **Remediate** only the approved items.
   - `consolidate`, `distill` or `harden`: call the Skill tool with that skill and the finding. That command edits and verifies.
   - `placement`: call `placement`. It returns a plan. Implement that plan with the host's own planning only after the user approves the plan itself.
   - **bug fix:** use the host's own planning and editing.
6. **Re-audit** the paths that batch changed by calling `audit` on them.
7. **Record a durable constraint** only after the user agrees. Write it into an existing CLAUDE.md, AGENTS.md or architecture doc. When none of those exist and the user wants a baseline, write a short summary at the path they name. Write a constraint only when the code and the docs already support it.

When the audit reports no debt, stop and say what was checked.

## Output
```
Conventions: path, … | none
Audit: <scope, debt count>
Batch (awaits approval):
1. path:line — category — Fix with: <command> — why this batch
Approved: yes | no
Remediated: path:line — command — verification
Re-audit: …
Constraints written: path | none
Next: …
```
- Before approval, Next is the batch waiting for approval.
- After a batch and its re-audit, Next is the next batch, or `Next: none` when nothing material remains.

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
