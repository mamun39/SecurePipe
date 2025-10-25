# scanners/run_gitleaks.py
import os, shutil, subprocess, pathlib, sys

out = pathlib.Path("reports/gitleaks.json")
out.parent.mkdir(parents=True, exist_ok=True)

env = os.environ.copy()
user_bin = pathlib.Path.home() / ".local" / "bin"
env["PATH"] = str(user_bin) + os.pathsep + env.get("PATH", "")

# Prefer explicit path via env var
candidate = env.get("GITLEAKS_EXE")

def find_exe():
    if candidate and pathlib.Path(candidate).exists():
        return candidate
    # common names on Windows/Linux
    for name in ("gitleaks", "gitleaks.exe"):
        path = shutil.which(name, path=env["PATH"])
        if path:
            return path
    # Search typical Windows install dirs
    for base in (os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)"),
                 os.path.join(os.environ.get("LOCALAPPDATA",""), "Programs")):
        if not base: 
            continue
        for sub in ("", "Gitleaks",):
            p = pathlib.Path(base) / sub / "gitleaks.exe"
            if p.exists():
                return str(p)
    return None

exe = find_exe()
if not exe:
    print("[gitleaks] not found on PATH. Install via winget: winget install Gitleaks.Gitleaks")
    sys.exit(0)  # soft-skip; pipeline continues

cmd = [exe, "detect", "-f", "json", "-r", str(out)]
print("[gitleaks] running:", " ".join(cmd))
subprocess.run(cmd, env=env, check=False)
print(f"[gitleaks] wrote {out}")
