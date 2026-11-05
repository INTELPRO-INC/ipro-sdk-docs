#!/usr/bin/env python3
"""Check that every language mirrors the zh-TW site (the reference language).

Each of en, zh-cn and ja is compared with zh. Fails when:
  * a page exists in one language only;
  * two nav trees list different files or a different order;
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
REFERENCE = "zh"
LANGS = ("zh", "en", "zh-cn", "ja")
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


def compare(lang: str, pages: dict[str, set[str]], nav: dict[str, list[str]]) -> list[str]:
    """Problems between the reference language and `lang`."""
    ref = REFERENCE
    errors = []
    for a, b in ((ref, lang), (lang, ref)):
        for rel in sorted(pages[a] - pages[b]):
            errors.append(f"docs/{a}/{rel}: no {b} counterpart")

    if nav[ref] != nav[lang]:
        for i, (a, b) in enumerate(zip(nav[ref], nav[lang])):
            if a != b:
                errors.append(f"nav differs at entry {i + 1}: {ref}={a} {lang}={b}")
                break
        else:
            errors.append(f"nav length differs: {ref}={len(nav[ref])} {lang}={len(nav[lang])}")

    for rel in sorted(pages[ref] & pages[lang]):
        meta = {}
        heads = {}
        for side in (ref, lang):
            m, body = split_front_matter((ROOT / "docs" / side / rel).read_text(encoding="utf-8"))
            meta[side] = m
            heads[side] = headings(body)
        (ref_h2, ref_ids), (h2, ids) = heads[ref], heads[lang]
        if ref_h2 != h2:
            errors.append(f"{rel}: level-2 headings {ref}={ref_h2} {lang}={h2}")
        if ref_ids != ids:
            missing = sorted(set(ref_ids) ^ set(ids))
            detail = f"only on one side: {', '.join(missing)}" if missing else "same ids, different order"
            errors.append(f"{rel}: heading ids differ between {ref} and {lang} ({detail})")
        if meta[ref].get("status") != meta[lang].get("status"):
            errors.append(f"{rel}: status {ref}={meta[ref].get('status')} {lang}={meta[lang].get('status')}")
    return errors


def main() -> int:
    pages = {lang: {p.relative_to(ROOT / "docs" / lang).as_posix()
                    for p in (ROOT / "docs" / lang).rglob("*.md")} for lang in LANGS}
    nav = {lang: nav_files(f"mkdocs.{lang}.yml") for lang in LANGS}
    errors = [err for lang in LANGS if lang != REFERENCE for err in compare(lang, pages, nav)]
    for err in errors:
        print(f"parity: {err}")
    print(f"parity: {len(pages[REFERENCE])} pages x {len(LANGS)} languages, {len(nav[REFERENCE])} nav entries, "
          f"{len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
