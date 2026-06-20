#!/usr/bin/env bash
# Canon guard: Upstream is ONE procedural platform, no packs. Two checks:
#   1. Dead platform IDENTIFIERS, scanned repo-wide (they never appear in prose).
#   2. The legacy synthetic-data "pack" vocabulary in the reference fixtures + docs.
#      Phase 4 Category B re-derived these to dataset vocabulary (SyntheticDatasetTeaser,
#      specialty, dataset_id). The deprecated cross-repo aliases (list_synthetic_pack_teasers,
#      synthetic_public_pack_teasers) were dropped 2026-06-14 once upstream-data updated its
#      bridge, and are now banned so they cannot return.
# Mirrors upstream-v2's test_customer_has_no_pack_or_specialty_drift and upstream-mcp's
# test/canon.test.ts.
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

SYNTH_PATTERN='SyntheticPackTeaser|pack_family|representative_pack|get_synthetic_pack|list_synthetic_data_packs|compile_synthetic_scenario_dsl|list_synthetic_pack_teasers|synthetic_public_pack_teasers'
synth_hits="$(grep -rInE "$SYNTH_PATTERN" "$ROOT/reference" "$ROOT/README.md" \
  --exclude-dir=.git 2>/dev/null || true)"

if [ -n "$synth_hits" ]; then
  echo "FAIL: legacy synthetic-data pack vocabulary reintroduced:" >&2
  echo "$synth_hits" >&2
  exit 1
fi

# 3. Retired pricing/program framing. Pioneer / Founding 5 / "$49 locked for life"
#    are RETIRED (2026-06-14 v2 de-drift; current tiers = Assist / Pay-as-you-go /
#    Co-pilot / Autopilot). The pioneer-claim issue template survived checks 1-2
#    because they only ban pack IDENTIFIERS, not pricing copy. Scanned on the public
#    surfaces (README, reference docs, .github); .planning history is excluded.
RETIRED_PATTERN='pioneer|founding 5|founding pioneer|locked for life|\$49|\$349'
retired_hits="$(grep -rIniE "$RETIRED_PATTERN" "$ROOT/README.md" "$ROOT/reference" "$ROOT/.github" \
  --exclude="check-canon.sh" 2>/dev/null || true)"

if [ -n "$retired_hits" ]; then
  echo "FAIL: retired Pioneer / pricing framing on a public surface:" >&2
  echo "$retired_hits" >&2
  echo "Current canon: Assist (free) / Pay as you go / Co-pilot / Autopilot. No Pioneer." >&2
  exit 1
fi

echo "canon OK: no legacy pack/specialty identifiers, synthetic pack vocabulary, or retired pricing framing"
