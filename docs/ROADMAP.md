# Roadmap

This roadmap is grouped by the kind of Godot workflow a user is trying to make
safer. It is not a promise of dates; it is a practical map for issues, fixtures,
and small contributions.

## Export And Release Targets

Useful next work:

- export preset diff reports for before/after release reviews;
- exported-folder or PCK manifest inspection when direct PCK parsing is not
  available;
- more HTML5 and desktop export examples.

Suggested labels: `workflow: export`, `report schema`, `good first fixture`.

## Mobile UI And Localization

Useful next work:

- overlay highlights that consume joined localization layout-risk reports;
- more safe-area overlay examples for phone and tablet viewports;
- font/glyph coverage examples for localized UI.

Suggested labels: `workflow: mobile-ui`, `workflow: localization`,
`good first fixture`.

## Runtime Evidence

Useful next work:

- scenario evidence bundles for dashboards;
- retry and flaky-run summaries;
- telemetry adapters for common CSV/JSON profiler exports.

Suggested labels: `workflow: runtime-evidence`, `workflow: dashboard`,
`report schema`.

## Content, Saves, Packs, And Mods

Useful next work:

- save migration lab reports that show source fixture, migration command, and
  destination validation together;
- pack diff and load-order checks;
- content graph presets for more common Godot data shapes.

Suggested labels: `workflow: content-data`, `good first fixture`.

## GDScript Refactor Safety

Useful next work:

- scene contract checks for required child nodes, groups, signals, and methods;
- architecture dead-zone reports for likely unused scripts/resources;
- ownership and hotspot summaries for larger projects.

Suggested labels: `workflow: gdscript-architecture`, `good first fixture`.

## Reports And Dashboards

Useful next work:

- more report schemas for package-specific JSON payloads;
- a stronger release dashboard demo with several linked artifacts;
- short docs for using dashboard outputs as CI artifacts.

Suggested labels: `workflow: dashboard`, `workflow: visual-regression`,
`report schema`.
