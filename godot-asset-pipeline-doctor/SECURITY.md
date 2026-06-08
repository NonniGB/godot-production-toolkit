# Security

## Supported Versions

Only the latest released version receives security fixes.

## Reporting A Vulnerability

Open a private security advisory on the repository if available. If private advisories are not available, open an issue that describes the impact without attaching sensitive project files.

## Data Handling

The tool scans local file metadata and image pixels. It does not upload project files, contact external services, or execute Godot scripts. Reports may include local file paths, so review JSON or text output before posting it publicly.

## Untrusted Projects

The scanner reads PNG files and text `.import` files. Treat reports from untrusted repositories carefully, and avoid sharing generated output if paths reveal private information.

