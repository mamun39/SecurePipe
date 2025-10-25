import json, subprocess, pathlib
out = pathlib.Path("reports/semgrep.sarif")
out.parent.mkdir(parents=True, exist_ok=True)
subprocess.run(["semgrep", "scan", "--config", "p/ci", "--sarif", "-o", str(out)], check=False)
print(f"[semgrep] wrote {out}")