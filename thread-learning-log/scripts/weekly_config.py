"""Private runtime locations; importing this module does not create files."""
import os
from pathlib import Path
from zoneinfo import ZoneInfo

codex_dir = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).expanduser()
ROOT = Path(os.environ.get("LEARNING_LOG_ROOT", str(codex_dir / "skills/thread-learning-log"))).expanduser().resolve()
REPORT_DIR = Path(os.environ.get("LEARNING_LOG_REPORT_DIR", str(ROOT / "reports"))).expanduser().resolve()
TZ = ZoneInfo(os.environ.get("LEARNING_LOG_TIMEZONE", "UTC"))
PORT = int(os.environ.get("LEARNING_LOG_PORT", "4174"))
if not 1 <= PORT <= 65535:
    raise ValueError("LEARNING_LOG_PORT must be between 1 and 65535")
SITE_DIR = Path(__file__).resolve().parents[1] / "assets/learning-log-site"
