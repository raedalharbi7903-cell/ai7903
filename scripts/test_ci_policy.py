"""Source policy checks, not a YAML parser or hosted action-runtime acceptance."""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CIPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = (ROOT / ".github/workflows/quality.yml").read_text(
            encoding="utf-8"
        )
        cls.baseline = json.loads(
            (ROOT / "docs/09-devops/ci-action-baseline.json").read_text(
                encoding="utf-8"
            )
        )

    def test_every_action_is_a_reviewed_immutable_pin(self):
        source = re.findall(r"^\s*(?:- )?uses: (.+)$", self.workflow, re.MULTILINE)
        pins = []
        for entry in source:
            match = re.fullmatch(r"([^@\s]+)@([a-f0-9]{40})(?: # .*)?", entry)
            self.assertIsNotNone(match, entry)
            pins.append((match[1], match[2]))
        expected = [
            (item["repository"], item["commit"]) for item in self.baseline["actions"]
        ]
        self.assertCountEqual(pins, expected)
        self.assertEqual(len(pins), 5)
        for item in self.baseline["actions"]:
            self.assertEqual(item["runtime"], "node24")
            self.assertEqual(
                item["source_url"],
                f"https://raw.githubusercontent.com/{item['repository']}/{item['commit']}/action.yml",
            )
            self.assertTrue(
                item["release_url"].startswith(
                    "https://github.com/" + item["repository"] + "/releases/tag/"
                )
            )

    def test_no_write_tokens_or_persisted_credentials(self):
        block = re.search(r"(?ms)^permissions:\n(.*?)(?=^\S)", self.workflow)
        self.assertIsNotNone(block)
        self.assertEqual(block[1].strip(), "contents: read")
        self.assertIn("persist-credentials: false", self.workflow)
        for forbidden in (
            "persist-credentials: true",
            "pull_request_target",
            "secrets: inherit",
            "id-token:",
        ):
            self.assertNotIn(forbidden, self.workflow)
        self.assertIn("branches: [feature/crypto-analysis-validation]", self.workflow)

    def test_application_tools_and_cache_policy_are_preserved(self):
        for setting in (
            'python-version: "3.12"',
            'node-version: "24.14.0"',
            'version: "11.25.0"',
            "package_json_file: frontend/package.json",
            "package-manager-cache: false",
            "cache: false",
        ):
            self.assertIn(setting, self.workflow)

    def test_runtime_and_evidence_acceptance_remain_required(self):
        for command in (
            "scripts/verify.py",
            "scripts/postgres_acceptance.py",
            "scripts/smoke_container.py",
            "docker build -t ai-analysis-backend:ci backend",
        ):
            self.assertIn(command, self.workflow)
        for setting in (
            "include-hidden-files: true",
            "archive: true",
            "retention-days: 14",
            "if-no-files-found: error",
        ):
            self.assertIn(setting, self.workflow)
