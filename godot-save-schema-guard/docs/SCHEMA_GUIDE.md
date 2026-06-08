# Schema Guide

The first release supports a practical subset of JSON Schema:

- `type`: `object`, `array`, `string`, `integer`, `number`, `boolean`, `null`
- `required`
- `properties`
- `items`
- `additionalProperties: false`

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
