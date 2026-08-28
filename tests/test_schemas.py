from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from hostproto.validate import SCHEMA_DIR, load_schema, unsupported_keywords, validate

ROOT = SCHEMA_DIR.parent
EXAMPLES = ROOT / "examples"


def example(lane: str, name: str) -> dict:
    return json.loads((EXAMPLES / lane / f"{name}.json").read_text(encoding="utf-8"))


class SchemaTests(unittest.TestCase):
    def test_every_schema_uses_only_checked_keywords(self) -> None:
        for path in sorted(SCHEMA_DIR.glob("*.schema.json")):
            with self.subTest(schema=path.name):
                self.assertEqual(unsupported_keywords(load_schema(path)), set())

    def test_every_example_validates_against_its_schema(self) -> None:
        count = 0
        for lane in ("browser", "dap-sketch"):
            for path in sorted((EXAMPLES / lane).glob("*.json")):
                if path.name == "README.json":
                    continue
                schema = SCHEMA_DIR / f"{path.stem}.schema.json"
                with self.subTest(lane=lane, example=path.name):
                    self.assertTrue(schema.is_file(), f"no schema for {path.name}")
                    self.assertEqual(validate(schema, json.loads(path.read_text())), [])
                    count += 1
        self.assertGreaterEqual(count, 14)

    def test_the_same_schema_holds_browser_and_dap_instances(self) -> None:
        """Kill gate 1, at schema level: one envelope, two host classes."""
        for name in ("handles", "observation", "target-ref", "intent", "receipt", "error"):
            with self.subTest(name=name):
                for lane in ("browser", "dap-sketch"):
                    self.assertEqual(validate(SCHEMA_DIR / f"{name}.schema.json", example(lane, name)), [])

    def test_stale_target_error_must_not_claim_host_invocation(self) -> None:
        error = example("browser", "error")
        error["host_invoked"] = True
        self.assertTrue(validate(SCHEMA_DIR / "error.schema.json", error))

    def test_runtime_verification_requires_execution_count(self) -> None:
        profile = example("browser", "capability-profile")
        profile["capabilities"]["surface.navigate"].pop("runtime_executions")
        self.assertTrue(validate(SCHEMA_DIR / "capability-profile.schema.json", profile))

    def test_recovery_cannot_mint_approval(self) -> None:
        recovery = example("browser", "recovery")
        recovery["approval"] = {"granted": True}
        self.assertTrue(validate(SCHEMA_DIR / "recovery.schema.json", recovery))

    def test_evidence_refs_are_content_addressed(self) -> None:
        ref = example("browser", "evidence-ref")
        ref["ref"] = "file:///tmp/download.bin"
        self.assertTrue(validate(SCHEMA_DIR / "evidence-ref.schema.json", ref))

    def test_target_ref_declares_actions_and_revision(self) -> None:
        target = example("browser", "target-ref")
        for missing in ("revision", "actions"):
            broken = copy.deepcopy(target)
            broken.pop(missing)
            with self.subTest(missing=missing):
                self.assertTrue(validate(SCHEMA_DIR / "target-ref.schema.json", broken))

    def test_observation_loss_must_be_explicit(self) -> None:
        observation = example("browser", "observation")
        observation["bounded"].pop("lossy")
        self.assertTrue(validate(SCHEMA_DIR / "observation.schema.json", observation))

    def test_no_task_schema_exists(self) -> None:
        """Kill gate: a universal task type appearing here is the failure mode."""
        names = {path.stem.split(".")[0] for path in SCHEMA_DIR.glob("*.json")}
        self.assertFalse({"task", "job", "run", "transport", "discovery"} & names)


if __name__ == "__main__":
    unittest.main()
