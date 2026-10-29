"""Read-only local Markdown-link audit. Missing targets are failures, not waivers."""

import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

LINK = re.compile(r"!?\[[^\]]*\]\((<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)")


def audit(root: Path) -> list[dict[str, object]]:
    root = root.resolve()
    documents = sorted((root / "docs").rglob("*.md"))
    documents += sorted(root.glob("*.md"))
    frontend_readme = root / "frontend" / "README.md"
    if frontend_readme.exists():
        documents.append(frontend_readme)
    issues = []
    for source in documents:
        fenced = False
        for number, line in enumerate(
            source.read_text(encoding="utf-8").splitlines(), 1
        ):
            if line.lstrip().startswith(("```", "~~~")):
                fenced = not fenced
                continue
            if fenced:
                continue
            for match in LINK.finditer(line):
                href = match.group(1).strip("<>")
                parsed = urlsplit(href)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                target = (source.parent / unquote(parsed.path)).resolve()
                if not target.is_relative_to(root) or not target.exists():
                    issues.append(
                        {
                            "source": source.relative_to(root).as_posix(),
                            "line": number,
                            "target": href,
                            "reason": "missing_or_outside_repository",
                        }
                    )
    return issues


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    issues = audit(root)
    report = root / ".verification" / "documentation-audit.json"
    report.parent.mkdir(exist_ok=True)
    report.write_text(
        json.dumps(
            {"scope": "inline local Markdown file links", "issues": issues}, indent=2
        ),
        encoding="utf-8",
    )
    print(f"Documentation file links: {len(issues)} issues")
    for issue in issues:
        print(f"{issue['source']}:{issue['line']} -> {issue['target']}")
    return int(bool(issues))


if __name__ == "__main__":
    raise SystemExit(main())
