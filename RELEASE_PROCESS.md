# Release Process

This document describes the structured release process for Wareflow Employee Management System.

## Overview

The release process is designed to be:
- **Consistent**: Every release follows the same steps
- **Automated**: Build and release notes are generated automatically
- **Safe**: Tests run before builds, checksums verify integrity
- **Communicated**: Users receive clear release notes and upgrade instructions

## Release Types

### Major Releases (X.0.0)
**When**: Major new features, breaking changes, API changes

**Characteristics**:
- Breaking changes allowed
- Migration required
- Extensive testing
- Long support cycle for previous version (6 months)

**Examples**:
- Configuration format changes (JSON → YAML)
- Database schema changes
- Removed features

**Process**:
1. Create release branch: `release/v2.0.0`
2. Complete all planned features
3. Update migration scripts
4. Test migration from previous version
5. Beta testing (2 weeks)
6. Release candidate (1 week)
7. Stable release

### Minor Releases (0.X.0)
**When**: New features, backward compatible

**Characteristics**:
- No breaking changes
- New functionality added
- Standard testing
- No migration required

**Process**:
1. Develop on main branch
2. Test all new features
3. Update documentation
4. Tag and release

### Patch Releases (0.0.X)
**When**: Bug fixes only

**Characteristics**:
- No new features
- Critical bug fixes
- Security fixes
- Quick turnaround

**Process**:
1. Fix on main branch
2. Quick smoke test
3. Tag and release

## Pre-Release Checklist

Before creating a release, ensure:

### Quality Checks
- [ ] All tests pass (`pytest` with ≥70% coverage)
- [ ] No critical bugs open
- [ ] No security vulnerabilities
- [ ] Performance acceptable
- [ ] Code review completed

### Documentation
- [ ] Release notes written (or generated)
- [ ] Breaking changes documented
- [ ] Migration guide created (if breaking changes)
- [ ] API documentation updated (if API changes)
- [ ] User guide updated (if UI changes)

### Build Verification
- [ ] Build script works locally: `python build/build.py`
- [ ] Executable runs without errors
- [ ] Checksums generated correctly
- [ ] All artifacts created

### Migration
- [ ] Migration script tested (if needed)
- [ ] Rollback tested (if breaking changes)
- [ ] Backup/restore tested

## Release Process (Automated)

### Method 1: Tag-Based Release (Recommended)

**For automated release with GitHub Actions**:

```bash
# 1. Ensure main is up to date
git checkout main
git pull origin main

# 2. Create and push tag
git tag v1.2.3
git push origin v1.2.3

# That's it! GitHub Actions will:
# - Run tests
# - Build executables
# - Generate checksums
# - Generate release notes
# - Create GitHub release
# - Update CHANGELOG.md
```

### Method 2: Manual Workflow Dispatch

**For on-demand builds without tags**:

1. Go to GitHub Actions tab
2. Select "Build and Release" workflow
3. Click "Run workflow"
4. Enter version (e.g., v1.2.3)
5. Enable "Create GitHub release" if desired
6. Click "Run workflow"

### Method 3: Local Build

**For testing or custom builds**:

```bash
# Standard build
python build/build.py

# Clean build
python build/build.py --clean

# Custom version
python build/build.py --version v1.2.3

# Skip tests
python build/build.py --skip-tests
```

## Post-Release Tasks

### Immediate (After Release)

1. **Verify release on GitHub**
   - Check release notes are correct
   - Download and test executables
   - Verify checksums

2. **Update documentation links**
   - Update download links in README
   - Update version references in docs

3. **Announcements**
   - Post announcement in GitHub Discussions
   - Send email to users (if mailing list)
   - Update website/changelog

### Within First Week

1. **Monitor for issues**
   - Track upgrade problems
   - Respond to GitHub issues
   - Fix critical bugs quickly

2. **Gather feedback**
   - User experience with upgrade
   - Performance issues
   - Feature requests

3. **Metrics**
   - Track upgrade adoption
   - Monitor error rates
   - Review crash reports

