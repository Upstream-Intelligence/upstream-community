# Contributing to upstream-community

Thanks for contributing. This repo is the open-source reference layer for Upstream's Revenue Intelligence methodology — not a general RCM utilities library. Before contributing, read the scope below so your time isn't wasted.

---

## Scope

**In scope:**
- Additional CARC/RARC codes in `carc_rarc_utils.py`
- Improved feature engineering in `denial_prediction_reference.py` or `denial_clustering.py`
- New notebooks demonstrating existing reference implementations on public CMS data
- Bug fixes (wrong CARC descriptions, broken examples, etc.)
- Documentation improvements

**Out of scope:**
- Production Upstream model weights or internal features
- Proprietary payer data or payer-specific rule tables
- General RCM tooling unrelated to the existing modules
- Integrations with EHR/PM vendors (use the [Upstream API](https://upstream.cx/developers) for that)
- Any PHI or patient data — even synthetic PHI

---

## Payer Rule Contributions

The most valuable contributions are corrections to CARC/RARC code descriptions.

CMS updates the CARC/RARC code set periodically. If you find a code that is:
- Missing from `carc_rarc_utils.py`
- Has an outdated description
- Has an incorrect or incomplete corrective action

Please open a PR with the source. Acceptable sources:
- [CMS CARC code list](https://x12.org/codes/claim-adjustment-reason-codes)
- [Washington Publishing Company RARC list](https://x12.org/codes/remittance-advice-remark-codes)
- Official payer LCD/NCD documentation

Include the source URL in your PR description.

---

## CARC Code PR Format

When adding or updating CARC codes, follow this structure in `carc_rarc_utils.py`:

```python
CARCInfo(
    code="97",
    description="The benefit for this service is included in the payment/allowance "
                "for another service/procedure that has already been adjudicated.",
    category="bundled",
    corrective_action=(
        "Review NCCI edits for the code pair. Add modifier -59 or -X{EPSU} "
        "if the services were clinically distinct and separate. Document medical "
        "necessity for each service independently."
    ),
    regulatory_basis="CMS NCCI Policy Manual Chapter 3",
    source_url="https://www.cms.gov/medicare/coding-billing/national-correct-coding-initiative-ncci",
)
```

Required fields: `code`, `description`, `category`, `corrective_action`.  
Optional but preferred: `regulatory_basis`, `source_url`.

---

## Notebooks

Notebooks must:
1. Run end-to-end using only public data (CMS SynPUF or `sample_claims_schema.py` synthetic data)
2. Use an existing `reference/` module — notebooks are walkthroughs, not new implementations
3. Be committed with outputs cleared (`Kernel > Restart & Clear Output` before committing)
4. Have a markdown introduction explaining what the notebook teaches and why it matters

Notebooks go in `notebooks/` with the naming convention `NN_topic_name.ipynb` (e.g., `03_drift_detection_tutorial.ipynb`).

---

## Code Standards

- **Python 3.10+** — use `match`, `|` union types, `f-strings`
- **Type annotations** — all public functions must have full type annotations
- **Docstrings** — Google style, required on all public functions and classes
- **No external dependencies** not already in `requirements.txt` — open a discussion first
- **No hardcoded payer data** — all payer-specific values must come from public sources with a citation

---

## PR Process

1. Fork and create a branch: `feature/carc-additions`, `fix/carc-97-description`, `notebook/clustering-walkthrough`
2. Make your changes with tests if applicable
3. Run `python -m pytest tests/` to confirm nothing breaks
4. Open a PR against `main` with a description that includes:
   - What you changed and why
   - The public source for any new data you added
   - How to verify the change (what to run)

PRs without a clear public source for new CARC/RARC data will not be merged.

---

## Questions

Open an issue before starting large work. For questions about the Upstream API or production behavior, use the [developer docs](https://upstream.cx/developers) or join the [Discord](https://upstream.cx/community).
