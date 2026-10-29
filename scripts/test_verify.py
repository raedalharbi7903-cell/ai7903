"""Infrastructure tests for gate reporting; no server/dependencies required."""
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from verify import gates, run_gate


class VerificationTests(unittest.TestCase):
    def test_required_gates_are_unique_and_include_real_integration(self):
        configured = gates(Path("repository"), "python", "pnpm")
        names = [name for name, _, _ in configured]
        self.assertEqual(len(names), len(set(names)))
        self.assertIn("backend-import", names)
        self.assertIn("frontend-tests", names)
        self.assertIn("frontend-install", names)

    @patch("verify.subprocess.run")
    def test_failed_exit_cannot_be_reported_as_pass(self, execute):
        execute.return_value = subprocess.CompletedProcess(["test"], 1, "details", "failure")
        result = run_gate("test", Path("."), ["test"], {})
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["exit_code"], 1)
        self.assertIn("failure", result["output"])

    @patch("verify.subprocess.run", side_effect=FileNotFoundError("missing runtime"))
    def test_missing_tool_is_an_explicit_failure(self, execute):
        self.assertEqual(run_gate("test", Path("."), ["missing"], {})["status"], "FAIL")

    @patch("verify.subprocess.run", side_effect=subprocess.TimeoutExpired("test", 600))
    def test_timeout_is_an_explicit_failure(self, execute):
        self.assertEqual(run_gate("test", Path("."), ["test"], {})["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
