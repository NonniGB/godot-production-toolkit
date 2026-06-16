# Security

Save files can contain private player or test data. Do not publish real save files as issue attachments.

`godot-save-guard redact` can write sanitized fixture copies for selected JSON
paths, but it is not automatic private-data detection. Unlisted fields remain
unchanged, and reports can still include fixture paths and schema field names.
Review sanitized files before sharing them.

Migration commands are user-supplied and executed locally. Review command templates before running them in CI.
