# Install

Pick one host. For an agent that is not listed, copy [`AGENTS.md`](AGENTS.md) into the project, or install one directory from `skills/` as a skill.

The slash entry is `/judicious` (skill `judicious`). The other commands are skills with the same names: `reuse`, `placement`, `critique`, `audit`, `init`, `distill`, `consolidate`, `harden`, `polish`.

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

Grok does not load the Claude lifecycle hooks. Its SessionStart output cannot inject instructions, so the always-on card is [`AGENTS.md`](AGENTS.md). Copy that file into the project, or work from a checkout of this repo.

## Skills CLI

```bash
npx skills add Roy-Kid/judicious
npx skills add Roy-Kid/judicious --skill reuse
```

This copies skill files only. It does not install hooks. For the always-on card, also copy [`AGENTS.md`](AGENTS.md).

From a checkout, `npx skills add . --list` lists the ten skills and installs nothing.

## Other agents

Codex, Copilot, Gemini, OpenCode, and an npm package are not part of 0.1. Use [`AGENTS.md`](AGENTS.md) or `npx skills add Roy-Kid/judicious`.

## Uninstall

| Host | Command |
|---|---|
| Claude Code | `/plugin remove judicious` |
| Grok Build | `grok plugin uninstall judicious` |
| Skills CLI | `npx skills remove judicious reuse placement critique audit init distill consolidate harden polish` |

The skills CLI command takes the same `--agent` and `--global` flags as the install. Deleting a copied `AGENTS.md` removes the always-on card.
