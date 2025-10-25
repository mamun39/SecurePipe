# SecurePipe

Security automation for CI/CD: SAST, SCA, secrets, container scans, SBOM, and policy gates.

## Quickstart (local)
```bash
make setup
bash scripts/install_tools.sh   # one-time on Linux/macOS
make scan-all                   # runs all scanners, merges & scores
