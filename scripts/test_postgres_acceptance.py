"""Harness safety mocks only; these tests do not prove PostgreSQL execution."""

import json
import os
import unittest
from unittest.mock import patch

from postgres_acceptance import IMAGE, main


class PostgresHarnessSafetyTests(unittest.TestCase):
    def setUp(self):
        # Mock-only tests must never write fabricated runtime evidence.
        writer = patch("postgres_acceptance.Path.write_text")
        self.writer = writer.start()
        self.addCleanup(writer.stop)
        directory = patch("postgres_acceptance.Path.mkdir")
        directory.start()
        self.addCleanup(directory.stop)

    @patch("postgres_acceptance.docker", return_value="invalid-container")
    def test_invalid_identity_cannot_trigger_cleanup(self, command):
        with self.assertRaisesRegex(RuntimeError, "owned container"):
            main()
        self.assertEqual(command.call_count, 1)
        self.assertEqual(json.loads(self.writer.call_args.args[0])["status"], "FAIL")

    @patch("postgres_acceptance.docker")
    def test_public_port_is_rejected_and_only_owned_container_removed(self, command):
        identity = "a" * 64
        command.side_effect = [identity, "0.0.0.0:5432", ""]
        with self.assertRaisesRegex(RuntimeError, "loopback"):
            main()
        self.assertEqual(command.call_args.args, ("rm", "-f", identity))
        run = command.call_args_list[0]
        self.assertIn("127.0.0.1::5432", run.args)
        self.assertIn(IMAGE, run.args)
        self.assertNotIn(run.kwargs["environment"]["POSTGRES_PASSWORD"], run.args)
        self.assertNotIn("POSTGRES_HOST_AUTH_METHOD=trust", run.args)

    @patch("postgres_acceptance.time.sleep")
    @patch("postgres_acceptance.docker")
    def test_readiness_failure_is_bounded_and_preserves_other_containers(
        self, command, wait
    ):
        identity = "b" * 64

        def execute(*arguments, **kwargs):
            if arguments[0] == "run":
                return identity
            if arguments[0] == "port":
                return "127.0.0.1:12345"
            if arguments[0] == "rm":
                return ""
            raise RuntimeError("synthetic-unavailable")

        command.side_effect = execute
        with self.assertRaisesRegex(RuntimeError, "become ready"):
            main()
        self.assertEqual(wait.call_count, 50)
        self.assertEqual(command.call_args.args, ("rm", "-f", identity))

    @patch("builtins.print")
    @patch("postgres_acceptance.Path.write_text")
    @patch("postgres_acceptance.Path.mkdir")
    @patch("postgres_acceptance.verify_recovery")
    @patch(
        "postgres_acceptance.run_backend_tests", return_value="synthetic test output"
    )
    @patch("postgres_acceptance.docker")
    def test_owned_database_never_uses_external_database_url(
        self, command, tests, recovery, mkdir, write, output
    ):
        identity = "c" * 64
        command.side_effect = [identity, "127.0.0.1:12345", "", ""]
        with patch.dict(os.environ, {"DATABASE_URL": "do-not-use-existing-database"}):
            main()
        url, container, password = tests.call_args.args
        self.assertIn("@127.0.0.1:12345/ai_ci_", url)
        self.assertNotIn("do-not-use-existing-database", url)
        self.assertEqual(container, identity)
        self.assertTrue(password)
        self.assertIn("--tmpfs", command.call_args_list[0].args)
        self.assertEqual(command.call_args.args, ("rm", "-f", identity))
        written = write.call_args.args[0]
        self.assertNotIn(password, written)
        self.assertNotIn(url, written)
        recovery.assert_called_once()
