#!/usr/bin/env bash
set -euo pipefail

REPORT_DIR="${1:-./out}"
mkdir -p "${REPORT_DIR}"
REPORT="${REPORT_DIR}/environment_report.txt"

{
  echo "Week 1 Day 1 - Ubuntu On-Prem Readiness Report"
  echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  echo "[Operating system]"
  if [[ -f /etc/os-release ]]; then
    grep -E '^(PRETTY_NAME|VERSION_ID)=' /etc/os-release
  else
    echo "Missing /etc/os-release"
  fi
  echo
  echo "[Resources]"
  nproc --all | awk '{print "CPU cores: " $1}'
  free -h | awk '/^Mem:/ {print "Memory: " $2}'
  df -h . | awk 'NR==2 {print "Free disk on workspace filesystem: " $4}'
  echo
  echo "[Commands]"
  for command in python3 git curl docker; do
    if command -v "${command}" >/dev/null 2>&1; then
      echo "PASS ${command}: $(${command} --version 2>&1 | head -n 1)"
    else
      echo "FAIL ${command}: not installed"
    fi
  done
  if docker compose version >/dev/null 2>&1; then
    echo "PASS docker compose: $(docker compose version)"
  else
    echo "FAIL docker compose: plugin unavailable or Docker permission denied"
  fi
  echo
  echo "[Course port reservation check - Day 2 onward]"
  for port in 8080 8083 8088 9000 9092; do
    if ss -ltn 2>/dev/null | awk '{print $4}' | grep -Eq ":${port}$"; then
      echo "WARN TCP ${port} already in use"
    else
      echo "PASS TCP ${port} available"
    fi
  done
} | tee "${REPORT}"

echo
echo "Submit ${REPORT} as Lab 0 evidence."
