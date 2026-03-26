# Code Review Skill

Review changed code with confidence-based scoring to filter false positives.

## Review Scope

By default, review unstaged changes from `git diff`. The user may specify different files or scope.

## Review Criteria

### Project Guidelines Compliance
- SAM template best practices (Globals, DeletionPolicy, least-privilege IAM)
- Powertools usage patterns (Logger, Tracer, APIGatewayHttpResolver)
- DynamoDB access patterns and key design
- Blog code snippets match actual `examples/` code

### Bug Detection
- Logic errors and null/undefined handling
- Security vulnerabilities (OWASP Top 10)
- SAM template misconfigurations

### Code Quality
- Code duplication and unnecessary complexity
- Missing error handling
- Test coverage gaps

## Confidence Scoring

Rate each issue 0-100:
- **0-49**: Do not report.
- **50-74**: Report only if critical.
- **75-89**: Verified real issue. Report with fix suggestion.
- **90-100**: Confirmed critical issue. Must report.

**Only report issues with confidence >= 75.**

## Output Format

For each issue:
```
### [CRITICAL|IMPORTANT] <issue title> (confidence: XX)
**File:** `path/to/file.ext:line`
**Issue:** Clear description of the problem
**Fix:** Concrete code suggestion
```

## Usage
Run with `/code-review` command
