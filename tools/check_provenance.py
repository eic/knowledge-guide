#!/usr/bin/env python3
"""Every page under docs/ states where it came from: source, source_commit, generated, status.

status is draft (generated, not yet checked by a person) or reviewed (then reviewed_by and
reviewed are required). Index pages, which only hold navigation, are exempt.
"""
import re
import sys
from pathlib import Path

REQUIRED = ("source", "source_commit", "generated", "status")
STATUSES = ("draft", "reviewed")


def front_matter(page: Path) -> dict:
    text = page.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    head = text.split("---\n", 2)[1]
    return dict(re.findall(r"^(\w+):\s*(.+?)\s*$", head, re.M))


def problems(page: Path, fields: dict) -> list[str]:
    found = [f"{key} missing" for key in REQUIRED if key not in fields]
    if "source_commit" in fields and not re.fullmatch(r"[0-9a-f]{40}", fields["source_commit"]):
        found.append("source_commit is not a full 40-character sha")
    if "generated" in fields and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fields["generated"]):
        found.append("generated is not a YYYY-MM-DD date")
    status = fields.get("status")
    if status is not None and status not in STATUSES:
        found.append(f"status must be one of {', '.join(STATUSES)}")
    if status == "reviewed":
        found += [f"{key} missing for a reviewed page" for key in ("reviewed_by", "reviewed") if key not in fields]
    return found


def main() -> int:
    failures = 0
    for page in sorted(Path("docs").rglob("*.md")):
        if page.name == "index.md":
            continue
        for problem in problems(page, front_matter(page)):
            print(f"{page}: {problem}")
            failures += 1
    print(f"{failures} problem(s)" if failures else "every page states its provenance")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
