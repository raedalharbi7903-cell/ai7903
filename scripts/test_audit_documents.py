import tempfile
import unittest
from pathlib import Path

from audit_documents import audit


class DocumentationAuditTests(unittest.TestCase):
    def test_valid_external_anchor_and_encoded_links(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs").mkdir()
            (root / "docs" / "two words.md").write_text("# Target", encoding="utf-8")
            (root / "README.md").write_text(
                "[local](docs/two%20words.md) [web](https://example.com) [anchor](#x)",
                encoding="utf-8",
            )
            self.assertEqual(audit(root), [])

    def test_missing_links_fail_but_fenced_examples_do_not(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs").mkdir()
            (root / "README.md").write_text(
                "[missing](docs/missing.md)\n```text\n[example](example.md)\n```",
                encoding="utf-8",
            )
            issues = audit(root)
            self.assertEqual(len(issues), 1)
            self.assertEqual(issues[0]["line"], 1)

    def test_outside_repository_is_not_a_valid_document_target(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs").mkdir()
            (root / "README.md").write_text("[outside](../)", encoding="utf-8")
            self.assertEqual(len(audit(root)), 1)


if __name__ == "__main__":
    unittest.main()
