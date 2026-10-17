---
name: init
description: Starts engineering governance for a project. Discovers conventions already in the repo, runs audit, and proposes a small approved batch of debt fixes. Use when asked to initialize Judicious, set up governance, or start paying down structural debt. Asks before it writes; remediation goes through the fix command named in the audit.
argument-hint: "[path]"
license: MIT
---


# init

**Question:** How do we give this project a starting point for engineering governance?

**Mode:** orchestrating. The first pass only reads. Any write waits for approval (**Appendix: Verification**).

## Loading skills
When this workflow uses another skill, load its current instructions and follow them with the supplied target and arguments. Use the environment's skill-loading mechanism when available; otherwise read the matching installed `SKILL.md` using file or resource access. In a source checkout, skills live at `skills/<name>/SKILL.md`. Resolve names within the Judicious package to avoid unrelated skills with the same name. No particular tool name or invocation syntax is required. If the required instructions cannot be accessed, report the missing skill and stop that dependent step; do not reconstruct it from memory.

## Procedure
1. **Discover conventions** already written down: README, project instruction files, architecture or ADR docs, and the manifests. Use those rules. Do not add a plan format, a spec format, or a Judicious process file in order to initialize.
2. **Audit** by loading and following `audit` with the same target. That report is the only findings list.
3. **Triage** the debt into one small batch, ordered by impact. Each item is independently verifiable and names its Locations (see **Appendix: Report**).
4. **Ask** before any edit. Show the batch and its Locations, then stop until the user approves.
5. **Remediate** only the approved items.
   - `consolidate`, `distill` or `harden`: load and follow that skill with the finding. That command edits and verifies.
   - `placement`: load and follow `placement` with the finding. It returns a plan. Implement that plan with the host's own planning only after the user approves the plan itself.
   - **bug fix:** use the host's own planning and editing.
6. **Re-audit** the paths that batch changed by loading and following `audit` on them.
7. **Record a durable constraint** only after the user agrees. Write it into an existing project instruction file or architecture doc. When none of those exist and the user wants a baseline, write a short summary at the path they name. Write a constraint only when the code and the docs already support it.

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
