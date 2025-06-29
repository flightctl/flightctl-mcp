## 📋 Description
Brief description of the changes made in this PR.

**Related Issue(s):** 
<!-- Link to related issues: Fixes #123, Closes #456 -->

**DCO Compliance:** 
All commits in this PR are signed off with `git commit -s` to comply with the Developer Certificate of Origin.

## 🔄 Type of Change
<!-- Check all that apply -->
- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation update
- [ ] 🧪 Test improvements
- [ ] 🔧 Infrastructure/tooling changes
- [ ] 🎨 Code style/refactoring (no functional changes)

## 🧪 Testing
<!-- Describe the tests you ran and how to reproduce them -->

### Unit Tests
- [ ] Added unit tests for new functionality
- [ ] Updated existing unit tests
- [ ] All unit tests pass (`make test-unit`)

### Integration Tests  
- [ ] Added integration tests if needed
- [ ] All integration tests pass (`make test`)

### Manual Testing
- [ ] Tested against live Flight Control instance (`python test_live_instance.py`)
- [ ] Tested with different configurations
- [ ] Verified backwards compatibility

**Test Results:**
```bash
# Paste relevant test output here
make test
# Output...
```

## 🔍 Code Quality
<!-- Ensure code quality standards are met -->
- [ ] Code follows style guidelines (`make lint` passes)
- [ ] Code is properly formatted (`black --check` passes)
- [ ] Type hints are included where appropriate
- [ ] Functions and classes are properly documented
- [ ] No security issues introduced

## 📖 Documentation
<!-- Check if documentation needs to be updated -->
- [ ] Updated README.md (if needed)
- [ ] Updated TESTING.md (if test procedures changed)
- [ ] Updated docstrings for new/modified functions
- [ ] Added examples for new features
- [ ] Updated configuration documentation

## ⚠️ Breaking Changes
<!-- If this is a breaking change, describe what breaks and how to migrate -->
**Is this a breaking change?** No / Yes

If yes, describe:
- What breaks
- How to migrate from old behavior
- Deprecation timeline (if applicable)

## 🎯 Checklist
<!-- Ensure your PR is ready for review -->
### Before Submitting
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] My changes generate no new warnings or errors
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

### CI/CD
- [ ] All GitHub Actions checks pass
- [ ] Container builds successfully
- [ ] Code coverage is maintained or improved

### Git & DCO
- [ ] My commits have clear, descriptive messages
- [ ] All commits are signed off with `git commit -s` (DCO compliance)
- [ ] I have rebased onto the latest main branch
- [ ] My branch is up to date with upstream/main

## 🖼️ Screenshots
<!-- If applicable, add screenshots to help reviewers understand the changes -->

## 📝 Additional Notes
<!-- Add any additional notes, concerns, or context for reviewers -->

### Performance Impact
<!-- Describe any performance implications -->

### Security Considerations
<!-- Describe any security implications -->

### Future Work
<!-- Any follow-up work that should be done -->

---

## 👀 Review Guidelines for Maintainers

**Focus Areas:**
- [ ] Code quality and style
- [ ] Test coverage and quality
- [ ] Documentation completeness
- [ ] Security implications
- [ ] Performance impact
- [ ] Backwards compatibility

**Testing:**
- [ ] Code builds and runs successfully
- [ ] All tests pass
- [ ] Manual testing confirms functionality
- [ ] No regression in existing features 