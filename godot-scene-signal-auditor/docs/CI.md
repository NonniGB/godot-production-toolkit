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
