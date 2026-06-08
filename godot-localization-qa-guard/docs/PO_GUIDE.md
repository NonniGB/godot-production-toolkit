# PO Guide

The PO parser supports straightforward gettext entries:

```po
#, fuzzy
msgid "MENU_START"
msgstr "Demarrer"
```

Checks include:

- Empty `msgstr`.
- Fuzzy entries.
- Duplicate `msgid`.
- Placeholder mismatch between `msgid` and `msgstr`.

The language is inferred from the file stem, such as `fr.po`.
