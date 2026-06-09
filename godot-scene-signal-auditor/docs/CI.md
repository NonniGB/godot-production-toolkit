# CI Usage

```yaml
- name: Install signal auditor
  run: python -m pip install godot-scene-signal-auditor

- name: Audit scene signals
  run: godot-signal-audit . --strict-stale-connections --format json --output signal-report.json
```

Generate a graph artifact:

```powershell
godot-signal-audit . --format mermaid --output docs\SIGNAL_GRAPH.md
```

JSON reports include a small metadata block, summary counts, a rule catalog, and
per-finding explanations. Keep the JSON report as a CI artifact when scene wiring
failures need review outside the job log.
