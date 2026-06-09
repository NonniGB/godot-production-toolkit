# Policy Files

Use a policy file when different kinds of actions need different device
coverage. For example, movement actions might need keyboard and touch bindings,
while debug actions only need keyboard bindings.

By default, the CLI reads `.godot-input-map-auditor.toml` beside
`project.godot` when it exists. You can also pass a file explicitly:

```powershell
godot-input-audit . --policy input-policy.toml --format json
```

Example:

```toml
[action_groups]
movement = ["move_*", "dash"]
menu = ["ui_*", "pause"]
debug = ["debug_*"]

[group_requirements]
movement = ["keyboard", "touch"]
menu = ["keyboard", "controller", "touch"]
debug = ["keyboard"]
```

Patterns use shell-style matching such as `move_*`. The first matching group is
used for each action.

Supported device families are:

- `keyboard`
- `mouse`
- `controller`
- `touch`

JSON reports include the matched group and group-specific required devices for
each action. Generated Markdown input references also include a group column
when a policy file is active.
