# Security

`godot-pack-mod-doctor` reads local JSON manifests and does not require network
access.

Do not publish private project paths, unreleased content names, credentials, or
player data in public pack manifests or issue fixtures.

Manifest checks flag common review risks such as local paths, parent-directory
segments, development folders, logs, backups, key files, scripts, native
binaries, archives, and packed project files. These warnings are review aids;
they do not inspect file contents or guarantee that a pack is safe to run.
