from __future__ import annotations

import re
from pathlib import Path

from .models import ParsedScene, SceneConnection

EXT_RESOURCE_RE = re.compile(r'^\[ext_resource[^\]]*path="([^"]+)"[^\]]*id="([^"]+)"')
NODE_RE = re.compile(r'^\[node name="([^"]+)"([^\]]*)\]')
PARENT_RE = re.compile(r'parent="([^"]+)"')
SCRIPT_RE = re.compile(r'script\s*=\s*ExtResource\("([^"]+)"\)')
CONNECTION_RE = re.compile(
    r'^\[connection[^\]]*signal="([^"]+)"[^\]]*from="([^"]+)"[^\]]*to="([^"]+)"[^\]]*method="([^"]+)"'
)


def parse_scene(path: Path, content: str) -> ParsedScene:
    ext_resources: dict[str, str] = {}
    node_scripts: dict[str, str] = {}
    connections: list[SceneConnection] = []
    current_node: str | None = None

    for raw_line in content.splitlines():
        line = raw_line.strip()
        ext_match = EXT_RESOURCE_RE.match(line)
        if ext_match:
            resource_path, resource_id = ext_match.groups()
            ext_resources[resource_id] = _normalize_resource_path(resource_path)
            continue

        node_match = NODE_RE.match(line)
        if node_match:
            name, rest = node_match.groups()
            parent_match = PARENT_RE.search(rest)
            current_node = name if parent_match else "."
            continue

        script_match = SCRIPT_RE.search(line)
        if script_match and current_node is not None:
            script_path = ext_resources.get(script_match.group(1))
            if script_path:
                node_scripts[current_node] = script_path
            continue

        connection_match = CONNECTION_RE.match(line)
        if connection_match:
            signal, from_node, to_node, method = connection_match.groups()
            connections.append(
                SceneConnection(
                    scene_path=path,
                    signal=signal,
                    from_node=from_node,
                    to_node=to_node,
                    method=method,
                )
            )

    return ParsedScene(path=path, node_scripts=node_scripts, connections=connections)


def _normalize_resource_path(path: str) -> str:
    if path.startswith("res://"):
        return path.removeprefix("res://")
    return path
