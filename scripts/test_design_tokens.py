"""Source-level token checks, separate from DOM/visual tests. REQ: UI-TOKENS."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DesignTokenTests(unittest.TestCase):
    def test_every_color_and_typography_reference_resolves(self):
        styles = (ROOT / "frontend/src/styles.css").read_text(encoding="utf-8")
        tokens = (ROOT / "frontend/src/styles/tokens.css").read_text(encoding="utf-8")
        definitions = dict(re.findall(r"(--[\w-]+):\s*([^;]+);", tokens))
        references = re.findall(r"var\((--[\w-]+)\)", styles)
        self.assertGreater(len(references), 45)
        self.assertFalse(set(references) - definitions.keys())
        self.assertIsNone(re.search(r"#[a-fA-F0-9]{3,8}\b", styles))
        self.assertIn('@import "./styles/tokens.css"', styles)

    def test_current_demo_defaults_are_explicitly_provisional(self):
        tokens = (ROOT / "frontend/src/styles/tokens.css").read_text(encoding="utf-8")
        self.assertIn("NOT founder-approved", tokens)
        self.assertIn("--ui-color-surface-canvas: #0b1018", tokens)
        self.assertIn("--ui-color-surface-action: #99e3cf", tokens)
        self.assertIn("--ui-color-scheme: dark", tokens)
        self.assertIn(
            "--ui-font-family: Inter, ui-sans-serif, system-ui, sans-serif", tokens
        )
