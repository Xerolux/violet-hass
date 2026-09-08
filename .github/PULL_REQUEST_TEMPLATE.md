## Description

- **What does this change?** Be specific. If it fixes a bug, describe the bug. If it adds a feature, describe the feature.
- **Why is it needed?** What breaks without it, or what becomes possible with it?
- **Anything a reviewer should know?** Links to discussions, controller firmware quirks, related pull requests.

> The title of this pull request becomes a line in the release notes, so write
> it as a [Conventional Commit](https://www.conventionalcommits.org/), e.g.
> `fix(switch): stop DMX scenes fighting the light platform`.

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that changes existing behaviour)
- [ ] Documentation
- [ ] Refactor (no behaviour change)
- [ ] Tests
- [ ] Build/CI
- [ ] Chore (maintenance, dependencies)

## Checklist

- [ ] I tested this. *Say how* — e.g. "controlled the pump from the UI and confirmed the state updates after the next poll".
- [ ] Lint is clean: `ruff check custom_components/violet_pool_controller tests`
- [ ] Types are clean: `mypy custom_components/violet_pool_controller`
- [ ] Tests pass: `pytest tests/ -q`
- [ ] Tests added or updated for the behaviour I changed
- [ ] Documentation updated (code docstrings, `README.md`, `docs/wiki/` — and the `.de.md` twin if I touched an English wiki page)
- [ ] Everything I wrote is in English (see the Language Policy in `CLAUDE.md`)
- [ ] No new security assumptions: nothing restores device state, nothing acts without an explicit user command (see `SECURITY.md`)
- [ ] Changelog entry added to `CHANGELOG.md` under a `## Version X.Y.Z (YYYY-MM-DD)` heading

### Release checklist (maintainer only)

A version bump must move **all five** version sources plus the changelog, or
CI's "Version consistency" job fails:

- [ ] `custom_components/violet_pool_controller/manifest.json`
- [ ] `custom_components/violet_pool_controller/const.py` (`INTEGRATION_VERSION`)
- [ ] `custom_components/violet_pool_controller/.version`
- [ ] `pyproject.toml`
- [ ] `CLAUDE.md` ("Current Integration Version")
- [ ] `CHANGELOG.md` section for the new version — it becomes the release page

## Related Issue(s)

Fixes #

## Screenshots

Delete this section if the change is not visible in the UI.

| Before | After |
| ------ | ----- |
|        |       |

## Testing Instructions

1.
2.
3.

## Notes for Reviewers

- Anything you would like specific feedback on?
- Known limitations or follow-ups?
- Alternatives you considered and rejected?
