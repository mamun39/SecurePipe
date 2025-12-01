# utils/aggregate_score.py
import json, pathlib, sys, tempfile, subprocess, shutil
from collections import Counter

threshold = "high"
if "--fail-threshold" in sys.argv:
    threshold = sys.argv[sys.argv.index("--fail-threshold")+1].lower()

# 🔧 read merged.json as UTF-8
merged_path = pathlib.Path("reports/merged.json")
data = json.loads(merged_path.read_text(encoding="utf-8"))

sev_weight = {"CRITICAL":5,"HIGH":4,"MEDIUM":3,"LOW":1}
counts = Counter((v.get("severity","UNKNOWN") or "UNKNOWN").upper() for v in data.get("vulnerabilities",[]))

md = pathlib.Path("reports/security-summary.md")
# 🔧 write markdown as UTF-8 (the lock emoji will now work)
md.write_text(
f"""# 🔐 Security Summary

| Severity  | Count |
|-----------|------:|
| CRITICAL  | {counts.get('CRITICAL',0)} |
| HIGH      | {counts.get('HIGH',0)} |
| MEDIUM    | {counts.get('MEDIUM',0)} |
| LOW       | {counts.get('LOW',0)} |
| UNKNOWN   | {counts.get('UNKNOWN',0)} |

**Threshold:** {threshold.upper()}
""",
encoding="utf-8",
)
print("wrote reports/security-summary.md")

fail = counts.get("CRITICAL",0) > 0 or (threshold=="high" and counts.get("HIGH",0)>0)

# Optional policy enforcement via Conftest/OPA if available
conftest = shutil.which("conftest")
policy_dir = pathlib.Path("policies")
if conftest and policy_dir.exists():
    policy_input = {
        "threshold": threshold,
        "vulnerabilities": data.get("vulnerabilities", []),
    }
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tmp:
        json.dump(policy_input, tmp)
        tmp_path = tmp.name
    try:
        result = subprocess.run(
            [conftest, "test", tmp_path, "--policy", str(policy_dir)],
            text=True,
        )
        if result.returncode != 0:
            fail = True
            print("conftest policy violations detected")
    finally:
        pathlib.Path(tmp_path).unlink(missing_ok=True)
else:
    print("conftest not installed or policies/ missing; skipping policy enforcement")

sys.exit(1 if fail else 0)
