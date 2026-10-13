#!/usr/bin/env python3
"""List the pages whose cited source files changed since the commit the page was generated from.

For each page: the source repository and commit from its front matter, and the files it links
to under github.com/<source>/blob/. The GitHub compare API gives the files changed between
that commit and the repository's default branch; a page is stale when one of its cited files
is among them. Output is Markdown, one line per stale page, for the weekly issue.
"""
import json
import os
import re
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path


def github(path: str) -> dict:
    request = urllib.request.Request(f"https://api.github.com{path}", headers={"User-Agent": "knowledge-guide"})
    if token := os.getenv("GITHUB_TOKEN"):
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def front_matter(page: Path) -> dict:
    text = page.read_text(encoding="utf-8")
    return dict(re.findall(r"^(\w+):\s*(.+?)\s*$", text.split("---\n", 2)[1], re.M)) if text.startswith("---\n") else {}


def cited_files(page: Path, source: str) -> set[str]:
    text = page.read_text(encoding="utf-8")
    return set(re.findall(rf"github\.com/{re.escape(source)}/blob/[^/]+/([^)#\s]+)", text))


def main() -> int:
    changed_since: dict[tuple[str, str], set[str]] = {}
    pages_by_source: dict[str, list[tuple[Path, dict]]] = defaultdict(list)
    for page in sorted(Path("docs").rglob("*.md")):
        fields = front_matter(page)
        if "source" in fields and "source_commit" in fields:
            pages_by_source[fields["source"]].append((page, fields))
    stale = []
    for source, pages in pages_by_source.items():
        default_branch = github(f"/repos/{source}")["default_branch"]
        head = github(f"/repos/{source}/commits/{default_branch}")["sha"]
        for page, fields in pages:
            key = (source, fields["source_commit"])
            if key not in changed_since:
                compare = github(f"/repos/{source}/compare/{fields['source_commit']}...{head}")
                changed_since[key] = {entry["filename"] for entry in compare.get("files", [])}
            hits = sorted(cited_files(page, source) & changed_since[key])
            if hits:
                stale.append(f"- `{page}` cites {len(hits)} changed file(s) in {source} since `{fields['source_commit'][:7]}`: " + ", ".join(f"`{hit}`" for hit in hits[:5]) + (" …" if len(hits) > 5 else ""))
    print(f"Checked against the default branches on {os.popen('date -u +%Y-%m-%d').read().strip()}.\n")
    print("\n".join(stale) if stale else "Every page cites the current source.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
