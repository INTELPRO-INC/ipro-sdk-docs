#!/usr/bin/env python3
"""Generate the examples pages from data/examples.yml and the app READMEs.

Writes, for both languages:
  * the catalog tables in examples/index.md (between `examples-<category>`
    markers; the prose around them stays hand-written);
  * examples/<app>.md for every app that ships a README (unless excluded),
    with the catalog data on top and the README below, converted by
    readme_md.py and the curation rules in data/examples.yml;
  * the `examples` nav block in mkdocs.<lang>.yml.
Generated pages must pass the red-line check, or nothing is written.

Usage: tools/gen_examples.py [--sdk PATH]
  --sdk  unpacked SDK release (default: $IPRO_SDK_RELEASE or ~/Works/IPRO-SDK-<version>)
"""
import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any

import readme_md
import redline_check
from gen_common import (DOCS, LANGS, ROOT, front_matter, github_url, load_yaml, redline_errors, release,
                        release_tag, replace_block, table, update_nav)

DATA = ROOT / "data" / "examples.yml"
INDEX = "examples/index.md"
GENERATOR = "tools/gen_examples.py"
RAW_BASE = "https://raw.githubusercontent.com/INTELPRO-INC/IPRO-SDK"
LABELS = {
    "zh": {"app": "應用", "purpose": "用途", "boards": "板卡與設定", "console": "主控台", "item": "項目",
           "content": "內容", "source": "原始碼", "build": "建置",
           "note_title": "README 原文",
           "note": "以下是應用隨附的 README（SDK {sdk}），保留原文、未翻譯；只替換了不適合公開的內容。"},
    "en": {"app": "Application", "purpose": "Purpose", "boards": "Boards and configs", "console": "Console",
           "item": "Item", "content": "Details", "source": "Source", "build": "Build",
           "note_title": "The README as shipped",
           "note": "Below is the README that ships with the application (SDK {sdk}), as written; "
                   "only content unfit for publication was replaced."},
}


def default_sdk() -> Path:
    env = os.environ.get("IPRO_SDK_RELEASE")
    return Path(env) if env else Path.home() / "Works" / f"IPRO-SDK-{release()['sdk']}"


