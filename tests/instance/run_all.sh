#!/usr/bin/env bash
# run_all.sh - Runs every check in order and saves a log.
set -euo pipefail
cd "$(dirname "$0")"
LOG="stack-check-$(date +%Y%m%d-%H%M%S).log"
VENV="${VENV:-$HOME/venv-datathon}"
{
  bash ./01_system_check.sh
  bash ./02_install_stack.sh
  echo; "$VENV/bin/python" 03_test_stack.py
  echo; bash ./04_docker_check.sh
  echo; "$VENV/bin/python" 05_test_claims.py
} 2>&1 | tee "$LOG"
echo "Log saved to $LOG"
