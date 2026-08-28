"""Bundle a canonical schema for use as an MCP tool inputSchema/outputSchema.

The canonical files reference each other by `$id` (`intent` → `target-ref`).
MCP 2026-07-28 imposes `$ref` resolution requirements on tool schemas, so a
tool definition gets a self-contained copy: every cross-file reference is
rewritten to a local `$defs` entry. Semantics are unchanged; only where the
bytes live.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from .validate import SCHEMA_DIR, load_schema


def _walk(node: Any, seen: dict[str, dict[str, Any]], schema_dir: Path) -> Any:
    if isinstance(node, dict):
        out: dict[str, Any] = {}
        for key, value in node.items():
            if key == "$ref" and isinstance(value, str) and not value.startswith("#"):
                name = value.rsplit("/", 1)[-1].replace(".schema.json", "")
                if name not in seen:
                    seen[name] = {}  # placeholder guards cycles
                    other = load_schema(schema_dir / f"{name}.schema.json")
                    other.pop("$schema", None)
                    other.pop("$id", None)
                    seen[name] = _walk(other, seen, schema_dir)
                out["$ref"] = f"#/$defs/{name}"
            else:
                out[key] = _walk(value, seen, schema_dir)
        return out
    if isinstance(node, list):
        return [_walk(item, seen, schema_dir) for item in node]
    return node


def bundle(schema_path: Path) -> dict[str, Any]:
    root = load_schema(schema_path)
    seen: dict[str, dict[str, Any]] = {}
    bundled = _walk(root, seen, schema_path.parent)
    if seen:
        defs = dict(bundled.get("$defs", {}))
        defs.update(seen)
        bundled["$defs"] = defs
    return bundled


def has_remote_ref(node: Any) -> bool:
    if isinstance(node, dict):
        return any((k == "$ref" and isinstance(v, str) and not v.startswith("#")) or has_remote_ref(v) for k, v in node.items())
    if isinstance(node, list):
        return any(has_remote_ref(item) for item in node)
    return False


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: python -m hostproto.bundle SCHEMA", file=sys.stderr)
        return 64
    print(json.dumps(bundle(Path(argv[0])), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
