"""Shared helpers for the page generators (gen_documents, gen_examples, gen_api).

Generated pages are committed like hand-written ones; the generators are run
by maintainers when the source data changes. Every generated page carries
`generated: tools/<generator>.py` in its front matter so nobody edits it by hand.
"""
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
LANGS = ("zh", "en")
GITHUB_REPO = "https://github.com/INTELPRO-INC/IPRO-SDK"


class _AnyTagLoader(yaml.SafeLoader):
    """Read mkdocs*.yml files, which carry !!python/name and !ENV tags."""


_AnyTagLoader.add_multi_constructor("", lambda loader, suffix, node: None)
_AnyTagLoader.add_multi_constructor("tag:yaml.org,2002:python/", lambda loader, suffix, node: None)


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def release() -> dict[str, str]:
    """extra.release from mkdocs.base.yml (single source of the SDK version)."""
    data = yaml.load((ROOT / "mkdocs.base.yml").read_text(encoding="utf-8"), Loader=_AnyTagLoader)
    return data["extra"]["release"]


def release_tag() -> str:
    return f"IPRO-SDK-{release()['sdk']}"


def github_url(path: str, kind: str = "tree") -> str:
    """Link to a path in the SDK repository at the documented release tag."""
    return f"{GITHUB_REPO}/{kind}/{release_tag()}/{path.strip('/')}"


def front_matter(meta: dict[str, Any]) -> str:
    body = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False, width=1000)
    return f"---\n{body}---\n"


def write_page(lang: str, rel: str, meta: dict[str, Any], body: str) -> Path:
    path = DOCS / lang / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    text = front_matter(meta) + "\n" + body.strip() + "\n"
    path.write_text(text, encoding="utf-8")
    return path


def table(headers: list[str], rows: Iterable[list[str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines += ["| " + " | ".join(cell_text(c) for c in row) + " |" for row in rows]
    return "\n".join(lines)


def cell_text(text: str) -> str:
    """Make text safe inside a Markdown table cell."""
    return re.sub(r"\s*\n\s*", " ", text).replace("|", "\\|").strip()


def replace_block(text: str, name: str, content: str, comment: tuple[str, str]) -> str:
    """Replace the lines between BEGIN/END markers named `name`.

    `comment` gives the marker syntax, e.g. ("# ", "") for YAML or
    ("<!-- ", " -->") for Markdown. Markers must already exist.
    """
    start, end = comment
    pattern = re.compile(
        rf"(?P<head>^(?P<indent>[ \t]*){re.escape(start)}BEGIN generated: {re.escape(name)}{re.escape(end)}\n)"
        rf".*?"
        rf"(?P<tail>^[ \t]*{re.escape(start)}END generated: {re.escape(name)}{re.escape(end)}$)",
        re.S | re.M,
    )
    match = pattern.search(text)
    if not match:
        raise KeyError(f"markers for generated block '{name}' not found")
    body = content.rstrip("\n") + "\n" if content.strip() else ""
    return text[: match.start()] + match.group("head") + body + match.group("tail") + text[match.end():]


NavEntry = tuple[str, "str | list[NavEntry]"]


def nav_lines(entries: list[NavEntry], indent: str) -> list[str]:
    """YAML nav lines: (title, file) or (title, [children]) entries."""
    lines = []
    for title, target in entries:
        if isinstance(target, str):
            lines.append(f'{indent}- "{title}": {target}')
        else:
            lines.append(f'{indent}- "{title}":')
            lines += nav_lines(target, indent + "    ")
    return lines


def update_nav(name: str, entries: dict[str, list[NavEntry]]) -> None:
    """Rewrite the generated nav block `name` in mkdocs.<lang>.yml.

    entries[lang] lists the same files in the same order for both languages;
    the block's indentation comes from its BEGIN marker.
    """
    for lang in LANGS:
        path = ROOT / f"mkdocs.{lang}.yml"
        text = path.read_text(encoding="utf-8")
        marker = re.search(rf"^([ \t]*)# BEGIN generated: {re.escape(name)}$", text, re.M)
        if not marker:
            raise KeyError(f"nav markers '{name}' missing in {path.name}")
        lines = nav_lines(entries[lang], marker.group(1))
        path.write_text(replace_block(text, name, "\n".join(lines), ("# ", "")), encoding="utf-8")


def redline_errors(pages: dict[str, dict[str, str]], rules: list) -> list[str]:
    """Red-line errors in rendered pages ({lang: {rel path: text}}), checked in place.

    Each page is written to a temporary file directly under docs/<lang>/ so the
    language-scoped rules apply, then removed. Private matches stay redacted.
    """
    import redline_check

    errors = []
    for lang, files in pages.items():
        for rel, text in files.items():
            path = DOCS / lang / f"_check_{Path(rel).name}"
            path.write_text(text, encoding="utf-8")
            try:
                errors += [redline_check.format_finding(f, False).replace(path.name, rel)
                           for f in redline_check.scan_file(path, rules) if f.rule.severity == "error"]
            finally:
                path.unlink()
    return errors
