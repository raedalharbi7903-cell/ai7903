import io
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from smoke_container import main


class ContainerSafetyTests(unittest.TestCase):
    def test_packaged_command_disables_raw_access_logging(self):
        dockerfile = Path(__file__).resolve().parents[1] / "backend" / "Dockerfile"
        command = next(
            line.removeprefix("CMD ")
            for line in dockerfile.read_text(encoding="utf-8").splitlines()
            if line.startswith("CMD ")
        )
        arguments = json.loads(command)
        self.assertIn("--no-access-log", arguments)
        self.assertNotIn("--access-log", arguments)

    @patch("smoke_container.docker", return_value="untrusted-identity")
    def test_invalid_identity_never_triggers_broad_cleanup(self, command):
        with self.assertRaisesRegex(RuntimeError, "identity"):
            main()
        self.assertEqual(command.call_count, 1)

    @patch("smoke_container.docker")
    def test_non_loopback_mapping_fails_and_cleans_only_owned_container(self, command):
        identity = "a" * 64
        command.side_effect = [identity, "0.0.0.0:8000", ""]
        with self.assertRaisesRegex(RuntimeError, "loopback"):
            main()
        self.assertEqual(command.call_args.args, ("rm", "-f", identity))

    @patch("smoke_container.urlopen")
    @patch("smoke_container.docker")
    def test_root_runtime_fails_and_owned_container_is_removed(self, command, request):
        identity = "b" * 64
        command.side_effect = [identity, "127.0.0.1:12345", "0", ""]
        request.return_value = io.StringIO('{"status":"healthy"}')
        with self.assertRaisesRegex(RuntimeError, "root"):
            main()
        self.assertEqual(command.call_args.args, ("rm", "-f", identity))


if __name__ == "__main__":
    unittest.main()
