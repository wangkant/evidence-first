"""Check that shipped plugin metadata and skill entrypoints remain installable."""
import json
import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


class RepositoryChecks(unittest.TestCase):
    def test_marketplace_matches_shipped_plugins(self):
        market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        names = [entry["name"] for entry in market["plugins"]]
        self.assertEqual(len(names), len(set(names)), "duplicate plugin registration")
        for entry in market["plugins"]:
            with self.subTest(plugin=entry["name"]):
                plugin = ROOT / entry["source"]
                manifest = json.loads((plugin / ".claude-plugin/plugin.json").read_text())
                self.assertEqual(entry["name"], manifest["name"])
                self.assertEqual(entry["version"], manifest["version"])
                self.assertRegex(manifest["version"], r"^\d+\.\d+\.\d+$")
                self.assertTrue((plugin / manifest["skills"]).is_dir())
                self.assertTrue(list((plugin / manifest["skills"]).glob("*/SKILL.md")))

    def test_skill_frontmatter_and_bundled_resources(self):
        skills = list((ROOT / "plugins").glob("*/skills/*/SKILL.md"))
        self.assertTrue(skills)
        for path in skills:
            with self.subTest(skill=path.parent.name):
                text = path.read_text()
                self.assertTrue(text.startswith("---\n"))
                _, frontmatter, body = text.split("---", 2)
                meta = yaml.safe_load(frontmatter)
                self.assertEqual(meta["name"], path.parent.name)
                self.assertRegex(meta["name"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
                self.assertIsInstance(meta["description"], str)
                self.assertTrue(0 < len(meta["description"]) <= 1024)
                self.assertTrue(body.strip())
                # Check references in backticks or Markdown links, not prose mentions.
                for relative in re.findall(r"(?:`|\()((?:references|scripts)/[\w./-]+)(?:`|\))", body):
                    self.assertTrue((path.parent / relative).is_file(), relative)


if __name__ == "__main__":
    unittest.main()
