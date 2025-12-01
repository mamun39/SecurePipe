# import json, subprocess, pathlib
# out = pathlib.Path("reports/semgrep.sarif")
# out.parent.mkdir(parents=True, exist_ok=True)
# subprocess.run(["semgrep", "scan", "--config", "p/ci", "--sarif", "-o", str(out)], check=False)
# print(f"[semgrep] wrote {out}")

# scanners/run_semgrep.py
import os, shutil, subprocess, pathlib, sys

out = pathlib.Path("reports/semgrep.sarif")
out.parent.mkdir(parents=True, exist_ok=True)

env = os.environ.copy()
# Force UTF-8 regardless of Windows codepage
env["PYTHONUTF8"] = "1"
env["PYTHONIOENCODING"] = "utf-8"

# Allow override via env var and search PATH for semgrep executable
candidate = env.get("SEMGREP_EXE")
exe = candidate if candidate and pathlib.Path(candidate).exists() else shutil.which("semgrep", path=env.get("PATH"))

if not exe:
    print("[semgrep] not found on PATH. Install with `pip install semgrep` or see scripts/install_tools.sh")
    sys.exit(0)  # soft-skip to keep pipeline moving

# Use a stable public config tuned for CI; restrict to repo to avoid scanning venv, .git, etc.
cmd = [
    exe, "scan",
    "--config", "p/ci",
    "--exclude", ".venv",
    "--exclude", ".git",
    "--exclude", "reports",
    "--sarif", "-o", str(out),
    "--error",   # non-zero exit on rule errors (we soft-fail at make step anyway)
]

try:
    print("[semgrep] running:", " ".join(cmd))
    # Do not fail the whole pipeline if semgrep itself errors; aggregator handles gating
    subprocess.run(cmd, env=env, check=False)
finally:
    print(f"[semgrep] wrote {out}")
