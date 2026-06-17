# Godot Scenario Report

- Scenarios: 2
- Passed: 0
- Failed: 0
- Errors: 0
- Warnings: 2

| Scenario | Status | Duration ms | Assertions |
|---|---|---:|---:|
| menu_startup | warning | 2710.0 | 0 |
| trade_flow | warning | 6550.0 | 0 |

## Findings

| Severity | Rule | Scenario | Message | Help |
|---|---|---|---|---|
| warning | flaky_scenario | menu_startup | menu_startup changed status across runs: failed, passed. | Inspect logs and artifacts from both passing and failing runs before treating this scenario as stable. |
| warning | flaky_scenario | trade_flow | trade_flow changed status across runs: failed, passed. | Inspect logs and artifacts from both passing and failing runs before treating this scenario as stable. |

## Flaky Scenarios

| Scenario | Statuses | Observations |
|---|---|---:|
| menu_startup | failed, passed | 3 |
| trade_flow | failed, passed | 4 |

## Retried Scenarios

| Scenario | Run | Attempts | Statuses | Final status |
|---|---|---:|---|---|
| trade_flow | godot-scenario-report-kit\examples\tiny-scenario-runs\retry-run | 2 | failed, passed | passed |
