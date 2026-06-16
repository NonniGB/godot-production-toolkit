# Toolkit Diagrams

These GitHub-renderable Mermaid diagrams show how the Godot Production Toolkit
pieces fit together. For command details, start with the
[Tool Index](../TOOL_INDEX.md), [Use Cases](../USE_CASES.md),
[workflow guides](../workflows/), and [report gallery](../report-gallery/).

## Tool Output Flow

```mermaid
flowchart LR
    project["Godot project files"]
    ui_json["mobile-ui.json"]
    scenario_json["scenario run JSON"]
    runtime_json["runtime samples"]

    export_tool["godot-export-doctor"]
    asset_tool["godot-asset-doctor"]
    input_tool["godot-input-audit"]
    mobile_perf_tool["godot-mobile-perf-doctor"]
    mobile_ui_tool["godot-mobile-ui-doctor"]
    scenario_tool["godot-scenario-report"]
    telemetry_tool["godot-telemetry-lab"]
    project_tool["godot-project-doctor"]
    dashboard_tool["godot-release-dashboard"]

    reports["JSON, Markdown, SARIF, PNG, HTML reports"]
    mobile_readiness["mobile readiness report"]
    scenario_report["scenario evidence"]
    runtime_report["runtime evidence"]
    release_page["release dashboard HTML"]

    project --> export_tool --> reports
    project --> asset_tool --> reports
    project --> input_tool --> reports
    project --> mobile_perf_tool --> reports
    ui_json --> mobile_ui_tool
    reports --> mobile_ui_tool --> mobile_readiness
    scenario_json --> scenario_tool --> scenario_report
    runtime_json --> telemetry_tool --> runtime_report
    reports --> project_tool --> release_page
    mobile_readiness --> dashboard_tool
    scenario_report --> dashboard_tool
    runtime_report --> dashboard_tool
    reports --> dashboard_tool --> release_page
```

See the [Tool Index](../TOOL_INDEX.md) for package names and output formats.

## Release Evidence Workflow

```mermaid
flowchart TD
    start["Pick release profile"]
    run_checks["Run export, asset, input, and mobile performance checks"]
    collect["Collect reports in one reports directory"]
    summarize["Build project summary"]
    review["Review findings and linked artifacts"]
    fix["Fix project or config issues"]
    dashboard["Publish static dashboard"]
    archive["Archive release evidence"]

    start --> run_checks --> collect --> summarize --> review
    review -->|findings remain| fix --> run_checks
    review -->|ready| dashboard --> archive
```

Useful references:
[CI release checklist](../workflows/godot-ci-release-checklist.md),
[Android export CI](../workflows/godot-android-export-ci.md), and
[release dashboard samples](../report-gallery/).

## Mobile Readiness Workflow

```mermaid
flowchart TD
    export_ui["Export resolved UI rectangles"]
    check_ui["Check safe areas, touch targets, spacing, and overflow"]
    audit_input["Audit keyboard, touch, mouse, and controller input"]
    check_export["Check Android export settings"]
    check_perf["Check mobile renderer and texture settings"]
    optional_visual["Optional visual smoke plan"]
    readiness["Build mobile readiness report"]
    review_mobile["Review mobile blockers"]
    fix_mobile["Fix UI, input, export, or asset settings"]
    done["Attach report to release evidence"]

    export_ui --> check_ui
    check_ui --> readiness
    audit_input --> readiness
    check_export --> readiness
    check_perf --> readiness
    optional_visual --> readiness
    readiness --> review_mobile
    review_mobile -->|blockers remain| fix_mobile --> export_ui
    review_mobile -->|ready| done
```

Useful references:
[mobile UI safe-area testing](../workflows/godot-mobile-ui-safe-area-testing.md),
[localization overflow testing](../workflows/godot-localization-overflow-testing.md),
and [Mobile UI Readiness](../USE_CASES.md#mobile-ui-readiness).
