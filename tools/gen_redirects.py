#!/usr/bin/env python3
"""Write redirect pages for the old Jekyll URLs into the built site.

Runs after both languages are built (tools/build.sh calls it). For every page
in data/redirects.yml it writes <page>.html into site/ and site/en/, which is
where the old site served /<page> and /en/<page>. Each redirect page sends an
old section anchor (#id) to its new home with a small script, and falls back
to a meta refresh to the page target when scripts are off.

Before writing anything it checks that every old page has an entry, every
anchor names a section of the old page, every target page is built and every
explicit target anchor exists, and that no redirect would replace a built
page (its own earlier output is replaced). Any problem is an error and
nothing is written.

Usage: tools/gen_redirects.py [--site DIR]
"""
import argparse
import html
import json
import re
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

from gen_common import DOCS, LANGS, ROOT, load_yaml, mkdocs_config

DATA = ROOT / "data" / "redirects.yml"
GENERATOR = "tools/gen_redirects.py"
LEGACY = ROOT / "legacy"
SECTION_ID = re.compile(r'<section id="([^"]+)"')
LABELS = {
    "zh": {"lang": "zh-TW", "moved": "這一頁已經搬到"},
    "en": {"lang": "en", "moved": "This page has moved to"},
}

# Returns the HTML of a built page (by URL path relative to the language root), or None.
PageReader = Callable[[str], "str | None"]


@dataclass(frozen=True)
class Redirect:
    """One old page in one language: its default target and its anchor map."""
    page: str
    default: str
    anchors: dict[str, str]
    title: str


def page_url(target: str) -> tuple[str, str]:
    """('guides/ble.md#x') -> ('guides/ble/', 'x'); index.md maps to its directory."""
    path, _, anchor = target.partition("#")
    if not path.endswith(".md"):
        raise ValueError(f"target must name a .md page: {target}")
    stem = path[:-3]
    if stem == "index":
        url = ""
    elif stem.endswith("/index"):
        url = stem[: -len("index")]
    else:
        url = stem + "/"
    return url, anchor


def has_id(page_html: str, anchor: str) -> bool:
    return re.search(rf'\bid="{re.escape(anchor)}"', page_html) is not None


def legacy_sections() -> dict[str, list[str]]:
    """{old page name: [section ids]} from legacy/*.html, without the home page."""
    if not LEGACY.is_dir():
        return {}
    return {p.stem: SECTION_ID.findall(p.read_text(encoding="utf-8"))
            for p in sorted(LEGACY.glob("*.html")) if p.stem != "index"}


def page_title(lang: str, target: str) -> str:
    path = DOCS / lang / target.partition("#")[0]
    text = path.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        meta = yaml.safe_load(text[4:text.find("\n---\n", 4)]) or {}
        if meta.get("title"):
            return str(meta["title"])
    heading = re.search(r"^# (.+)$", text, re.M)
    return heading.group(1).strip() if heading else path.stem


def validate(data: dict[str, Any], sections: dict[str, list[str]], read: PageReader) -> list[str]:
    """Problems with the redirect table against the old pages and one built language."""
    pages = data.get("pages") or {}
    errors = []
    if sections:
        errors += [f"{name}: old page has no redirect entry" for name in sorted(set(sections) - set(pages))]
        errors += [f"{name}: no such page in legacy/" for name in sorted(set(pages) - set(sections))]
    for name, entry in pages.items():
        targets = [("to", entry.get("to") or "")]
        for old_id, target in (entry.get("anchors") or {}).items():
            if sections and name in sections and old_id not in sections[name]:
                errors.append(f"{name}#{old_id}: the old page has no such section")
            targets.append((f"#{old_id}", target))
        for label, target in targets:
            try:
                url, anchor = page_url(target)
            except ValueError as exc:
                errors.append(f"{name} {label}: {exc}")
                continue
            built = read(url)
            if built is None:
                errors.append(f"{name} {label}: {target} is not a built page")
            elif anchor and not has_id(built, anchor):
                errors.append(f"{name} {label}: {target} has no heading #{anchor}")
    return errors


