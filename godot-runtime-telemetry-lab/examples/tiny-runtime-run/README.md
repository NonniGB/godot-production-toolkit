# Tiny Runtime Run

This fixture is a minimal telemetry sample for `godot-runtime-telemetry-lab`.
It is not tied to a specific game project; it uses ordinary frame, physics,
memory, node, and draw-call fields that a Godot smoke test or debug exporter can
write as JSON or CSV.

It demonstrates a frame-budget spike during a short combat phase, a small memory
trend, and a timeline report that can be opened locally or uploaded as a CI
artifact.

```powershell
godot-telemetry-lab timeline godot-runtime-telemetry-lab\examples\tiny-runtime-run --format html --output reports\runtime-timeline.html
godot-telemetry-lab budget init --profile android-high --output reports\runtime-budget.json
godot-telemetry-lab summarize godot-runtime-telemetry-lab\examples\tiny-runtime-run --budget-file reports\runtime-budget.json --format markdown
```

This folder also includes `android-high-budget.json`, generated with
`budget init`, so the example can be run without creating a budget first.
