# Godot Scenario Report

- Scenarios: 2
- Passed: 1
- Failed: 1
- Errors: 2
- Warnings: 0

| Scenario | Status | Duration ms | Assertions |
|---|---|---:|---:|
| scenario.menu_startup | passed | 812.0 | 0 |
| scenario.trade_flow | failed | 1450.0 | 1 |

## Findings

| Severity | Rule | Scenario | Message | Help |
|---|---|---|---|---|
| error | scenario_failed | scenario.trade_flow | scenario.trade_flow reported failed status. | Open the scenario source and attached artifacts first; this is the top-level run failure. |
| error | assertion_failed | scenario.trade_flow | scenario.trade_flow assertion 'failure' failed. expected cargo transfer event was not observed | Inspect the named assertion and its message before rerunning the whole scenario suite. |
