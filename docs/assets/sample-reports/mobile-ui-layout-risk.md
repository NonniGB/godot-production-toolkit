# Godot Mobile UI Layout Risk

| Metric | Value |
|---|---:|
| Text nodes | 3 |
| Matched nodes | 2 |
| Unmatched text nodes | 1 |
| Stress entries | 5 |
| Warnings | 7 |

## Findings

| Severity | Screen | Node | Key | Variant | Estimated / Available Width | Message |
|---|---|---|---|---|---:|---|
| warning | main_menu | play | `MENU_START` | long | 79.2 / 38.0 | Node 'play' may overflow with long stress text from key 'MENU_START'. |
| warning | main_menu | play | `MENU_START` | pseudo | 132.0 / 38.0 | Node 'play' may overflow with pseudo stress text from key 'MENU_START'. |
| warning | main_menu | play | `MENU_START` | rtl | 61.6 / 38.0 | Node 'play' may overflow with rtl stress text from key 'MENU_START'. |
| warning | main_menu | options | `MENU_SETTINGS` | compact | 132.0 / 76.0 | Node 'options' may overflow with compact stress text from key 'MENU_SETTINGS'. |
| warning | main_menu | options | `MENU_SETTINGS` | long | 422.4 / 76.0 | Node 'options' may overflow with long stress text from key 'MENU_SETTINGS'. |
| warning | main_menu | options | `MENU_SETTINGS` | pseudo | 387.2 / 76.0 | Node 'options' may overflow with pseudo stress text from key 'MENU_SETTINGS'. |
| warning | main_menu | options | `MENU_SETTINGS` | rtl | 255.2 / 76.0 | Node 'options' may overflow with rtl stress text from key 'MENU_SETTINGS'. |
