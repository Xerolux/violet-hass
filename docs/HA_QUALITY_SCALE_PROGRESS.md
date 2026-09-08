# Home Assistant Quality Scale

This file used to be a 200-line prose summary of a checklist. It claimed
"80%+ coverage", "10 services", "10 workflows" and certification against the
OWASP Top 10 — none of which was true, and none of which anything checked.
A summary of a checklist rots faster than the checklist, so this page now just
points at the checklist.

## Where the real status lives

| Question | Authoritative source |
|---|---|
| Which level is claimed? | `custom_components/violet_pool_controller/manifest.json` → `"quality_scale"` |
| Which rules are met? | `custom_components/violet_pool_controller/quality_scale.yaml` — one entry per rule, with its status |
| What does a rule mean? | [Home Assistant Integration Quality Scale](https://developers.home-assistant.io/docs/core/integration-quality-scale/) |
| What is the coverage floor? | `pyproject.toml` → `[tool.coverage.report] fail_under` |
| Which checks run in CI? | `.github/workflows/validate.yml` |

## Current numbers

Counted from the repository, not from memory. Re-derive them rather than
trusting this table if it looks old:

```bash
# Declared quality scale level
python -c "import json;print(json.load(open('custom_components/violet_pool_controller/manifest.json'))['quality_scale'])"

# Quality scale rules and their statuses
grep -c '^  [a-z-]*:' custom_components/violet_pool_controller/quality_scale.yaml
grep 'status:' custom_components/violet_pool_controller/quality_scale.yaml | sort | uniq -c

# Registered services
grep -c 'hass.services.async_register' custom_components/violet_pool_controller/services.py

# Actual test coverage
pytest tests/ -q --cov=custom_components/violet_pool_controller --cov-report=term
```

## On security claims

The integration is **not** certified against the OWASP Top 10, and no such
certification exists to hold. What it does have is documented in
[SECURITY.md](../SECURITY.md): a passive-first model, input sanitisation in the
API package, rate limiting, the `UNSAFE_SWITCH_KEYS` opt-in, `SafetyGuard` and
`AuthReportingAPI` — each of them backed by tests in
`tests/test_security_principles.py`, `tests/test_safety_guard.py` and
`tests/test_auth_guard.py`.

CI runs CodeQL, TruffleHog and Trivy weekly and on relevant changes
(`.github/workflows/security.yml`). Those are scanners, not certifications.
