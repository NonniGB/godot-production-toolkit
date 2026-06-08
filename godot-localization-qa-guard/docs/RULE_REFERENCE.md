# Rule Reference

- `no_catalogs`: no translation files were provided.
- `csv_missing_keys_header`: CSV header does not start with `keys`.
- `utf8_bom_detected`: CSV starts with a UTF-8 BOM.
- `duplicate_key`: duplicate CSV key or PO `msgid`.
- `missing_language_column`: required language is missing from a CSV file.
- `empty_translation`: required target cell or PO `msgstr` is empty.
- `fuzzy_translation`: PO entry is marked fuzzy.
- `unchanged_translation`: target string matches the source string.
- `placeholder_mismatch`: source and target placeholder sets differ.
- `missing_key`: scanned project text references a key not present in catalogs.
- `unused_key`: catalog key was not seen in scanned project text.
