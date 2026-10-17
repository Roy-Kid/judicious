"""Structural checks for the skills.sh layout.

Run: python3 -m unittest discover -s tests -v
Stdlib only.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILLS = REPO / "skills"
MAX_DESCRIPTION = 1024
MAX_INJECT_WORDS = 160
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REUSE_DECISIONS = {"REUSE", "COMPOSE", "EXTEND", "REPLACE", "CREATE", "UNRESOLVED"}
SEARCH_OUTCOMES = {"FOUND", "NOT_FOUND_IN_SCOPE", "UNKNOWN"}
MODES = {"read-only", "modifying", "orchestrating"}


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        raise AssertionError(f"{path}: missing frontmatter")
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if not sep:
            raise AssertionError(f"{path}: bad frontmatter line {line!r}")
        fields[key.strip()] = value.strip()
    return fields


def body(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.S)


class LayoutTests(unittest.TestCase):
    def test_store_layout(self):
        self.assertFalse((REPO / "SKILL.md").exists(), "a root SKILL.md shadows skills/")
        self.assertFalse((REPO / "scripts").exists())
        self.assertFalse((REPO / "src").exists())
        self.assertFalse((REPO / "plugins").exists())
        skills = sorted(p for p in SKILLS.iterdir() if p.is_dir())
        self.assertTrue(skills)
        for skill in skills:
            self.assertEqual(list(skill.glob("SKILL.md")), [skill / "SKILL.md"])

    def test_marketplace_points_at_this_repo(self):
        plugin = json.loads((REPO / ".claude-plugin" / "plugin.json").read_text())
        market = json.loads((REPO / ".claude-plugin" / "marketplace.json").read_text())
        self.assertEqual(plugin["name"], "judicious")
        entries = {e["name"]: e for e in market["plugins"]}
        self.assertEqual(entries["judicious"]["source"], "./")
        self.assertEqual(market["owner"]["url"], "https://github.com/Roy-Kid")
        self.assertFalse((REPO / "commands").exists())

    def test_grok_and_agents_card(self):
        grok_name = json.loads((REPO / "plugin.json").read_text())
        grok_market = json.loads((REPO / ".grok-plugin" / "marketplace.json").read_text())
        self.assertEqual(grok_name["name"], "judicious")
        self.assertEqual(grok_name["hooks"], "")
        entries = {e["name"]: e for e in grok_market["plugins"]}
        self.assertEqual(entries["judicious"]["source"], "./")
        self.assertEqual(grok_market["owner"]["url"], "https://github.com/Roy-Kid")
        card = (REPO / "AGENTS.md").read_text(encoding="utf-8")
        context = json.loads((REPO / "hooks" / "session-start.json").read_text())
        injected = context["hookSpecificOutput"]["additionalContext"]
        self.assertIn(injected, card)
        install = (REPO / "INSTALL.md").read_text(encoding="utf-8")
        self.assertIn("Roy-Kid/judicious", install)
        self.assertIn("npx skills add", install)
        self.assertIn("grok plugin install", install)
        self.assertNotIn("commands/", install)

    def test_store_page_lists_every_skill(self):
        page = json.loads((REPO / "skills.sh.json").read_text())
        listed = {name for group in page["groupings"] for name in group["skills"]}
        present = {p.parent.name for p in SKILLS.glob("*/SKILL.md")}
        self.assertEqual(listed, present)


class SkillTests(unittest.TestCase):
    def skills(self):
        return sorted(SKILLS.glob("*/SKILL.md"))

    def test_frontmatter(self):
        for skill in self.skills():
            with self.subTest(skill=skill.parent.name):
                fields = frontmatter(skill)
                self.assertEqual(fields.get("name"), skill.parent.name)
                self.assertRegex(fields["name"], NAME)
                self.assertTrue(fields.get("description"))
                self.assertLessEqual(len(fields["description"]), MAX_DESCRIPTION)
                self.assertNotRegex(fields.get("allowed-tools", ""), r"\b(Write|Edit)\b")

    def test_router_names_every_skill(self):
        router = (SKILLS / "judicious" / "SKILL.md").read_text()
        for skill in self.skills():
            name = skill.parent.name
            if name == "judicious":
                continue
            self.assertIn(f"| `{name}` | `{name}` |", router)
            self.assertNotIn(f"judicious:{name}", router)

    def test_router_holds_no_command_rules(self):
        router = (SKILLS / "judicious" / "SKILL.md").read_text()
        for label in REUSE_DECISIONS | SEARCH_OUTCOMES:
            self.assertNotIn(f"`{label}`", router)
        self.assertNotIn("Appendix:", router)

    def test_modes_and_next(self):
        for skill in self.skills():
            if skill.parent.name == "judicious":
                continue
            text = skill.read_text(encoding="utf-8")
            with self.subTest(skill=skill.parent.name):
                match = re.search(r"\*\*Mode:\*\* ([a-z-]+)", text)
                self.assertIsNotNone(match)
                self.assertIn(match.group(1), MODES)
                self.assertIn("Next", text)
                self.assertIn("Appendix: Report", text)
                if match.group(1) == "read-only":
                    self.assertIn("read-only", frontmatter(skill)["description"].lower())
                if match.group(1) == "modifying":
                    self.assertIn("edits code", frontmatter(skill)["description"].lower())
                    self.assertIn("Appendix: Verification", text)

    def test_skills_are_self_contained(self):
        for skill in self.skills():
            text = skill.read_text(encoding="utf-8")
            with self.subTest(skill=skill.parent.name):
                self.assertNotRegex(text, r"\]\((?!https?://|#)[^)]+\)")
                self.assertNotIn("CLAUDE_SKILL_DIR", text)
                self.assertNotIn("CLAUDE_PLUGIN_ROOT", text)
                self.assertNotIn("scripts/build.py", text)
                self.assertNotRegex(text, r"/(Users|home)/\w+")

    def test_delegation_uses_installed_names(self):
        self.assertIn("`critique`", body(SKILLS / "audit" / "SKILL.md"))
        init = body(SKILLS / "init" / "SKILL.md")
        self.assertIn("`audit`", init)
        self.assertIn("approval", init.lower())
        self.assertIn("`reuse`", body(SKILLS / "polish" / "SKILL.md"))

    def test_reuse_vocabulary_is_closed(self):
        text = body(SKILLS / "reuse" / "SKILL.md").split("## Appendix:")[0]
        used = set(re.findall(r"`([A-Z][A-Z_]{3,})`", text))
        self.assertLessEqual(used, REUSE_DECISIONS | SEARCH_OUTCOMES)
        self.assertLessEqual(REUSE_DECISIONS, used)
        self.assertIn("Decision:", text)

    def test_critique_has_terminal_line(self):
        self.assertIn("Findings: <n> (high <h>)", (SKILLS / "critique" / "SKILL.md").read_text())


class HookTests(unittest.TestCase):
    def test_inject_stays_small_and_names_reuse(self):
        payload = json.loads((REPO / "hooks" / "session-start.json").read_text())
        context = payload["hookSpecificOutput"]["additionalContext"]
        self.assertLessEqual(len(context.split()), MAX_INJECT_WORDS)
        self.assertIn("`reuse`", context)
        self.assertNotIn("judicious:", context)
        config = json.loads((REPO / "hooks" / "hooks.json").read_text())
        command = config["hooks"]["SessionStart"][0]["hooks"][0]["command"]
        self.assertIn("JUDICIOUS_INJECT", command)
        self.assertIn("session-start.json", command)


if __name__ == "__main__":
    unittest.main()
