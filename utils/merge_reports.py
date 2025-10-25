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
            data = json.loads(p.read_text())
            merged["sources"][name] = True
            # naive extract of vulns by known fields; refined later
            if name == "trivy":
                for r in data.get("Results", []):
                    for v in r.get("Vulnerabilities", []) or []:
                        merged["vulnerabilities"].append({
                            "tool": "trivy",
                            "id": v.get("VulnerabilityID"),
                            "severity": v.get("Severity", "UNKNOWN")
                        })
        except Exception as e:
            print(f"[yellow]{name}: skip parse error: {e}[/yellow]")

pathlib.Path("reports/merged.json").write_text(json.dumps(merged, indent=2))
print("[green]wrote reports/merged.json[/green]")