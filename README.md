# Judicious

Engineering judgment for AI coding agents. Judicious helps an agent write only code that has a reason to exist, sits in the right place, and can be maintained.

It is Markdown skills only: no runtime, no AST, no MCP server. Search, planning, editing and tests are left to the host agent. The full design is in [docs/spec-v0.3.md](docs/spec-v0.3.md).

## Commands

| Command | Mode | Question |
|---|---|---|
| `/judicious reuse [need]` | read-only | Does a capability that meets this need already exist? |
| `/judicious critique [path]` | read-only | What is structurally wrong with this design? Always fans out to subagents. |
| `/judicious audit [path]` | read-only | What architecture problems and technical debt does this codebase have? |
| `/judicious placement [path or finding]` | read-only | Where should this code live: keep, move, extract, lower (e.g. into a core library) or remove? |
| `/judicious init [path]` | orchestrating | Discover existing conventions, audit, and remediate one approved batch. |
| `/judicious consolidate [finding]` | edits code | Merge parallel implementations or APIs into one. |
| `/judicious distill [finding]` | edits code | Remove code that has no reason to exist, preserving behavior. |
| `/judicious harden [finding]` | edits code | Make silent failures loud: contracts, errors, invariants, lossy round trips. |
| `/judicious polish` | edits code | Is the current change ready to merge? Applies only small, local fixes. |

`/judicious` with no argument lists them. Each command is also a skill whose `name` matches the command (`reuse`, `critique`, …).

**Flow:**
1. `critique` or `audit` locates every problem at `path:line` and tags it with `Fix with: consolidate | distill | harden | placement | bug fix`.
2. The fix command starts from those Locations instead of searching again.
3. `init` runs `audit`, then that same loop on one approved batch.
4. `polish` checks the current diff before a merge.
5. Every command ends with a **Next** recommendation, usually `critique --changed` to re-check.

Commands that edit code run the project's own tests before and after. They ask for approval before changing a public API, touching more than about 5 files, or crossing repositories.

**Two activation styles.**
- **Before implementation:** install the `reuse` skill. Its description is written so the agent loads it before adding code. A Claude plugin install also injects a short reuse-first card at session start. Opt out of that card with `JUDICIOUS_INJECT=0`.
- **Manual checks:** invoke `critique`, `audit`, `placement`, `init`, `distill`, `consolidate`, `harden` or `polish`.

## Install

Full steps, including uninstall, are in [INSTALL.md](INSTALL.md). The public repo is [Roy-Kid/judicious](https://github.com/Roy-Kid/judicious). Installs are what list it on [skills.sh](https://skills.sh).

```bash
npx skills add Roy-Kid/judicious
npx skills add Roy-Kid/judicious --skill reuse
```

```text
/plugin marketplace add Roy-Kid/judicious
/plugin install judicious@judicious
```

```bash
grok plugin install Roy-Kid/judicious --trust
```

`npx skills add` installs the skill files only. The reuse-first hook ships with the Claude plugin. On hosts that cannot inject it, copy [AGENTS.md](AGENTS.md).

## Layout

```
skills/<name>/SKILL.md       one self-contained skill; directory name is the frontmatter name
skills.sh.json               how skills.sh groups this repo's page
.claude-plugin/              plugin.json + marketplace.json (source: ./)
.grok-plugin/marketplace.json  Grok marketplace index (source: ./)
plugin.json                  Grok plugin name
hooks/                       Claude-plugin-only reuse-first injection
AGENTS.md                    the same reuse-first card, for hosts that cannot inject it
INSTALL.md                   Claude, Grok, skills CLI, and uninstall
tests/                       structural checks for the store layout
```

## Develop

```bash
python3 -m unittest discover -s tests -v
npx skills add . --list
claude plugin validate .
grok plugin validate .
```
