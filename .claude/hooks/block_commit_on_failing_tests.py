"""PreToolUse hook: block `git commit` commands while the pytest suite is failing."""
import json
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GIT_COMMIT_PATTERN = re.compile(r"\bgit\s+(?:-\S+\s+)*commit\b")


def get_python_executable():
    venv_python = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        venv_python = PROJECT_ROOT / ".venv" / "bin" / "python"
    return str(venv_python) if venv_python.exists() else sys.executable


def main():
    payload = json.load(sys.stdin)
    command = payload.get("tool_input", {}).get("command", "")
    if not GIT_COMMIT_PATTERN.search(command):
        return 0

    result = subprocess.run(
        [get_python_executable(), "-m", "pytest", "-q", "--tb=short"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return 0

    print("git commit blocked: the python tests are failing.", file=sys.stderr)
    print((result.stdout + result.stderr)[-3000:], file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
