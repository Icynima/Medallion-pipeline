#!/usr/bin/env bash
set -euo pipefail

# Week 1 Day 1: prepare an Ubuntu 24.04 LTS on-prem lab host.
# Review enterprise proxy/firewall and sudo policy before running this script.

if [[ ! -f /etc/os-release ]]; then
  echo "Cannot identify the Linux distribution." >&2
  exit 1
fi

source /etc/os-release
if [[ "${ID:-}" != "ubuntu" || "${VERSION_ID:-}" != "24.04" ]]; then
  echo "Expected Ubuntu 24.04 LTS. Found ${PRETTY_NAME:-unknown}." >&2
  echo "Continue only after your trainer confirms support." >&2
  exit 1
fi

echo "Installing Python, Git, curl and Docker Engine prerequisites..."
sudo apt-get update
sudo apt-get install -y ca-certificates curl git python3 python3-venv python3-pip jq

sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
sudo tee /etc/apt/sources.list.d/docker.sources >/dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: ${UBUNTU_CODENAME:-$VERSION_CODENAME}
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker

COURSE_HOME="${HOME}/medallion-training"
mkdir -p "${COURSE_HOME}"
python3 -m venv "${COURSE_HOME}/.venv"
"${COURSE_HOME}/.venv/bin/python" -m pip install --upgrade pip
"${COURSE_HOME}/.venv/bin/python" -m pip install jupyterlab

echo
echo "Environment prepared at ${COURSE_HOME}."
echo "Docker commands need sudo unless your organization approves docker-group access."
echo "Run verify_environment.sh next."
