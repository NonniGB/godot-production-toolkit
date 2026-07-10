# Rule Reference

- `invalid_json`: fixture is not valid JSON.
- `missing_version_field`: top-level `version` is missing.
- `missing_required_property`: schema-required property is absent.
- `numeric_type_drift`: schema expects a number but the save stores a numeric string.
- `type_mismatch`: value type does not match schema.
- `unexpected_property`: schema has `additionalProperties: false` and the save contains an extra field.
- `migration_command_failed`: migration command returned a non-zero exit code.
  Chain reports include step and output context plus captured command output
  when available.
- `migration_chain_empty`: a migration chain file did not contain valid steps.
- `migration_chain_planned`: dry-run output showing the ordered migration steps.
- `migration_path_missing`: a supported save version has no migration path to the current format.
- `redaction_applied`: selected scalar values were redacted and a sanitized fixture copy was written.
- `redaction_non_scalar_target`: a configured redaction path matched an object or array and was left unchanged.
- `redaction_output_exists`: the sanitized output file already exists and `--overwrite` was not set.
- `redaction_path_missing`: a configured redaction path was not found in a fixture.
- `redaction_planned`: dry-run output showing how many values would be redacted.
