# Godot Mobile UI Doctor

| Metric | Value |
|---|---:|
| Screens | 1 |
| Viewports | 1 |
| Nodes | 3 |
| Interactive nodes | 2 |
| Errors | 0 |
| Warnings | 6 |

## Findings

| Severity | Rule | Location | Message | Help |
|---|---|---|---|---|
| warning | `safe_area_overlap` | main_menu / portrait_phone / title | Node 'title' overlaps the safe-area inset for viewport 'portrait_phone'. | Move important controls and labels inside the safe-area rectangle. |
| warning | `text_overflow_risk` | main_menu / portrait_phone / title | Text on node 'title' may not fit inside its exported rectangle. | Allow wrapping, shorten the label, resize the control, or check localized strings. |
| warning | `text_overflow_risk` | main_menu / portrait_phone / play | Text on node 'play' may not fit inside its exported rectangle. | Allow wrapping, shorten the label, resize the control, or check localized strings. |
| warning | `touch_target_too_small` | main_menu / portrait_phone / play | Interactive node 'play' is 40x40; target size is 44px. | Increase the clickable area or wrap the control in a larger touch zone. |
| warning | `text_overflow_risk` | main_menu / portrait_phone / options | Text on node 'options' may not fit inside its exported rectangle. | Allow wrapping, shorten the label, resize the control, or check localized strings. |
| warning | `touch_targets_too_close` | main_menu / portrait_phone / play,options | Interactive nodes 'play' and 'options' are 2.0px apart; target spacing is 8px. | Add spacing or make only one of the overlapping rectangles interactive. |
