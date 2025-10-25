# utils/aggregate_score.py
import json, pathlib, sys
from collections import Counter

threshold = "high"
if "--fail-threshold" in sys.argv:
    threshold = sys.argv[sys.argv.index("--fail-threshold")+1].lower()

# 🔧 read merged.json as UTF-8
merged_path = pathlib.Path("reports/merged.json")
data = json.loads(merged_path.read_text(encoding="utf-8"))

sev_weight = {"CRITICAL":5,"HIGH":4,"MEDIUM":3,"LOW":1}
counts = Counter(v.get("severity","UNKNOWN") for v in data.get("vulnerabilities",[]))

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
sys.exit(1 if fail else 0)
