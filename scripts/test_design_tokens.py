"""Source-level token checks, separate from DOM/visual tests. REQ: UI-TOKENS."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DesignTokenTests(unittest.TestCase):
    def test_editor_defaults_preserve_utf8_python_and_frontend_conventions(self):
        config = (ROOT / ".editorconfig").read_text(encoding="utf-8")
        for expected in (
            "root = true",
            "charset = utf-8",
            "end_of_line = lf",
            "insert_final_newline = true",
            "trim_trailing_whitespace = true",
            "[*.py]\nindent_size = 4",
            "json,yml,yaml,css,html,md",
            "[Makefile]\nindent_style = tab",
        ):
            self.assertIn(expected, config)

    def test_arabic_shell_keeps_identifiers_ltr_and_theme_provisional(self):
        html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
        page = (ROOT / "frontend/src/pages/AnalysisPage.tsx").read_text(
            encoding="utf-8"
        )
        styles = (ROOT / "frontend/src/styles.css").read_text(encoding="utf-8")
        self.assertIn('<html lang="ar" dir="rtl">', html)
        self.assertIn('dir="ltr"', page)
        self.assertIn("margin-inline-start", styles)
        self.assertIn("padding-inline-start", styles)
        self.assertNotIn('name="theme-color"', html)

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
