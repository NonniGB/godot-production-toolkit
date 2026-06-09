# Rule Reference

- `stale_scene_connection`: a persistent scene connection targets a method missing from the resolved target script. This often happens after a method rename or scene refactor.
- `autoload_signal_usage`: a configured autoload name is used in a signal connect call. This is not always wrong, but it is worth reviewing when global signal usage grows.

Use `--strict-stale-connections` to make stale scene connections errors. Without it, stale connections are warnings.
