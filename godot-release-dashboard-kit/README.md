# Godot Release Dashboard Kit

`godot-release-dashboard-kit` builds a small static dashboard from JSON,
Markdown, and image artifacts produced by Godot Production Toolkit commands.

It is intentionally simple: point it at a reports folder and it writes a
self-contained HTML file suitable for a CI artifact or release checklist.

## Install

```powershell
python -m pip install godot-release-dashboard-kit
```

From a source checkout:

```powershell
python -m pip install -e .\godot-release-dashboard-kit
```

## Quick Start

```powershell
godot-release-dashboard build reports\godot-project-doctor --output reports\dashboard.html
```

Write a machine-readable dashboard summary:

```powershell
godot-release-dashboard build reports\godot-project-doctor --format json --output reports\dashboard.json
```

## Inputs

The dashboard scans a folder recursively for `.json`, `.md`, `.png`, `.jpg`,
`.jpeg`, `.svg`, and `.webp` files. Toolkit JSON reports are summarized through
their `tool`, `kind`, and `summary` fields when available. Image artifacts such
as mobile UI overlays, screenshot diffs, pixel previews, and visual smoke
captures are embedded into the self-contained HTML output.

## Outputs

- `html`: self-contained static dashboard with report cards and image previews.
- `json`: summary for scripts or later dashboard tooling.
