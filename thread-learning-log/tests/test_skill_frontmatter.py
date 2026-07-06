import unittest
from pathlib import Path


SKILL_PATH = Path(__file__).resolve().parents[1] / "SKILL.md"


class SkillFrontmatterTests(unittest.TestCase):
    def test_skill_frontmatter_is_valid_yaml(self):
        try:
            import yaml
        except ModuleNotFoundError:
            self.skipTest("PyYAML not installed")

        text = SKILL_PATH.read_text(encoding="utf-8")
        _, frontmatter, _ = text.split("---", 2)
        metadata = yaml.safe_load(frontmatter)

        self.assertEqual(metadata["name"], "thread-learning-log")
        self.assertIsInstance(metadata["description"], str)
        self.assertIn("current Codex thread", metadata["description"])
        self.assertIn("learning-log entry", metadata["description"])


if __name__ == "__main__":
    unittest.main()
