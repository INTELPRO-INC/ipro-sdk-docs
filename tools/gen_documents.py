#!/usr/bin/env python3
"""Generate documents/index.md (both languages) from data/documents.yml.

Each document is either `access: request` (listed, available from INTELPRO
on request) or `access: public` with one download URL per language in
`files`. A public document without files is an error, so a page never shows
an empty download column.

Usage: tools/gen_documents.py
"""
import sys
from typing import Any

from gen_common import LANGS, ROOT, load_yaml, table, write_page

DATA = ROOT / "data" / "documents.yml"
PAGE = "documents/index.md"
LABELS = {
    "zh": {"document": "文件", "version": "版本", "languages": "語言", "contents": "內容", "get": "取得方式",
           "request": "向 INTELPRO 索取", "notice": "取得方式", "lang": {"zh-TW": "繁中", "en": "English"},
           "sep": "／"},
    "en": {"document": "Document", "version": "Version", "languages": "Languages", "contents": "Contents",
           "get": "Availability", "request": "On request", "notice": "How to get them",
           "lang": {"zh-TW": "zh-TW", "en": "English"}, "sep": " / "},
}


def validate(data: dict[str, Any]) -> list[str]:
    errors = []
    seen = set()
    for category in data["categories"]:
        for doc in category["documents"]:
            if doc["id"] in seen:
                errors.append(f"duplicate document id {doc['id']}")
            seen.add(doc["id"])
            if doc["access"] not in ("request", "public"):
                errors.append(f"{doc['id']}: access must be request or public")
            if doc["access"] == "public":
                missing = [lang for lang in doc["languages"] if not (doc.get("files") or {}).get(lang)]
                if missing:
                    errors.append(f"{doc['id']}: public but no file for {', '.join(missing)}")
    return errors


def availability(doc: dict[str, Any], lang: str) -> str:
    labels = LABELS[lang]
    if doc["access"] == "request":
        return labels["request"]
    links = [f"[{labels['lang'][code]}]({doc['files'][code]})" for code in doc["languages"]]
    return labels["sep"].join(links)


def render(data: dict[str, Any], lang: str) -> str:
    labels = LABELS[lang]
    page = data["page"]
    parts = [f"# {page['title'][lang]}", "", page["intro"][lang], ""]
    on_request = any(d["access"] == "request" for c in data["categories"] for d in c["documents"])
    if on_request:
        parts += [f'!!! info "{labels["notice"]}"', f"    {page['request_notice'][lang]}", ""]
    headers = [labels[k] for k in ("document", "version", "languages", "contents", "get")]
    for category in data["categories"]:
        rows = [[
            doc["title"][lang],
            doc["version"],
            labels["sep"].join(labels["lang"][code] for code in doc["languages"]),
            doc["summary"][lang],
            availability(doc, lang),
        ] for doc in category["documents"]]
        parts += [f"## {category['title'][lang]} {{ #{category['id']} }}", "", table(headers, rows), ""]
    parts.append(page["outro"][lang])
    return "\n".join(parts)


def main() -> int:
    data = load_yaml(DATA)
    errors = validate(data)
    for err in errors:
        print(f"documents.yml: {err}", file=sys.stderr)
    if errors:
        return 1
    for lang in LANGS:
        meta = {
            "title": data["page"]["title"][lang],
            "description": data["page"]["description"][lang],
            "generated": "tools/gen_documents.py",
            "migrate_from": [],
        }
        write_page(lang, PAGE, meta, render(data, lang))
    count = sum(len(c["documents"]) for c in data["categories"])
    print(f"documents: {count} documents in {len(data['categories'])} categories -> docs/*/{PAGE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
