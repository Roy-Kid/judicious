# Install

Judicious workflows use Markdown instructions and the environment's existing search, editing and verification capabilities. They require no vendor-specific skill tool, planning mode, or subagent API. The integrations below are optional installation adapters.

For any environment, install the needed directories from `skills/` or make their instructions readable. For reuse-first activation, merge the card in [`AGENTS.md`](AGENTS.md) into the project's recognized instruction file.

The examples use `/judicious` (skill `judicious`); actual invocation syntax depends on the environment. The other commands are skills with the same names: `reuse`, `placement`, `critique`, `audit`, `init`, `distill`, `consolidate`, `harden`, `polish`.

## Claude Code

Send these as two separate prompts:

```
/plugin marketplace add Roy-Kid/judicious
```

```
/plugin install judicious@judicious
```

This install includes the reuse-first card at session start. Opt out with `JUDICIOUS_INJECT=0`.

From a checkout:

```bash
claude plugin marketplace add .
claude plugin install judicious@judicious
```

## Grok Build

```bash
grok plugin install Roy-Kid/judicious --trust
```

The plugin is off until you enable it. In `/plugins`, open Plugins and press Space on `judicious`, or add this to `~/.grok/config.toml`:

```toml
[plugins]
enabled = ["judicious"]
```

Start a new session. The skills show up as `/judicious`, `/reuse`, `/critique`, and the rest of the names above. `grok inspect` lists what loaded.

Grok does not load the Claude lifecycle hooks. Its SessionStart output cannot inject instructions, so the always-on card is [`AGENTS.md`](AGENTS.md). Merge that card into the project's recognized instruction file, preserving existing rules.

## Skills CLI

```bash
npx skills add Roy-Kid/judicious
npx skills add Roy-Kid/judicious --skill reuse
```

This copies skill files only. It does not install hooks. For the always-on card, merge [`AGENTS.md`](AGENTS.md) into the project's recognized instruction file.

From a checkout, `npx skills add . --list` lists the ten skills and installs nothing.

## Any agent or environment

Install the skills using the environment's supported discovery mechanism, or make the required `skills/<name>/SKILL.md` files readable and ask the agent to follow them. Load the current instructions for each referenced skill, using a skill loader when available or file/resource access otherwise. Installing only `init` or `audit` does not install the skills they compose; make those definitions accessible too.

For reuse-first activation, merge the card in [`AGENTS.md`](AGENTS.md) into the project's existing instruction file using the filename and location your environment recognizes. Preserve existing project instructions. The card alone does not contain the full skill workflows.

If a required skill definition cannot be accessed, report that missing definition. The absence of a dedicated skill tool or delegation mechanism does not prevent execution.

## Uninstall

| Host | Command |
|---|---|
| Claude Code | `/plugin remove judicious` |
| Grok Build | `grok plugin uninstall judicious` |
| Skills CLI | `npx skills remove judicious reuse placement critique audit init distill consolidate harden polish` |

The skills CLI command takes the same `--agent` and `--global` flags as the install. Remove only the Judicious card from the project instruction file to disable it; preserve unrelated rules.
