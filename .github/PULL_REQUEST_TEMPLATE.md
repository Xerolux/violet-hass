## Pull Request Title

### Description

- **What issue does this solve?** (e.g., Bug fix, feature enhancement, refactoring, documentation update, etc.)  Be specific.  If it fixes a bug, describe the bug. If it adds a feature, describe the feature.
- **Why is this change necessary?**  Explain the motivation behind the changes.  Why is this bug fix important? What benefit does this new feature provide?
- **Additional context or background information:** Include any other relevant details that might help reviewers understand the changes.  This could include links to related discussions, design documents, or external resources.

### Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Code refactor (changes that do not add functionality or fix bugs, but improve the code's structure or readability)
- [ ] Tests (adding or modifying tests)
- [ ] Build/CI (changes to the build system or continuous integration)
- [ ] Chore (maintenance tasks, updating dependencies, etc.)
- [ ] Other (please describe):

### Checklist

- [ ] I have tested my changes locally or in a staging environment.  *Be specific about how you tested.* (e.g., "I tested by manually controlling the pump and verifying that the state updates correctly in Home Assistant.")
- [ ] All automated tests pass. (If applicable.  Run `scripts/lint.sh`)
- [ ] I have added or updated necessary documentation (in the code, `README.md`, and any other relevant documentation).
- [ ] I have reviewed my code for any security vulnerabilities.
- [ ] My changes are backward-compatible (if applicable). If not, clearly explain why and what breaking changes are introduced.
- [ ] I have followed the coding style and conventions of this project. (Run `black .` to format your code)
- [ ] I have added a changelog entry in `docs/CHANGELOG.md` (if applicable).  Use the format: `- Your change description ([#PR number](link to PR))`
- [ ] I have updated the version number in `const.py` and `manifest.json` if this is a new release.

### Related Issue(s)

Fixes # (issue number)  Closes # (issue number)  Related to # (issue number) ### Screenshots (if applicable)

| Before                                       | After                                       |
| -------------------------------------------- | -------------------------------------------- |
| | |

### Testing Instructions

1.  ...
2.  ...
3.  ...

### Notes for Reviewers

*   Are there any parts of the code you'd like specific feedback on?
*   Are there any known limitations or potential issues?
*   Are there any alternative approaches you considered?
