# Dependency management

## Automated updates

Dependabot checks the root Python requirements, Streamlit application requirements, and GitHub Actions every Monday. It groups compatible updates to keep review volume manageable.

Review every update before merging. For dependency changes:

1. Inspect the package changelog and supported Python versions.
2. Check for breaking changes and security advisories.
3. Run the complete CI workflow.
4. Verify the application starts and the affected feature works.
5. Merge only after reviewing the resulting constraints and test results.

This repository uses bounded version ranges in its requirements files. Dependabot updates those ranges; it does not replace review or testing.

## Vulnerability auditing

The **Dependency Security Audit** workflow runs weekly and can also be started manually from GitHub Actions. It audits both the backend/shared runtime requirements and the Streamlit runtime requirements with pip-audit in strict mode.

A failed audit means one or more resolved dependencies have a known vulnerability or the audit could not complete successfully. Review the workflow log and advisory details before changing package constraints. Do not suppress an advisory merely to make the workflow green.

## Operational notes

- Keep development and runtime dependencies separate where practical.
- Do not commit generated credentials, environment files, or private package indexes.
- Re-run the full test suite after dependency updates.
- The audit covers Python package advisories; it does not scan container images, operating-system packages, deployed infrastructure, or application logic.