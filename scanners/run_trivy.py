import subprocess, pathlib
out = pathlib.Path("reports/trivy.json")
out.parent.mkdir(parents=True, exist_ok=True)
# Repo scan (FS). For image scans, change to: ["trivy","image","--format","json","-o",str(out),"image:tag"]
subprocess.run(["trivy","fs","--quiet","--format","json","-o",str(out),"."], check=False)
print(f"[trivy] wrote {out}")