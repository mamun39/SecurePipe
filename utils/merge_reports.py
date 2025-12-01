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


def add_vuln(tool, vuln_id, severity):
    """Append a normalized vulnerability entry."""
    merged["vulnerabilities"].append({
        "tool": tool,
        "id": vuln_id or "UNKNOWN",
        "severity": (severity or "UNKNOWN").upper(),
    })


def parse_semgrep(data):
    merged["sources"]["semgrep"] = True
    sev_map = {"error": "HIGH", "warning": "MEDIUM", "note": "LOW", "info": "LOW"}
    for run in data.get("runs", []):
        for res in run.get("results", []) or []:
            rule_id = res.get("ruleId") or res.get("rule", {}).get("id")
            level = (res.get("level") or res.get("kind") or "").lower()
            rule_sev = (res.get("properties", {}).get("severity") or "").lower()
            severity = sev_map.get(rule_sev, sev_map.get(level, "MEDIUM"))
            add_vuln("semgrep", rule_id, severity)


def parse_gitleaks(raw_text):
    merged["sources"]["gitleaks"] = True
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        # gitleaks can emit JSONL; fall back to line-by-line parsing
        entries = []
        for line in raw_text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        data = entries

    if isinstance(data, dict) and "findings" in data:
        findings = data.get("findings", [])
    elif isinstance(data, list):
        findings = data
    else:
        findings = []

    for f in findings:
        rid = f.get("RuleID") or f.get("Description")
        sev = f.get("Severity") or "HIGH"  # default high for secrets
        add_vuln("gitleaks", rid, sev)


def parse_trivy(data):
    merged["sources"]["trivy"] = True
    for r in data.get("Results", []):
        for v in r.get("Vulnerabilities", []) or []:
            add_vuln("trivy", v.get("VulnerabilityID"), v.get("Severity"))


def parse_pip_audit(data):
    merged["sources"]["pip_audit"] = True
    for dep in data.get("dependencies", []):
        for v in dep.get("vulns", []) or []:
            vid = v.get("id") or f"{dep.get('name')}@{dep.get('version')}"
            sev = v.get("severity") or "HIGH"  # conservative default
            add_vuln("pip-audit", vid, sev)


def parse_sbom(data):
    # No vulnerabilities extracted yet; we only mark presence for metadata
    merged["sources"]["sbom"] = True


parsers = {
    "semgrep": lambda text: parse_semgrep(json.loads(text)),
    "gitleaks": parse_gitleaks,
    "trivy": lambda text: parse_trivy(json.loads(text)),
    "pip_audit": lambda text: parse_pip_audit(json.loads(text)),
    "sbom": lambda text: parse_sbom(json.loads(text)),
}


for name, path in reports.items():
    p = pathlib.Path(path)
    if not p.exists():
        continue
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
        parser = parsers.get(name)
        if parser:
            parser(text)
    except Exception as e:
        print(f"[yellow]{name}: skip parse error: {e}[/yellow]")

out = pathlib.Path("reports/merged.json")
out.write_text(json.dumps(merged, indent=2), encoding="utf-8")
print("[green]wrote reports/merged.json[/green]")
