package cicd

__doc__ := "Block build if any CRITICAL, or if HIGH > 0 when threshold=high"

deny[msg] {
  some v in input.vulnerabilities
  v.severity == "CRITICAL"
  msg := sprintf("Build blocked: CRITICAL vulnerability: %v", [v.id])
}

deny[msg] {
  input.threshold == "high"
  some v in input.vulnerabilities
  v.severity == "HIGH"
  msg := sprintf("Build blocked: HIGH vulnerability: %v", [v.id])
}