def resolve(name: str, entry: dict[str, Any], old_ids: list[str], base: str, read: PageReader) -> tuple[str, dict[str, str]]:
    """The default URL and the {old id: URL} map for one old page."""
    default_url, default_anchor = page_url(entry["to"])
    default = base + default_url + (f"#{default_anchor}" if default_anchor else "")
    explicit = entry.get("anchors") or {}
    anchors = {}
    for old_id in dict.fromkeys(list(old_ids) + list(explicit)):
        target = explicit.get(old_id, entry["to"])
        url, anchor = page_url(target)
        if "#" not in target and has_id(read(url) or "", old_id):
            anchor = old_id
        resolved = base + url + (f"#{anchor}" if anchor else "")
        if resolved != default:
            anchors[old_id] = resolved
    return default, anchors


def render(redirect: Redirect, lang: str, origin: str) -> str:
    labels = LABELS[lang]
    default = html.escape(redirect.default, quote=True)
    title = html.escape(redirect.title)
    script_map = json.dumps(redirect.anchors, ensure_ascii=False, sort_keys=True).replace("</", "<\\/")
    script_default = json.dumps(redirect.default).replace("</", "<\\/")
    return "\n".join([
        "<!doctype html>",
        f'<html lang="{labels["lang"]}">',
        "<head>",
        '<meta charset="utf-8">',
        f"<title>{title} - IPRO SDK</title>",
        f'<meta name="generator" content="{GENERATOR}">',
        '<meta name="robots" content="noindex">',
        f'<link rel="canonical" href="{html.escape(origin + redirect.default, quote=True)}">',
        "<script>(function () {",
        f"  var anchors = {script_map};",
        "  var id = location.hash.slice(1);",
        "  try { id = decodeURIComponent(id); } catch (e) {}",
        f"  location.replace(anchors[id] || {script_default});",
        "})();</script>",
        f'<meta http-equiv="refresh" content="0; url={default}">',
        "</head>",
        "<body>",
        f'<p>{labels["moved"]} <a href="{default}">{title}</a></p>',
        "</body>",
        "</html>",
        "",
    ])


def site_reader(site_dir: Path) -> PageReader:
    def read(url: str) -> "str | None":
        path = site_dir / url / "index.html"
        return path.read_text(encoding="utf-8") if path.is_file() else None
    return read


def build(data: dict[str, Any], sections: dict[str, list[str]], site: Path) -> tuple[dict[Path, str], list[str]]:
    """{output path: page text} for both languages, or the problems that stop it."""
    outputs: dict[Path, str] = {}
    errors: list[str] = []
    for lang in LANGS:
        config = mkdocs_config(lang)
        site_url = urlparse(config["site_url"])
        site_dir = site / Path(config["site_dir"]).relative_to("site")
        read = site_reader(site_dir)
        errors += [f"[{lang}] {err}" for err in validate(data, sections, read)]
        if errors:
            continue
        for name, entry in data["pages"].items():
            out = site_dir / f"{name}.html"
            if out.exists() and GENERATOR not in out.read_text(encoding="utf-8"):
                errors.append(f"[{lang}] {name}: {out.relative_to(site)} is a built file; refusing to replace it")
                continue
            default, anchors = resolve(name, entry, sections.get(name, []), site_url.path, read)
            redirect = Redirect(name, default, anchors, page_title(lang, entry["to"]))
            outputs[out] = render(redirect, lang, f"{site_url.scheme}://{site_url.netloc}")
    return outputs, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--site", type=Path, default=ROOT / "site", help="built site (default: site/)")
    args = parser.parse_args(argv)
    if not (args.site / "index.html").is_file():
        print(f"gen_redirects: no built site at {args.site}; run the build first", file=sys.stderr)
        return 2
    outputs, errors = build(load_yaml(DATA), legacy_sections(), args.site)
    if errors:
        print("gen_redirects: fix data/redirects.yml:", file=sys.stderr)
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        return 1
    for path, text in outputs.items():
        path.write_text(text, encoding="utf-8")
    print(f"redirects: {len(outputs)} old URLs -> new pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
