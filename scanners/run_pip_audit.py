import subprocess, pathlib
out = pathlib.Path("reports/pip-audit.json")
out.parent.mkdir(parents=True, exist_ok=True)
subprocess.run(["pip-audit", "-r", "demo_app/requirements.txt", "-f", "json", "-o", str(out)], check=False)
print(f"[pip-audit] wrote {out}")