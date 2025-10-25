# import json, subprocess, pathlib
# out = pathlib.Path("reports/semgrep.sarif")
# out.parent.mkdir(parents=True, exist_ok=True)
# subprocess.run(["semgrep", "scan", "--config", "p/ci", "--sarif", "-o", str(out)], check=False)
# print(f"[semgrep] wrote {out}")

# scanners/run_semgrep.py
import os, subprocess, pathlib, sys

out = pathlib.Path("reports/semgrep.sarif")
out.parent.mkdir(parents=True, exist_ok=True)

env = os.environ.copy()
# Force UTF-8 regardless of Windows codepage
env["PYTHONUTF8"] = "1"
env["PYTHONIOENCODING"] = "utf-8"

# Use a stable public config tuned for CI; restrict to repo to avoid scanning venv, .git, etc.
cmd = [
    "semgrep", "scan",
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
