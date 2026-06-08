# Security Policy

## Supported scope

This repository contains static analysis, report generation, deterministic asset utilities, and a GitHub composite action. The tools are intended to run on local projects and CI checkouts without requiring network access, except package installation in GitHub Actions.

## Reporting a vulnerability

Open a private advisory when available, or create a minimal public issue that avoids secrets and proprietary files. Include the affected tool, command, version, operating system, and a minimal fixture.

## Secret handling

Do not paste signing keys, API tokens, keystores, export credentials, private project archives, or proprietary assets into issues. The export preset checker is designed to redact suspicious values, but reporters should still provide reduced fixtures.
