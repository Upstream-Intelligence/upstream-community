---
gsd_state_version: 1.0
milestone: phase-1-canon-anchor
milestone_name: canon-anchor
status: initialized
last_updated: "2026-06-13T22:00:00-05:00"
last_activity: 2026-06-13
progress:
  total_phases: 3
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
  percent: 0
product_readiness:
  status: initialized
  estimated_completion_band: "not started"
  note: "This repo tracks public-methodology alignment."
---

# State

See: `.planning/PROJECT.md` and `../docs/plans/2026-06-12-002-feat-prior-auth-assurance-ecosystem-plan.md`

This repo is not the milestone control plane for this lane. The controlling GSD
phase is `../.planning/phases/02-shared-phase-1-ship-point/`, and this repo
owns the public-methodology slice of Plan `02-03`.

## Status (2026-06-13)

The public-methodology slice of `02-03` is DONE and pushed (commit `64ff675`):
MINIMUM drift fix only -- denial-first headline and the dead engine.upstream.cx
link removed. The public-safe boundary is preserved: NO private runtime vocab
(Workflow Bridge, Case Trace, Criteria Proof) was imported, and the root
`02-VALIDATION` row 02-03-02 now ABSENCE-checks this README for that vocab via
`02-03-drift-gate.sh` (it no longer wrongly demands the vocab be present).

This repo is NON-DEPLOYING. The milestone SHIPPED (PR #27 merged, endpoint live).

## Status (2026-06-13, Phase 4 - No-Packs Framing Convergence)

Category A DONE + pushed (`chore: drop Dental Pack framing + add legacy-identifier
canon guard`): "Dental Pack intelligence engine" -> "dental denial intelligence
engine"; added `scripts/check-canon.sh` + `.github/workflows/canon.yml` (bans the
nine legacy identifiers, proven able to FAIL, enforced by a dedicated workflow
because the org reusable-ci python test step is advisory: `|| true` and needs
`pyproject.toml`, which this repo lacks).

Category B DONE (2026-06-14, unblocked by upstream-data v3.40 + the MCP
re-derivation): `reference/synthetic_data_fixtures.py` de-packed -- `SyntheticPackTeaser`
-> `SyntheticDatasetTeaser`, `pack_family` -> `specialty`, `representative_pack` ->
`dataset_id`, catalog-reference keys -> `dataset_count`/`dataset_ids`. Deprecated
cross-repo shims `list_synthetic_pack_teasers` / `synthetic_public_pack_teasers` kept
(upstream-data audits referenced the old names) -- FLAGGED for the concurrent
session to update its audit, then drop at v4.0. methodology-doc + README pack
vocabulary -> dataset/specialty. `check-canon.sh` extended to ban the synthetic pack
vocabulary (SyntheticPackTeaser/pack_family/representative_pack/...), proven able to
FAIL; aliases intentionally excluded. Python executes, asserts public-safe. See
`../.planning/phases/04-no-packs-framing-convergence/04-B-PLAN-synthetic-data-redrive.md`.
