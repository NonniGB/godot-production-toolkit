# Security

This package reads local JSON result files and does not require network access.
Avoid sharing private save files, logs, or screenshots in public issues; a small
synthetic run file is usually enough.

Scenario bundles can link logs, JUnit XML, profiler captures, screenshots, and
other local files with `--evidence KIND=PATH`. The bundle does not copy or inline
those file contents, but the report can still reveal file names, relative paths,
or absolute paths if you pass them. Review bundle JSON, Markdown, or HTML before
publishing it as a public CI artifact.
