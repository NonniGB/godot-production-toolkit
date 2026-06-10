# Sprite Manifests

`godot-asset-doctor manifest check` validates project-owned sprite metadata
against the PNG files it describes. It is useful when sprites have hand-authored
attachment points such as sockets, hardpoints, UI markers, thrusters, or spawn
points.

## Example

```powershell
godot-asset-doctor manifest check sprite-manifest.json --project . --format json --output reports\sprite-manifest.json
```

Render a contact sheet for visual review:

```powershell
godot-asset-doctor manifest contact-sheet sprite-manifest.json --project . --output reports\sprite-contact-sheet.png
```

## Manifest Shape

```json
{
  "sprites": [
    {
      "id": "player_ship",
      "source_path": "assets/player_ship.png",
      "runtime_path": "res://assets/player_ship.png",
      "width": 64,
      "height": 64,
      "tags": ["ship", "player"],
      "anchors": {
        "muzzle": {"x": 58, "y": 28},
        "engine": {"x": 6, "y": 32}
      }
    }
  ]
}
```

## Checks

- sprite entries must be objects;
- sprite ids must be present and unique;
- `source_path` must exist and point to a PNG file;
- declared width and height must match the PNG;
- anchors must stay within the PNG bounds.

Anchor coordinates are checked in pixel space using the source PNG dimensions.
Coordinates on the edge, such as `x = width` or `y = height`, are accepted so
projects can represent edge sockets deliberately.

## Contact Sheets

`manifest contact-sheet` writes a PNG review sheet from every renderable sprite
in the manifest. It keeps transparent sprites readable with a checkerboard
background, labels each sprite by id, and draws anchor markers on top of the
thumbnail. Add `--show-anchor-labels` when the anchor names themselves should
appear in the image.

Use this when reviewing sockets, hardpoints, muzzle positions, UI markers,
thruster points, or spawn points:

```powershell
godot-asset-doctor manifest contact-sheet sprite-manifest.json --project . --output reports\sprite-contact-sheet.png --thumb-size 128 --columns 5
```

Example output:

![Sprite contact sheet with anchor markers](images/sprite-contact-sheet.png)

The command only writes the requested output file. It does not modify source
images or manifest data.
