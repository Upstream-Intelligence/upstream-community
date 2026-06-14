#!/usr/bin/env bash
# Canon guard: Upstream is ONE procedural platform, no packs. The legacy
# specialty/pack machinery must never reappear in this repo. Mirrors
# upstream-v2's care/tests/test_models.py::test_customer_has_no_pack_or_specialty_drift.
# Scope is the dead IDENTIFIERS only, which never appear in the synthetic-data
# product surface, so this needs no allowlist and cannot false-fail on the
# pending synthetic-data de-pack migration.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PATTERN='VerticalPack|SPECIALTY_PACKS|signup_pack|is_all_packs|specialty_modules|CustomerSpecialtyModule|ProductConfig|outpatient_leaf|specialty_type'

# Exclude .git, node_modules, and this script (which contains the banned list).
hits="$(grep -rInE "$PATTERN" "$ROOT" \
  --exclude-dir=.git \
  --exclude-dir=node_modules \
  --exclude="check-canon.sh" 2>/dev/null || true)"

if [ -n "$hits" ]; then
  echo "FAIL: legacy pack/specialty machinery reintroduced:" >&2
  echo "$hits" >&2
  exit 1
fi

echo "canon OK: no legacy pack/specialty identifiers"
