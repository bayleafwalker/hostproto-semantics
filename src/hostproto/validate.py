"""Dependency-free validator for the JSON Schema subset these schemas use.

Supported: type, const, enum, required, properties, additionalProperties,
items, minItems, minProperties, minLength, maxLength, minimum, pattern,
anyOf, allOf, if/then, $ref (local `#/$defs/...` and cross-file within
`schemas/`). Anything else in a schema is a defect: `unsupported_keywords`
reports it so a schema cannot quietly rely on a keyword nobody checks.
CI additionally runs the full `jsonschema` package.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schemas"
SUPPORTED = {
    "$schema", "$id", "title", "description", "type", "const", "enum", "required", "properties",
    "additionalProperties", "items", "minItems", "minProperties", "minLength", "maxLength",
    "minimum", "pattern", "anyOf", "allOf", "if", "then", "$ref", "$defs",
}
_TYPES = {"object": dict, "array": list, "string": str, "integer": int, "boolean": bool, "null": type(None)}


def load_schema(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def unsupported_keywords(schema: Any, found: set[str] | None = None) -> set[str]:
    found = set() if found is None else found
    if isinstance(schema, dict):
        for key, value in schema.items():
            if key not in SUPPORTED and key not in ("properties", "$defs"):
                found.add(key)
            if key in ("properties", "$defs", "additionalProperties", "items", "if", "then") or key in SUPPORTED:
                if key in ("properties", "$defs") and isinstance(value, dict):
                    for sub in value.values():
                        unsupported_keywords(sub, found)
                elif isinstance(value, (dict, list)):
                    unsupported_keywords(value, found)
    elif isinstance(schema, list):
        for item in schema:
            unsupported_keywords(item, found)
    return found


def _is_type(value: Any, name: str) -> bool:
    if name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if name == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return isinstance(value, _TYPES[name])


class Validator:
    def __init__(self, root: dict[str, Any], schema_dir: Path = SCHEMA_DIR) -> None:
        self.root = root
        self.schema_dir = schema_dir

    def _resolve(self, ref: str) -> tuple[dict[str, Any], dict[str, Any]]:
        if ref.startswith("#/"):
            node: Any = self.root
            for part in ref[2:].split("/"):
                node = node[part]
            return node, self.root
        name = ref.rsplit("/", 1)[-1]
        other = load_schema(self.schema_dir / name)
        return other, other

    def errors(self, value: Any, schema: dict[str, Any] | bool = None, path: str = "$") -> list[str]:  # type: ignore[assignment]
        schema = self.root if schema is None else schema
        if schema is True:
            return []
        if schema is False:
            return [f"{path}: schema forbids any value"]
        out: list[str] = []
        if "$ref" in schema:
            target, root = self._resolve(schema["$ref"])
            out.extend(Validator(root, self.schema_dir).errors(value, target, path))
        if "type" in schema:
            types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
            if not any(_is_type(value, t) for t in types):
                return out + [f"{path}: expected {types}, got {type(value).__name__}"]
        if "const" in schema and value != schema["const"]:
            out.append(f"{path}: expected const {schema['const']!r}")
        if "enum" in schema and value not in schema["enum"]:
            out.append(f"{path}: {value!r} not in {schema['enum']}")
        if isinstance(value, str):
            if "minLength" in schema and len(value) < schema["minLength"]:
                out.append(f"{path}: shorter than {schema['minLength']}")
            if "maxLength" in schema and len(value) > schema["maxLength"]:
                out.append(f"{path}: longer than {schema['maxLength']}")
            if "pattern" in schema and not re.search(schema["pattern"], value):
                out.append(f"{path}: does not match {schema['pattern']}")
        if isinstance(value, (int, float)) and not isinstance(value, bool) and "minimum" in schema and value < schema["minimum"]:
            out.append(f"{path}: below minimum {schema['minimum']}")
        if isinstance(value, dict):
            for key in schema.get("required", []):
                if key not in value:
                    out.append(f"{path}: missing required {key!r}")
            if "minProperties" in schema and len(value) < schema["minProperties"]:
                out.append(f"{path}: fewer than {schema['minProperties']} properties")
            props = schema.get("properties", {})
            for key, item in value.items():
                if key in props:
                    out.extend(self.errors(item, props[key], f"{path}.{key}"))
                elif "additionalProperties" in schema:
                    extra = schema["additionalProperties"]
                    if extra is False:
                        out.append(f"{path}: unexpected property {key!r}")
                    elif isinstance(extra, dict):
                        out.extend(self.errors(item, extra, f"{path}.{key}"))
        if isinstance(value, list):
            if "minItems" in schema and len(value) < schema["minItems"]:
                out.append(f"{path}: fewer than {schema['minItems']} items")
            if "items" in schema:
                for index, item in enumerate(value):
                    out.extend(self.errors(item, schema["items"], f"{path}[{index}]"))
        if "anyOf" in schema and all(self.errors(value, option, path) for option in schema["anyOf"]):
            out.append(f"{path}: matches no anyOf option")
        for option in schema.get("allOf", []):
            out.extend(self.errors(value, option, path))
        if "if" in schema and not self.errors(value, schema["if"], path) and "then" in schema:
            out.extend(self.errors(value, schema["then"], path))
        return out


def validate(schema_path: Path, instance: Any) -> list[str]:
    schema = load_schema(schema_path)
    unsupported = unsupported_keywords(schema)
    if unsupported:
        return [f"schema uses unsupported keywords: {sorted(unsupported)}"]
    return Validator(schema, schema_path.parent).errors(instance)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python -m hostproto.validate SCHEMA INSTANCE", file=sys.stderr)
        return 64
    errors = validate(Path(argv[0]), json.loads(Path(argv[1]).read_text(encoding="utf-8")))
    for error in errors:
        print(error)
    print("valid" if not errors else f"{len(errors)} error(s)")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
