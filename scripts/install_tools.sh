#!/usr/bin/env bash
set -euo pipefail
# Install CLI tools (Linux/macOS)
curl -sSfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Gitleaks install (try multiple strategies to avoid 404s)
install_gitleaks() {
  # 1) Homebrew on macOS (fastest, least brittle)
  if command -v brew >/dev/null 2>&1; then
    if brew list gitleaks >/dev/null 2>&1 || brew install gitleaks; then
      echo "gitleaks installed via brew"
      return 0
    fi
  fi

  # 2) Official install scripts (branch/path may vary)
  local gitleaks_urls=(
    "https://raw.githubusercontent.com/gitleaks/gitleaks/main/install.sh"
    "https://raw.githubusercontent.com/gitleaks/gitleaks/master/install.sh"
    "https://raw.githubusercontent.com/gitleaks/gitleaks/main/scripts/install.sh"
    "https://raw.githubusercontent.com/gitleaks/gitleaks/master/scripts/install.sh"
  )
  for url in "${gitleaks_urls[@]}"; do
    if curl -sSfL "$url" | bash; then
      echo "gitleaks installed via $url"
      return 0
    fi
  done

  # 3) Direct release tarball as a final fallback
  local version="${GITLEAKS_VERSION:-8.18.1}"
  local os arch
  os=$(uname -s | tr '[:upper:]' '[:lower:]')
  arch=$(uname -m)
  case "$arch" in
    x86_64) arch="x64" ;;
    arm64|aarch64) arch="arm64" ;;
  esac
  local tarball="gitleaks_${version}_${os}_${arch}.tar.gz"
  local url="https://github.com/gitleaks/gitleaks/releases/download/v${version}/${tarball}"
  if curl -sSfL "$url" -o "/tmp/${tarball}"; then
    tar -xzf "/tmp/${tarball}" -C /tmp
    install -m 0755 "/tmp/gitleaks" /usr/local/bin/gitleaks
    echo "gitleaks installed via ${url}"
    return 0
  fi

  echo "gitleaks installation failed; please install manually (brew install gitleaks)" >&2
  return 1
}

install_gitleaks || true

# Conftest (OPA) for policy enforcement
install_conftest() {
  if command -v conftest >/dev/null 2>&1; then
    echo "conftest already installed"
    return 0
  fi

  if command -v brew >/dev/null 2>&1; then
    if brew list conftest >/dev/null 2>&1 || brew install conftest; then
      echo "conftest installed via brew"
      return 0
    fi
  fi

  local version="${CONFTEST_VERSION:-0.56.0}"
  local os arch
  os="$(uname -s)"
  arch="$(uname -m)"
  case "$arch" in
    x86_64) arch="x86_64" ;;
    arm64|aarch64) arch="arm64" ;;
  esac
  local tarball="conftest_${version}_${os}_${arch}.tar.gz"
  local url="https://github.com/open-policy-agent/conftest/releases/download/v${version}/${tarball}"
  if curl -sSfL "$url" -o "/tmp/${tarball}"; then
    tar -xzf "/tmp/${tarball}" -C /tmp conftest
    install -m 0755 "/tmp/conftest" /usr/local/bin/conftest
    echo "conftest installed via ${url}"
    return 0
  fi

  echo "conftest installation failed; please install manually (brew install conftest)" >&2
  return 1
}

install_conftest || true

curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
pip install pip-audit semgrep
