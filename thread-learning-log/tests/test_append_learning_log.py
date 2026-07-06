import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "append_learning_log.py"
)
GLOBAL_SKILL_DIR = Path.home() / ".codex" / "skills" / "thread-learning-log"
LOG_PATH = str(GLOBAL_SKILL_DIR / "learning-log.md")
SKILL_PATH = str(GLOBAL_SKILL_DIR / "SKILL.md")
APPEND_SCRIPT_PATH = str(GLOBAL_SKILL_DIR / "scripts" / "append_learning_log.py")


class AppendLearningLogCliTests(unittest.TestCase):
    def base_payload(self):
        return {
            "entry_id": "20260325-1000-agentmemory-test-entry",
            "date": "2026-03-25",
            "time_start": "10:00",
            "time_end": "10:00",
            "time_basis": "logged_at",
            "category": "learning",
            "primary_tag": "@AgentMemory",
            "tags": ["@AgentMemory"],
            "context_status": "full",
            "source": "codex-thread",
            "source_locations": [
                LOG_PATH,
                SKILL_PATH,
            ],
            "reference_locations": [
                "https://example.com/blog-post",
                APPEND_SCRIPT_PATH,
            ],
            "title": "Test Entry",
            "sections": {
                "Summary": "Short summary.",
                "What I Did": "- Captured notes.",
                "What I Learned": "- Learned one thing.",
                "Decisions": "",
                "Open Questions": "",
                "Next Steps": "- Keep going.",
            },
        }

    def run_cli(self, *args, input_path):
        return subprocess.run(
            ["python3", str(SCRIPT_PATH), *args, "--input", str(input_path)],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_render_outputs_structured_entry(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            payload_path = Path(tmp_dir) / "payload.json"
            payload_path.write_text(
                json.dumps(self.base_payload(), indent=2), encoding="utf-8"
            )

            result = self.run_cli("--render", input_path=payload_path)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(
                "## 2026-03-25 10:00 | @AgentMemory | Test Entry", result.stdout
            )
            self.assertIn('tags: ["@AgentMemory"]', result.stdout)
            self.assertIn(
                f'source_locations: ["{LOG_PATH}", "{SKILL_PATH}"]',
                result.stdout,
            )
            self.assertIn(
                f'reference_locations: ["https://example.com/blog-post", "{APPEND_SCRIPT_PATH}"]',
                result.stdout,
            )
            self.assertIn("### Decisions\n- None.", result.stdout)

    def test_append_creates_root_heading_and_entry(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            payload_path = Path(tmp_dir) / "payload.json"
            log_path = Path(tmp_dir) / "learning-log.md"
            payload_path.write_text(
                json.dumps(self.base_payload(), indent=2), encoding="utf-8"
            )

            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT_PATH),
                    "--append",
                    "--input",
                    str(payload_path),
                    "--log-path",
                    str(log_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            content = log_path.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("# Learning Log\n\n"))
            self.assertIn("entry_id: \"20260325-1000-agentmemory-test-entry\"", content)
            self.assertIn(
                f'source_locations: ["{LOG_PATH}", "{SKILL_PATH}"]',
                content,
            )
            self.assertIn("### Next Steps\n- Keep going.", content)

    def test_invalid_category_returns_error(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            payload = self.base_payload()
            payload["category"] = "invalid-category"
            payload_path = Path(tmp_dir) / "payload.json"
            payload_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

            result = self.run_cli("--render", input_path=payload_path)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("category must be one of", result.stderr)

    def test_missing_locations_default_to_empty_lists(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            payload = self.base_payload()
            payload.pop("source_locations")
            payload.pop("reference_locations")
            payload_path = Path(tmp_dir) / "payload.json"
            payload_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

            result = self.run_cli("--render", input_path=payload_path)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("source_locations: []", result.stdout)
            self.assertIn("reference_locations: []", result.stdout)

    def test_legacy_path_aliases_are_normalized(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            payload = self.base_payload()
            payload.pop("source_locations")
            payload.pop("reference_locations")
            payload["source_paths"] = [
                LOG_PATH,
                LOG_PATH,
            ]
            payload["reference_paths"] = "https://example.com/alias"
            payload_path = Path(tmp_dir) / "payload.json"
            payload_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

            result = self.run_cli("--render", input_path=payload_path)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(
                f'source_locations: ["{LOG_PATH}"]',
                result.stdout,
            )
            self.assertIn(
                'reference_locations: ["https://example.com/alias"]',
                result.stdout,
            )


if __name__ == "__main__":
    unittest.main()
