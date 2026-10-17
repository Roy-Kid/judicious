# Judicious — repository guide

Markdown-only skills. Spec: `docs/spec-v0.3.md` (Chinese, authoritative for intent). Agent-facing files are in English. Workflows are independent of the agent; this filename is an installation adapter.

## Where things live

| Need | Path |
|---|---|
| A command | `skills/<name>/SKILL.md`. The directory name is the skill `name`. This file is the source of truth, and it is self-contained. |
| Router | `skills/judicious/SKILL.md` |
| Store page grouping | `skills.sh.json` |
| Claude plugin manifest | `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` (`source` is `./`) |
| Grok plugin manifest | `plugin.json` (`hooks` is empty) and `.grok-plugin/marketplace.json` (`source` is `./`) |
| Always-on card when a host cannot inject | `AGENTS.md` (same text as `hooks/session-start.json`) |
| Install steps | `INSTALL.md` |
| Reuse-first hook (Claude plugin only) | `hooks/`. `npx skills add` does not install hooks. |

## Invariants

1. Edit `skills/<name>/SKILL.md` directly. There is no build step.
2. Each skill stays self-contained: no links to other files in the repo, and no vendor-specific environment-variable reads. The store installs one skill directory at a time.
3. The router selects by the skill `name` (`critique`, `reuse`, …) and loads its instructions through the available skill loader or file/resource access. It holds no command rules. No named tool is required.
4. Adding a command means one new `skills/<name>/SKILL.md` whose frontmatter `name` matches the directory, plus a row in the router and in `skills.sh.json`.
5. Read-only is enforced in the playbook text, not with `disallowed-tools`.
6. Two activation styles:
   - **Before implementation:** the `reuse` skill, plus the reuse-first card through project instructions or optional lifecycle hooks.
   - **Manual checks:** the user invokes the skill by name.
7. Do not add a runtime, more hooks or MCP servers without measured evidence (spec §9, Stage 7).

## Commands

    python3 -m unittest discover -s tests -v
    npx skills add . --list
    claude plugin validate .
    grok plugin validate .
