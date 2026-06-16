# CI/CD Action Pinning Recommendations

**Issue**: Multiple GitHub Actions use @main/@master branches, which are unstable  
**Risk**: Actions can change behavior unexpectedly, breaking CI pipelines  
**Solution**: Pin to stable release tags

## Current Unstable References

### security.yml
- ❌ `trufflesecurity/trufflehog@main` → Pin to latest release (e.g., `v3.75.0`)
- ❌ `aquasecurity/trivy-action@master` → Pin to latest release (e.g., `v0.20.0`)

### validate.yml
- ❌ `home-assistant/actions/hassfest@master` → Pin to latest release
- ❌ `hacs/action@main` → Pin to latest release

## Recommended Actions

1. **Check Latest Releases**
   - Visit GitHub releases for each action
   - Note current stable version

2. **Update Workflow Files**
   ```yaml
   # Before
   uses: trufflesecurity/trufflehog@main
   
   # After
   uses: trufflesecurity/trufflehog@v3.75.0
   ```

3. **Verify Compatibility**
   - Test CI runs with pinned versions
   - Ensure no breaking changes

4. **Create Dependabot PRs** (optional)
   - Enable Dependabot for Actions
   - Auto-update to new releases

## Implementation Priority

1. **High**: trufflesecurity/trufflehog (security scanning)
2. **High**: home-assistant/actions/hassfest (validation)
3. **Medium**: hacs/action (HACS validation)
4. **Medium**: aquasecurity/trivy-action (vulnerability scanning)

## Notes

- Pinning to major version (e.g., `v3`) is acceptable compromise
- Use release tags, NOT branches
- Review changelog before updating
- Run CI tests locally when possible
