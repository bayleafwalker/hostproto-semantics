"""Write every canonical schema's bundled form to `bundled/`.

Adapters consume these files at a pinned commit and verify their digests;
they never re-bundle or copy the canonical schemas. `tests` fail if a
bundled file is stale relative to its canonical source.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from .bundle import bundle
from .validate import SCHEMA_DIR

BUNDLED_DIR = SCHEMA_DIR.parent / "bundled"


def render(name: str) -> str:
    return json.dumps(bundle(SCHEMA_DIR / f"{name}.schema.json"), indent=2, sort_keys=True) + "\n"


def emit() -> dict[str, str]:
    BUNDLED_DIR.mkdir(exist_ok=True)
    digests: dict[str, str] = {}
    for path in sorted(SCHEMA_DIR.glob("*.schema.json")):
        name = path.name.replace(".schema.json", "")
        text = render(name)
        (BUNDLED_DIR / f"{name}.json").write_text(text, encoding="utf-8")
        digests[name] = hashlib.sha256(text.encode("utf-8")).hexdigest()
    (BUNDLED_DIR / "SHA256SUMS").write_text(
        "".join(f"{digest}  {name}.json\n" for name, digest in digests.items()), encoding="utf-8"
    )
    return digests


if __name__ == "__main__":
    for name, digest in emit().items():
        print(f"{digest}  {name}.json")
    sys.exit(0)
