# Godot Scenario Report

- Scenarios: 2
- Passed: 1
- Failed: 1
- Errors: 3
- Warnings: 2

| Scenario | Status | Duration ms | Assertions |
|---|---|---:|---:|
| menu_startup | passed | 910.0 | 1 |
| trade_flow | failed | 2400.0 | 2 |

## Findings

| Severity | Rule | Scenario | Message |
|---|---|---|---|
| warning | missing_artifact | menu_startup | menu_startup lists missing artifact 'screenshots/menu.png'. |
| error | scenario_failed | trade_flow | trade_flow reported failed status. |
| error | assertion_failed | trade_flow | trade_flow assertion 'trade completed' failed. Buy button stayed disabled. |
| error | new_scenario_failure | trade_flow | trade_flow passed in the baseline but is now failed. |
| warning | duration_regression | trade_flow | trade_flow took 2400 ms, up from 1320 ms. |
