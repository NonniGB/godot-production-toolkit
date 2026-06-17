# Schema Guide

The first release supports a practical subset of JSON Schema:

- `type`: `object`, `array`, `string`, `integer`, `number`, `boolean`, `null`
- `required`
- `properties`
- `items`
- `additionalProperties: false`
- `default`, `const`, `enum`, and `examples` for generated fixture values.

Example:

```json
{
  "type": "object",
  "required": ["version"],
  "properties": {
    "version": { "type": "integer" }
  }
}
```

`generate-fixture` uses required fields by default, plus `default`, `const`,
the first `enum` value, or the first `examples` value when those hints are
present. Add `--include-optional` to include optional properties too, and use
`--set dotted.path=json_value` for stable IDs or intentionally recognizable
values.
