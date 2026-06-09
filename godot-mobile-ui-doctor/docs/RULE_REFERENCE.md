# Rule Reference

| Rule | Severity | Meaning |
|---|---|---|
| `missing_viewport` | error | A screen references a viewport that is not present. |
| `duplicate_node_id` | error | A screen repeats a node id, making reports ambiguous. |
| `node_outside_viewport` | error | A node rectangle leaves the viewport bounds. |
| `safe_area_overlap` | warning | A node overlaps the configured safe-area insets. |
| `touch_target_too_small` | warning | An interactive control is smaller than the configured target size. |
| `touch_targets_too_close` | warning | Two interactive controls are closer than the configured spacing. |
| `text_overflow_risk` | warning | The exported text may not fit in the node rectangle. |
| `no_interactive_controls` | warning | A screen contains no interactive metadata. |

These rules are intentionally conservative. They flag layout risks that deserve
review; they do not try to judge whether a screen is well designed.
