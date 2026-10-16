#!/usr/bin/env python3
"""Report migration progress from the legacy Jekyll site (legacy/) to docs/.

Every new zh-TW page lists its legacy sources in front matter:
    migrate_from:  ["ble-development.html", "hardware.html#ipro6s", ...]
    not_migrated:  [...]        sections deliberately left behind
    status: stub                page not written yet

An entry without "#" covers the whole legacy page. The report lists the
remaining stubs and every legacy <section id> that no page claims.

  --fail-on-stubs      exit 1 while any stub remains (gate for main)
  --fail-on-uncovered  exit 1 while any legacy section is unclaimed
"""
import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs" / "zh"
LEGACY = ROOT / "legacy"
SECTION_ID = re.compile(r'<section id="([^"]+)"')


def front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return yaml.safe_load(text[4:end]) or {}
    return {}


def legacy_sections() -> dict[str, list[str]]:
    if not LEGACY.is_dir():
        return {}
    return {p.name: SECTION_ID.findall(p.read_text(encoding="utf-8"))
            for p in sorted(LEGACY.glob("*.html"))}


def claimed(entries: list[str]) -> tuple[set[str], set[str]]:
    """Split entries into whole pages and page#section references."""
    pages, sections = set(), set()
    for entry in entries:
        ref = entry.split()[0]
        if "#" in ref:
            sections.add(ref)
        else:
            pages.add(ref)
    return pages, sections


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--fail-on-stubs", action="store_true")
    parser.add_argument("--fail-on-uncovered", action="store_true")
    args = parser.parse_args(argv)

    stubs, entries = [], []
    for page in sorted(DOCS.rglob("*.md")):
        meta = front_matter(page)
        rel = page.relative_to(DOCS).as_posix()
        if meta.get("status") == "stub":
            stubs.append(rel)
        entries += [str(e) for e in (meta.get("migrate_from") or []) + (meta.get("not_migrated") or [])]

    whole, parts = claimed(entries)
    uncovered = [f"{page}#{sid}" for page, ids in legacy_sections().items() if page not in whole
                 for sid in ids if f"{page}#{sid}" not in parts]
    unmentioned = [page for page in legacy_sections()
                   if page not in whole and not any(p.startswith(page + "#") for p in parts)]

    total = len(list(DOCS.rglob("*.md")))
    print(f"stubs: {len(stubs)} of {total} pages still to migrate")
    for rel in stubs:
        print(f"  stub  {rel}")
    for ref in uncovered:
        print(f"  unclaimed legacy section  {ref}")
    for page in unmentioned:
        print(f"  unclaimed legacy page     {page}")

    failed = (args.fail_on_stubs and stubs) or (args.fail_on_uncovered and (uncovered or unmentioned))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