def apps(data: dict[str, Any]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    return [(category, app) for category in data["categories"] for app in category["apps"]]


def has_page(app: dict[str, Any], sdk: Path) -> bool:
    readme = app.get("readme") or {}
    return not readme.get("exclude") and (sdk / app["path"] / "README.md").is_file()


def plain(text: str) -> str:
    """Strip Markdown links and code marks for front matter descriptions."""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return text.replace("`", "").strip()


def catalog(category: dict[str, Any], lang: str, pages: set[str]) -> str:
    labels = LABELS[lang]
    rows = []
    for app in category["apps"]:
        target = f"{app['name']}.md" if app["name"] in pages else github_url(app["path"])
        rows.append([f"[`{app['name']}`]({target})", app["purpose"][lang], app["boards"][lang], app["console"][lang]])
    return table([labels["app"], labels["purpose"], labels["boards"], labels["console"]], rows)


def readme_text(app: dict[str, Any], sdk: Path) -> str:
    rules = (app.get("readme") or {}).get("replace") or []
    tag = release_tag()
    text = (sdk / app["path"] / "README.md").read_text(encoding="utf-8")
    return readme_md.convert(
        text, app["path"], f"{RAW_BASE}/{tag}", github_url("", "blob").rstrip("/"),
        github_url("", "tree").rstrip("/"), rules)


def annotate_ignores(text: str, rule_ids: list[str], rules: list[redline_check.Rule]) -> str:
    """Mark reviewed matches of the given rules on prose lines as accepted."""
    if not rule_ids:
        return text
    chosen = [r for r in rules if r.id in rule_ids]
    lines = text.split("\n")
    code = readme_md.fence_map(lines)
    for i, line in enumerate(lines):
        hits = [r.id for r in chosen if not code[i] and r.pattern.search(line)]
        if hits:
            lines[i] = line + " " + " ".join(f"<!-- redline-ignore: {h} -->" for h in sorted(set(hits)))
    return "\n".join(lines)


def page(app: dict[str, Any], lang: str, readme: str) -> tuple[dict[str, Any], str]:
    labels = LABELS[lang]
    purpose = app["purpose"][lang].replace("](#", "](index.md#")
    facts = table([labels["item"], labels["content"]], [
        [labels["source"], f"[`{app['path']}`]({github_url(app['path'])})"],
        [labels["boards"], app["boards"][lang]],
        [labels["console"], app["console"][lang]],
        [labels["build"], f"`make -C {app['path']}`"],
    ])
    note = labels["note"].format(sdk=release()["sdk"])
    body = "\n".join([
        f"# {app['name']}", "", purpose, "", facts, "",
        "## README { #readme }", "",
        f'!!! note "{labels["note_title"]}"', f"    {note}", "",
        "<!-- verbatim:start -->", "", readme.strip(), "", "<!-- verbatim:end -->",
    ])
    meta = {"title": app["name"], "description": plain(app["purpose"][lang]), "generated": GENERATOR,
            "migrate_from": []}
    return meta, body


def render_all(data: dict[str, Any], sdk: Path, rules: list[redline_check.Rule]) -> dict[str, dict[str, str]]:
    """{lang: {relative path: full page text}} for every generated app page."""
    out: dict[str, dict[str, str]] = {lang: {} for lang in LANGS}
    for _, app in apps(data):
        if not has_page(app, sdk):
            continue
        readme = readme_text(app, sdk)
        readme = annotate_ignores(readme, (app.get("readme") or {}).get("redline_ignore") or [], rules)
        for lang in LANGS:
            meta, body = page(app, lang, readme)
            out[lang][f"examples/{app['name']}.md"] = front_matter(meta) + "\n" + body.strip() + "\n"
    return out


def write(data: dict[str, Any], pages: dict[str, dict[str, str]]) -> None:
    names = {Path(rel).stem for rel in pages["zh"]}
    for lang in LANGS:
        for stale in (DOCS / lang / "examples").glob("*.md"):
            if stale.name != "index.md" and stale.stem not in names and GENERATOR in stale.read_text(encoding="utf-8"):
                stale.unlink()
        for rel, text in pages[lang].items():
            (DOCS / lang / rel).write_text(text, encoding="utf-8")
        index = DOCS / lang / INDEX
        text = index.read_text(encoding="utf-8")
        for category in data["categories"]:
            text = replace_block(text, f"examples-{category['id']}", catalog(category, lang, names), ("<!-- ", " -->"))
        index.write_text(text, encoding="utf-8")
    nav = {lang: [(c["title"][lang], [(a["name"], f"examples/{a['name']}.md") for a in c["apps"] if a["name"] in names])
                  for c in data["categories"]] for lang in LANGS}
    update_nav("examples", {lang: [entry for entry in nav[lang] if entry[1]] for lang in LANGS})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--sdk", type=Path, default=default_sdk())
    args = parser.parse_args(argv)
    if not (args.sdk / "apps").is_dir():
        print(f"gen_examples: SDK release not found at {args.sdk}", file=sys.stderr)
        return 2
    data = load_yaml(DATA)
    try:
        rules = redline_check.public_rules() + redline_check.load_private_rules(None)
        pages = render_all(data, args.sdk, rules)
    except (readme_md.StaleRule, FileNotFoundError, ValueError) as exc:
        print(f"gen_examples: {exc}", file=sys.stderr)
        return 1
    errors = redline_errors(pages, rules)
    if errors:
        print("gen_examples: generated pages break the red lines; add curation rules in data/examples.yml:",
              file=sys.stderr)
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        return 1
    write(data, pages)
    print(f"examples: {len(pages['zh'])} app pages, {len(apps(data))} apps in the catalog")
    return 0


if __name__ == "__main__":
    sys.exit(main())
