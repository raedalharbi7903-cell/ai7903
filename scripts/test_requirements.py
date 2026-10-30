"""Requirement baseline integrity, not product-completion certification."""

import json
import re
import unittest
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "docs/02-product/canonical-requirements.json"


def unique_object(pairs):
    """Never silently discard traceability through duplicate JSON keys."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate requirement-register key: {key}")
        result[key] = value
    return result


class RequirementRegisterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.register = json.loads(
            REGISTER.read_text(encoding="utf-8"), object_pairs_hook=unique_object
        )
        cls.records = cls.register["requirements"]

    def test_duplicate_json_keys_cannot_hide_requirement_evidence(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            json.loads(
                '{"references": {"path": ["A"], "path": ["B"]}}',
                object_pairs_hook=unique_object,
            )

    def test_unique_records_cover_all_source_sections_and_known_components(self):
        identifiers = [record["id"] for record in self.records]
        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertTrue(
            {f"MASTER-{number:02}" for number in range(1, 32)} <= set(identifiers)
        )
        self.assertTrue(
            {f"AN-C{number:02}" for number in range(1, 25)} <= set(identifiers)
        )
        self.assertTrue(
            {f"AN-X{number:02}" for number in range(1, 5)} <= set(identifiers)
        )
        source = (ROOT / self.register["source"]).read_text(encoding="utf-8")
        sections = re.findall(r"^# (\d+)\. ", source, re.MULTILINE)
        self.assertEqual(sections, [str(number) for number in range(1, 32)])

    def test_every_requirement_has_scope_evidence_status_and_dependencies(self):
        fields = {
            "id",
            "description",
            "approval_status",
            "implementation_status",
            "source",
            "acceptance_criteria",
            "code_references",
            "test_references",
            "dependencies",
            "external_blockers",
            "remaining_work",
        }
        for record in self.records:
            self.assertFalse(fields - record.keys(), record["id"])
            for path in record["code_references"] + record["test_references"]:
                target = (ROOT / path).resolve()
                self.assertTrue(target.is_relative_to(ROOT.resolve()), path)
                self.assertTrue(target.is_file(), path)
            if "parent" in record:
                self.assertIn(record["parent"], {item["id"] for item in self.records})

    def test_reverse_traceability_is_exact(self):
        reverse = defaultdict(set)
        for record in self.records:
            for path in record["code_references"] + record["test_references"]:
                reverse[path].add(record["id"])
        self.assertEqual(
            dict(reverse),
            {
                path: set(ids)
                for path, ids in self.register["reverse_references"].items()
            },
        )

    def test_customer_and_command_scope_not_silently_omitted(self):
        customers = [
            item for item in self.records if item["id"].startswith("CUSTOMER-")
        ]
        command = [item for item in self.records if item["id"].startswith("COMMAND-")]
        self.assertEqual(len(customers), 23)
        self.assertEqual(len(command), 11)
        self.assertEqual(command[-1]["description"], "Board Meeting")
        for item in customers + command:
            if item["implementation_status"] == "VERIFIED COMPLETE":
                self.assertTrue(item["code_references"], item["id"])
                self.assertTrue(item["test_references"], item["id"])
                self.assertTrue(item.get("visual_approval_reference"), item["id"])
