import subprocess, pathlib
out = pathlib.Path("reports/sbom-spdx.json")
out.parent.mkdir(parents=True, exist_ok=True)
subprocess.run(["syft","dir:.","-o","spdx-json="+str(out)], check=False)
print(f"[syft] wrote {out}")