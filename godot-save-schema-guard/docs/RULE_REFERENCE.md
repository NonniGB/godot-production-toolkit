# Rule Reference

- `invalid_json`: fixture is not valid JSON.
- `missing_version_field`: top-level `version` is missing.
- `missing_required_property`: schema-required property is absent.
- `numeric_type_drift`: schema expects a number but the save stores a numeric string.
- `type_mismatch`: value type does not match schema.
- `unexpected_property`: schema has `additionalProperties: false` and the save contains an extra field.
- `migration_command_failed`: migration command returned a non-zero exit code.
- `migration_chain_empty`: a migration chain file did not contain valid steps.
- `migration_chain_planned`: dry-run output showing the ordered migration steps.
