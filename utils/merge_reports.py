# utils/merge_reports.py
import json, pathlib
from rich import print

reports = {
    "semgrep": "reports/semgrep.sarif",
    "gitleaks": "reports/gitleaks.json",
    "trivy": "reports/trivy.json",
    "pip_audit": "reports/pip-audit.json",
    "sbom": "reports/sbom-spdx.json",
}

merged = {"sources": {}, "vulnerabilities": []}

for name, path in reports.items():
    p = pathlib.Path(path)
    if p.exists():
        try:
            # 🔧 read as UTF-8; tolerate odd bytes
            text = p.read_text(encoding="utf-8", errors="replace")
            data = json.loads(text)
            merged["sources"][name] = True

            if name == "trivy":
                for r in data.get("Results", []):
                    for v in r.get("Vulnerabilities", []) or []:
                        merged["vulnerabilities"].append({
                            "tool": "trivy",
                            "id": v.get("VulnerabilityID"),
                            "severity": v.get("Severity", "UNKNOWN"),
                        })
        except Exception as e:
            print(f"[yellow]{name}: skip parse error: {e}[/yellow]")

out = pathlib.Path("reports/merged.json")
out.write_text(json.dumps(merged, indent=2), encoding="utf-8")
print("[green]wrote reports/merged.json[/green]")
