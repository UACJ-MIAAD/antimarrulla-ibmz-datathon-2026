#!/usr/bin/env bash
# 01_system_check.sh - Checks the OS, CPU architecture and base tools.
set -u
ok()   { echo -e "  \e[32m[OK]\e[0m   $*"; }
warn() { echo -e "  \e[33m[WARN]\e[0m $*"; }
fail() { echo -e "  \e[31m[FAIL]\e[0m $*"; FAILED=1; }
FAILED=0

echo "== System check =="
. /etc/os-release
[[ "$ID" == "ubuntu" && "$VERSION_ID" == "24.04" ]] && ok "OS: $PRETTY_NAME" || warn "OS is $PRETTY_NAME (expected Ubuntu 24.04)"

ARCH=$(uname -m)
[[ "$ARCH" == "s390x" ]] && ok "Architecture: s390x (provider requires dashboard verification)" || warn "Architecture is $ARCH, not s390x"

command -v python3 >/dev/null && ok "Python: $(python3 --version 2>&1)" || fail "python3 not found"

if command -v openssl >/dev/null; then
  ok "OpenSSL: $(openssl version)"
  openssl ciphers -s -tls1_3 2>/dev/null | grep -q TLS_AES_256_GCM_SHA384 \
    && ok "OpenSSL supports TLS 1.3 with AES-256-GCM" || fail "TLS 1.3 / AES-256-GCM not available in OpenSSL"
else
  fail "openssl not found"
fi

ok "CPUs: $(nproc), RAM: $(free -h | awk '/Mem:/{print $2}'), free disk on /: $(df -h / | awk 'NR==2{print $4}')"

if curl -sS --max-time 5 -o /dev/null https://pypi.org; then ok "Internet access to PyPI"; else warn "Cannot reach pypi.org (pip installs will fail)"; fi

exit $FAILED
