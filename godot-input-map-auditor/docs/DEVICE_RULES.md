# Device Classification

The first release classifies Godot event classes by family:

- `InputEventKey`: `keyboard`
- `InputEventMouseButton`, `InputEventMouseMotion`: `mouse`
- `InputEventJoypadButton`, `InputEventJoypadMotion`: `gamepad`
- `InputEventScreenTouch`, `InputEventScreenDrag`, `InputEventGesture`: `touch`

Unknown event classes remain in the event list but do not satisfy a device-family requirement.
