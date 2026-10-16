#!/usr/bin/env python3
"""Check that the zh-TW and English sites mirror each other.

Fails when:
  * a page exists in one language only;
  * the two nav trees list different files or a different order;
  * a page pair has a different number of level-2 headings, or different
    explicit heading ids ({ #id }), which the language switch and old anchor
    links rely on;
  * one side of a pair is a stub and the other is not.

Usage: tools/parity_check.py            (run from anywhere in the repo)
"""
import re
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
LANGS = ("zh", "en")
FENCE = re.compile(r"^\s*(```|~~~)")
HEADING = re.compile(r"^(#{2,6})\s+(.*?)\s*$")
EXPLICIT_ID = re.compile(r"\{[^}]*#([\w-]+)[^}]*\}\s*$")


class _AnyTagLoader(yaml.SafeLoader):
    """Load config files that carry !ENV or !!python/name tags."""


_AnyTagLoader.add_multi_constructor("", lambda loader, suffix, node: None)
_AnyTagLoader.add_multi_constructor("tag:yaml.org,2002:python/", lambda loader, suffix, node: None)


def split_front_matter(text: str) -> tuple[dict[str, Any], str]:
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return yaml.safe_load(text[4:end]) or {}, text[end + 5:]
    return {}, text


def headings(body: str) -> tuple[int, list[str]]:
    """Return (level-2 count, explicit ids in order), ignoring fenced code."""
    in_fence = False
    h2 = 0
    ids = []
    for line in body.splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING.match(line)
        if not m:
            continue
        if len(m.group(1)) == 2:
            h2 += 1
        idm = EXPLICIT_ID.search(m.group(2))
        if idm:
            ids.append(idm.group(1))
    return h2, ids


def nav_files(config: str) -> list[str]:
    data = yaml.load((ROOT / config).read_text(encoding="utf-8"), Loader=_AnyTagLoader)

    def walk(items: Any) -> Iterator[str]:
        for item in items or []:
            if isinstance(item, str):
                yield item
            elif isinstance(item, dict):
                for value in item.values():
                    if isinstance(value, str):
                        yield value
                    else:
                        yield from walk(value)

    return list(walk(data.get("nav")))


def main() -> int:
    errors = []
    pages = {lang: {p.relative_to(ROOT / "docs" / lang).as_posix()
                    for p in (ROOT / "docs" / lang).rglob("*.md")} for lang in LANGS}
    for lang, other in (("zh", "en"), ("en", "zh")):
        for rel in sorted(pages[lang] - pages[other]):
            errors.append(f"docs/{lang}/{rel}: no {other} counterpart")

    nav = {lang: nav_files(f"mkdocs.{lang}.yml") for lang in LANGS}
    if nav["zh"] != nav["en"]:
        for i, (a, b) in enumerate(zip(nav["zh"], nav["en"])):
            if a != b:
                errors.append(f"nav differs at entry {i + 1}: zh={a} en={b}")
                break
        else:
            errors.append(f"nav length differs: zh={len(nav['zh'])} en={len(nav['en'])}")

    for rel in sorted(pages["zh"] & pages["en"]):
        meta = {}
        heads = {}
        for lang in LANGS:
            m, body = split_front_matter((ROOT / "docs" / lang / rel).read_text(encoding="utf-8"))
            meta[lang] = m
            heads[lang] = headings(body)
        (zh_h2, zh_ids), (en_h2, en_ids) = heads["zh"], heads["en"]
        if zh_h2 != en_h2:
            errors.append(f"{rel}: level-2 headings zh={zh_h2} en={en_h2}")
        if zh_ids != en_ids:
            missing = sorted(set(zh_ids) ^ set(en_ids))
            detail = f"only on one side: {', '.join(missing)}" if missing else "same ids, different order"
            errors.append(f"{rel}: heading ids differ ({detail})")
        if meta["zh"].get("status") != meta["en"].get("status"):
            errors.append(f"{rel}: status zh={meta['zh'].get('status')} en={meta['en'].get('status')}")

    for err in errors:
        print(f"parity: {err}")
    print(f"parity: {len(pages['zh'])} page pairs, {len(nav['zh'])} nav entries, {len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
