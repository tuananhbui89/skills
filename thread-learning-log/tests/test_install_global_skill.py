import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "install_global_skill.py"
)


class InstallGlobalSkillTests(unittest.TestCase):
    def write_config(self, codex_home: Path) -> None:
        config = """
model = "gpt-5.4"

[sandbox_workspace_write]
writable_roots = [
  "/example/workspace",
]
network_access = false
""".lstrip()
        (codex_home / "config.toml").write_text(config, encoding="utf-8")

    def test_install_handles_multiline_writable_roots(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            codex_home = Path(tmp_dir) / ".codex"
            skills_dir = codex_home / "skills"
            codex_home.mkdir(parents=True)
            skills_dir.mkdir(parents=True)
            self.write_config(codex_home)

            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT_PATH),
                    "--codex-home",
                    str(codex_home),
                    "--writable-root",
                    str(skills_dir / "thread-learning-log"),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            installed_skill = skills_dir / "thread-learning-log" / "SKILL.md"
            self.assertTrue(installed_skill.exists())
            expected_writable_root = skills_dir / "thread-learning-log"

            config_text = (codex_home / "config.toml").read_text(encoding="utf-8")
            writable_line = next(
                line for line in config_text.splitlines() if line.startswith("writable_roots =")
            )
            extra_writable_line = next(
                line
                for line in config_text.splitlines()
                if line.startswith("extra_writable_roots =")
            )
            self.assertEqual(writable_line.count(f'"{expected_writable_root}"'), 1)
            self.assertEqual(extra_writable_line.count(f'"{expected_writable_root}"'), 1)

    def test_install_adds_missing_extra_writable_roots_inside_section(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            codex_home = Path(tmp_dir) / ".codex"
            skills_dir = codex_home / "skills"
            codex_home.mkdir(parents=True)
            skills_dir.mkdir(parents=True)
            self.write_config(codex_home)

            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT_PATH),
                    "--codex-home",
                    str(codex_home),
                    "--writable-root",
                    str(skills_dir / "thread-learning-log"),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            config_lines = (codex_home / "config.toml").read_text(encoding="utf-8").splitlines()
            section_start = config_lines.index("[sandbox_workspace_write]")
            section_end = next(
                (index for index in range(section_start + 1, len(config_lines)) if config_lines[index].startswith("[")),
                len(config_lines),
            )
            sandbox_section = "\n".join(config_lines[section_start:section_end])
            self.assertIn("extra_writable_roots =", sandbox_section)


if __name__ == "__main__":
    unittest.main()