## Version Numbering

Wareflow EMS follows [Semantic Versioning](https://semver.org/):

```
MAJOR.MINOR.PATCH

Examples:
- 2.0.0 - Major release (breaking changes)
- 1.2.0 - Minor release (new features)
- 1.2.3 - Patch release (bug fixes)
```

### Deciding Version Numbers

**Increment MAJOR (X.0.0) when**:
- Breaking changes introduced
- Configuration format changes
- Database schema changes
- Features removed

**Increment MINOR (0.X.0) when**:
- New features added
- Backward compatible changes
- New functionality
- Performance improvements

**Increment PATCH (0.0.X) when**:
- Bug fixes
- Security fixes
- Non-breaking changes
- Documentation updates

## Release Notes

Release notes are automatically generated from git commits using conventional commit format.

### Commit Message Format

For proper release notes, use conventional commits:

```
type(scope): description

# Types:
feat:     New feature
fix:      Bug fix
docs:     Documentation only
style:    Code style changes (formatting)
refactor: Code refactoring
perf:     Performance improvements
test:     Adding or updating tests
chore:    Maintenance tasks
build:    Build system changes
ci:       CI/CD changes
security: Security vulnerability fix

# Examples:
feat: add bulk Excel import
fix(auth): resolve login timeout issue
docs: update installation guide
security: patch file upload vulnerability
```

### Generated Sections

Release notes include these sections:
- ✨ New Features (feat:)
- 🐛 Bug Fixes (fix:)
- 🔒 Security Updates (security:)
- 📚 Documentation (docs:)
- ⚡ Performance (perf:)
- ⚠️ Breaking Changes (breaking commits)

### Manual Notes

For complex releases, you can manually edit the generated release notes on GitHub before publishing.

## Changelog

The CHANGELOG.md file is maintained automatically with each release.

### Format

Follows [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
# Changelog

## [Unreleased]
### Added
- New features (not yet released)

## [2.0.0] - 2025-01-23
### Added
- Released features
### Fixed
- Bug fixes
```

### Updating Changelog

Automatically updated by GitHub Actions when releasing. Can be manually updated with:

```bash
# Generate changelog from latest tag
python build/generate_changelog.py --update-file

# Generate for specific version
python build/generate_changelog.py --version v1.2.3 --update-file
```

## Breaking Changes

When introducing breaking changes:

### Before Release

1. **Document breaking changes**
   - Update CHANGELOG.md
   - Add migration guide
   - Document old → new behavior

2. **Implement migration**
   - Create migration script
   - Test migration from old version
   - Provide rollback mechanism

3. **Deprecation period** (if possible)
   - Mark as deprecated in previous release
   - Provide migration guide
   - Allow time for users to migrate

### In Release Notes

Clearly communicate breaking changes:

```markdown
## ⚠️ Breaking Changes

### Configuration format changed

The configuration file format has changed from JSON to YAML.

**Migration**:
Automatic migration is provided. Run:
```bash
wems upgrade
```

**Manual steps**:
If migration fails, manually convert config.json to config.yaml:
```json
{"alerts": {"critical_days": 7}}
```
Becomes:
```yaml
alerts:
  critical_days: 7
```

See [Migration Guide](docs/migration_v1_to_v2.md) for details.
```

## Security Updates

For security vulnerabilities:

### Release Process

1. **Fix privately** (in security branch if needed)
2. **Test thoroughly**
3. **Release as patch** (0.0.X)
4. **Clear communication**
   - Use "🔒 SECURITY UPDATE" in release notes
   - Include CVE number if assigned
   - Indicate severity (CRITICAL, HIGH, MEDIUM, LOW)
   - Recommend immediate upgrade

### Example Release Notes

```markdown
## 🔒 Security Updates

### Critical: File Upload Vulnerability (CVE-XXXX-XXXX)

**Severity**: CRITICAL (CVSS 9.1)
**Upgrade**: IMMEDIATELY

A path traversal vulnerability in file upload has been fixed.

**Impact**: Attackers could read arbitrary files
**Fix**: Proper path validation added
**Credit**: Reported by @researcher

All users should upgrade immediately.
```

## Rollback Plan

### Pre-Release

Always have a rollback plan:

1. **Backup previous version**
   - Tag rollback point: `v1.2.3-rollback`
   - Keep old release available

2. **Test rollback**
   - Verify users can downgrade
   - Test database rollback
   - Document rollback process

### If Release Fails

1. **Delete release** on GitHub
2. **Create hotfix patch**
3. **Release new version** quickly
4. **Communicate** with users

## Release Calendar

Planned release schedule:

### Major Releases
- **Schedule**: Every 6 months
- **Months**: January, July
- **Planning**: Starts 2 months before
- **Beta**: 2 weeks before release
- **RC**: 1 week before release

### Minor Releases
- **Schedule**: Monthly
- **Day**: First Monday of month
- **Features**: Feature freeze 1 week before

### Patch Releases
- **Schedule**: As needed
- **Trigger**: Critical bugs, security issues
- **Turnaround**: Within 48 hours for security

## Release Communication

### Channels

1. **GitHub Release** (automatic)
   - Release notes
   - Download links
   - Checksums

2. **GitHub Discussions**
   - Announcement post
   - Discussion thread

3. **Email** (if mailing list)
   - Release announcement
   - Upgrade instructions

### Announcement Template

```markdown
Subject: 🎉 Wareflow EMS v1.2.0 Released!

Hi everyone,

We're excited to announce Wareflow EMS v1.2.0!

**What's New**:
- ✨ Bulk Excel import for employees
- 🐛 Critical bug fixes
- 🔒 Security improvements

**Why Upgrade**:
- Security vulnerability fixed (upgrade recommended)
- New features save time
- Improved reliability

**How to Upgrade**:
1. Open application
2. Click "Update" when prompted
3. Follow migration wizard if needed
4. Done!

**Upgrade Time**: ~5 minutes
**Breaking Changes**: None

[Read Release Notes](link)
[Get Help](link)

Questions? Reply to this email or open a GitHub Issue.

Best regards,
Wareflow Team
```

## Troubleshooting

### Release Fails to Build

**Problem**: GitHub Actions build fails

**Solutions**:
1. Check tests are passing locally
2. Verify PyInstaller spec is correct
3. Check for syntax errors in workflows
4. View workflow logs for errors

### Release Notes Missing

**Problem**: Release notes not generated

**Solutions**:
1. Check commit messages follow conventional format
2. Verify tags are correctly formatted (vX.Y.Z)
3. Check generate_changelog.py runs locally
4. View workflow logs for changelog generation errors

### CHANGELOG.md Not Updated

**Problem**: CHANGELOG.md not committed after release

**Solutions**:
1. Check GitHub Actions permissions (contents: write)
2. Verify commit step in workflow
3. Manually update with: `python build/generate_changelog.py --update-file`
4. Commit and push manually

## Best Practices

### Do's
- ✅ Follow semantic versioning
- ✅ Use conventional commit messages
- ✅ Write tests for new features
- ✅ Document breaking changes
- ✅ Test migrations
- ✅ Communicate clearly
- ✅ Monitor after release
- ✅ Have rollback plan

### Don'ts
- ❌ Release without testing
- ❌ Skip migration for breaking changes
- ❌ Hide breaking changes
- ❌ Release on Friday (unless critical)
- ❌ Ignore security issues
- ❌ Forget to update docs
- ❌ Release major version without beta testing

## Quick Reference

### Create a Release
```bash
git tag v1.2.3
git push origin v1.2.3
```

### Generate Changelog Locally
```bash
python build/generate_changelog.py
python build/generate_changelog.py --update-file
```

### Build Locally
```bash
python build/build.py
python build/build.py --clean
```

### Check Version
```bash
git describe --tags --always
```

## Related Documents

- [CHANGELOG.md](CHANGELOG.md) - Complete change history
- [build/README.md](build/README.md) - Build system documentation
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
