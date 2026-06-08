# Reviewer Scorecard

## Automated review

| Signal | Evidence |
|---|---|
| Root README explains purpose quickly | `README.md` |
| Machine-readable evidence exists | `oss-review-evidence.json` |
| AI-facing summary exists | `AI_REVIEW_PACKAGE.md` |
| Agent manifests are validated | `verify_agent_interfaces.py` |
| Tests cover repository contract | `tests/` |
| CI workflow exists | `.github/workflows/portfolio-ci.yml` |
| GitHub Action adoption path exists | `godot-ci-doctor-action/action.yml` |

## Open-source maintenance

| Signal | Evidence |
|---|---|
| License | `LICENSE` and per-tool `LICENSE` files |
| Security policy | `SECURITY.md` and per-tool `SECURITY.md` files |
| Contribution guidance | `CONTRIBUTING.md` and per-tool `CONTRIBUTING.md` files |
| Support guidance | `SUPPORT.md` |
| Code of conduct | `CODE_OF_CONDUCT.md` |
| Issue templates | `.github/ISSUE_TEMPLATE/` |
| Dependency update config | `.github/dependabot.yml` |
| Maintainer automation | `docs/MAINTAINER_AUTOMATION.md` |

## Known gap

The known gap is organic public usage. This repository can prove technical readiness, release readiness, and maintainer intent. It cannot honestly prove external adoption before publication.
