# Rule Reference

- `stale_scene_connection`: a persistent scene connection targets a method missing from the resolved target script.
- `autoload_signal_usage`: a configured autoload name is used in a signal connect call.

Use `--strict-stale-connections` to make stale scene connections errors. Without it, stale connections are warnings.
