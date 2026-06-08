# Placeholder Checks

The guard compares placeholder sets between source and target text:

- `{name}`
- `{count}`
- `%s`
- `%d`
- `%i`
- `%f`

Example failure:

```csv
keys,en,fr
ITEM_COUNT,{count} items,{total} objets
```

The names differ, so formatting can fail or show incorrect data at runtime.
