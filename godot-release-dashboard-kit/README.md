# Godot Release Dashboard Kit

`godot-release-dashboard-kit` builds a small static dashboard from JSON and
Markdown reports produced by Godot Production Toolkit commands.

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

The first release scans a folder recursively for `.json` and `.md` files.
Toolkit JSON reports are summarized through their `tool`, `kind`, and `summary`
fields when available.

## Outputs

- `html`: self-contained static dashboard.
- `json`: summary for scripts or later dashboard tooling.
