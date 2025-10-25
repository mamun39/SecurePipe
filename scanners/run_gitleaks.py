import subprocess, pathlib
out = pathlib.Path("reports/gitleaks.json")
out.parent.mkdir(parents=True, exist_ok=True)
subprocess.run(["gitleaks", "detect", "-f", "json", "-r", str(out)], check=False)
print(f"[gitleaks] wrote {out}")