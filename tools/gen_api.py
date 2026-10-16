#!/usr/bin/env python3
"""Generate the API reference from Doxygen XML of the SDK's public headers.

Writes reference/api/<group>.md for every group in data/api.yml (both
languages), the group table in reference/api/index.md and the `api` nav block.
Every header in the XML must belong to exactly one group or be excluded.

Produce the XML from an SDK checkout that has the documented headers:
    cd <sdk> && (cat docs/api/Doxyfile; echo "OUTPUT_DIRECTORY = /tmp/ipro-api") | doxygen -
Usage: tools/gen_api.py --xml /tmp/ipro-api/xml
"""
import argparse
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import redline_check
from doxy_md import Doc, parse_doc, text_of
from gen_common import (LANGS, ROOT, front_matter, github_url, load_yaml, redline_errors, replace_block,
                        table, update_nav, write_page)

DATA = ROOT / "data" / "api.yml"
GENERATOR = "tools/gen_api.py"
LABELS = {
    "zh": {"param": "參數", "desc": "說明", "returns": "回傳值", "retval": "回傳碼", "name": "名稱", "value": "值",
           "field": "欄位", "type": "型別", "definition": "定義", "header": "標頭", "functions": "函式",
           "macros": "巨集", "typedefs": "型別定義", "group": "分類", "headers": "標頭數", "contents": "內容",
           "source": "原始碼", "anon_enum": "匿名列舉", "comment_lang": "說明取自標頭檔註解（英文）。",
           "sections": {"note": "注意", "warning": "警告", "attention": "注意", "see": "參考", "pre": "前置條件",
                        "post": "後置條件", "remark": "備註", "since": "起始版本", "deprecated": "已棄用"}},
    "en": {"param": "Parameter", "desc": "Description", "returns": "Returns", "retval": "Return value",
           "name": "Name", "value": "Value", "field": "Field", "type": "Type", "definition": "Definition",
           "header": "Header", "functions": "Functions", "macros": "Macros", "typedefs": "Typedefs",
           "group": "Group", "headers": "Headers", "contents": "Contents", "source": "Source",
           "anon_enum": "Anonymous enum", "comment_lang": "",
           "sections": {"note": "Note", "warning": "Warning", "attention": "Attention", "see": "See also",
                        "pre": "Precondition", "post": "Postcondition", "remark": "Remark", "since": "Since",
                        "deprecated": "Deprecated"}},
}
ADMONITION = {"note": "note", "attention": "warning", "warning": "warning", "deprecated": "warning"}


@dataclass
class Header:
    path: str
    xml: ET.Element
    slug: str


def header_slug(path: str) -> str:
    return Path(path).name.replace(".", "-")


def load_headers(xml_dir: Path) -> dict[str, Header]:
    headers = {}
    for f in sorted(xml_dir.glob("*_8h.xml")):
        compound = ET.parse(f).getroot().find("compounddef")
        path = compound.find("location").get("file")
        headers[path] = Header(path, compound, header_slug(path))
    return headers


def check_groups(data: dict[str, Any], headers: dict[str, Header]) -> list[str]:
    listed = [h for g in data["groups"] for h in g["headers"]] + list(data.get("exclude") or [])
    errors = [f"listed twice: {h}" for h in sorted({h for h in listed if listed.count(h) > 1})]
    errors += [f"not in the XML: {h}" for h in listed if h not in headers]
    errors += [f"not in any group or exclude: {h}" for h in headers if h not in listed]
    return errors


def members(header: Header, kind: str) -> list[ET.Element]:
    return [m for m in header.xml.iter("memberdef") if m.get("kind") == kind]


_STRUCTS: dict[Path, ET.Element] = {}


def structs(header: Header, xml_dir: Path) -> list[ET.Element]:
    """Struct compounds declared in the header, parsed once so anchors stick."""
    out = []
    for inner in header.xml.findall("innerclass"):
        path = xml_dir / f"{inner.get('refid')}.xml"
        if path not in _STRUCTS and path.is_file():
            _STRUCTS[path] = ET.parse(path).getroot().find("compounddef")
        if path in _STRUCTS:
            out.append(_STRUCTS[path])
    return out


def build_anchors(data: dict[str, Any], headers: dict[str, Header], xml_dir: Path) -> dict[str, str]:
    """refid -> '<group>.md#<anchor>' for every symbol that gets its own heading."""
    anchors: dict[str, str] = {}
    for group in data["groups"]:
        used: set[str] = set()
        for path in group["headers"]:
            header = headers[path]
            used.add(header.slug)
            anchors[header.xml.get("id")] = f"{group['id']}.md#{header.slug}"
            for member in header.xml.iter("memberdef"):
                kind = member.get("kind")
                if kind in ("function", "enum"):
                    anchor = unique(symbol_id(member, header), used)
                    member.set("_anchor", anchor)
                    anchors[member.get("id")] = f"{group['id']}.md#{anchor}"
                    for value in member.findall("enumvalue"):
                        anchors[value.get("id")] = f"{group['id']}.md#{anchor}"
                elif kind in ("define", "typedef", "variable"):
                    section = f"{header.slug}-{'macros' if kind == 'define' else 'typedefs'}"
                    anchors[member.get("id")] = f"{group['id']}.md#{section}"
            for struct in structs(header, xml_dir):
                anchor = unique(text_of(struct.find("compoundname")), used)
                struct.set("_anchor", anchor)
                anchors[struct.get("id")] = f"{group['id']}.md#{anchor}"
    return anchors


def symbol_id(member: ET.Element, header: Header) -> str:
    name = text_of(member.find("name"))
    if not name or name.startswith("@"):
        return f"{header.slug}-enum"
    return re.sub(r"[^\w-]", "-", name)


def unique(anchor: str, used: set[str]) -> str:
    candidate, n = anchor, 2
    while candidate in used:
        candidate, n = f"{anchor}-{n}", n + 1
    used.add(candidate)
    return candidate


def doc_blocks(doc: Doc, lang: str) -> list[str]:
    labels = LABELS[lang]
    out = [doc.brief] if doc.brief else []
    out += doc.body
    if doc.params:
        out.append(table([labels["param"], labels["desc"]], [[f"`{n}`", d] for n, d in doc.params]))
    if doc.returns:
        out.append(f"**{labels['returns']}**：{doc.returns}" if lang == "zh" else f"**{labels['returns']}:** {doc.returns}")
    if doc.retvals:
        out.append(table([labels["retval"], labels["desc"]], [[f"`{n}`", d] for n, d in doc.retvals]))
    for kind, text in doc.sections:
        title = labels["sections"][kind]
        if kind in ADMONITION:
            out.append(f'!!! {ADMONITION[kind]} "{title}"\n    ' + text.replace("\n", "\n    "))
        else:
            out.append(f"**{title}**：{text}" if lang == "zh" else f"**{title}:** {text}")
    return out


def function_md(member: ET.Element, lang: str, resolve: Any) -> str:
    name = text_of(member.find("name"))
    signature = f"{text_of(member.find('type'))} {name}{text_of(member.find('argsstring'))};".strip()
    parts = [f"### {name} {{ #{member.get('_anchor')} }}", "", "```c", signature, "```", ""]
    parts += [b + "\n" for b in doc_blocks(parse_doc(member, resolve), lang)]
    return "\n".join(parts)


def enum_md(member: ET.Element, header: Header, lang: str, resolve: Any) -> str:
    labels = LABELS[lang]
    name = text_of(member.find("name"))
    title = labels["anon_enum"] if not name or name.startswith("@") else name
    rows = []
    for value in member.findall("enumvalue"):
        init = text_of(value.find("initializer")).lstrip("= ").strip()
        vdoc = parse_doc(value, resolve)
        rows.append([f"`{text_of(value.find('name'))}`", f"`{init}`" if init else "",
                     " ".join([vdoc.brief] + vdoc.body).strip()])
    parts = [f"### {title} {{ #{member.get('_anchor')} }}", ""]
    parts += [b + "\n" for b in doc_blocks(parse_doc(member, resolve), lang)]
    parts.append(table([labels["name"], labels["value"], labels["desc"]], rows))
    return "\n".join(parts) + "\n"


def struct_md(struct: ET.Element, lang: str, resolve: Any) -> str:
    labels = LABELS[lang]
    name = text_of(struct.find("compoundname"))
    rows = []
    for field in struct.iter("memberdef"):
        if field.get("kind") != "variable":
            continue
        fdoc = parse_doc(field, resolve)
        ftype = f"`{text_of(field.find('type'))}{text_of(field.find('argsstring'))}`"
        rows.append([f"`{text_of(field.find('name'))}`", ftype, " ".join([fdoc.brief] + fdoc.body).strip()])
    parts = [f"### {name} {{ #{struct.get('_anchor')} }}", ""]
    parts += [b + "\n" for b in doc_blocks(parse_doc(struct, resolve), lang)]
    if rows:
        parts.append(table([labels["field"], labels["type"], labels["desc"]], rows))
    return "\n".join(parts) + "\n"


def macro_rows(header: Header, resolve: Any) -> list[list[str]]:
    rows = []
    for member in members(header, "define"):
        name = text_of(member.find("name"))
        params = [text_of(p.find("defname")) for p in member.findall("param")]
        shown = f"{name}({', '.join(params)})" if member.findall("param") else name
        value = text_of(member.find("initializer"))
        value = value if len(value) <= 40 else value[:37] + "..."
        doc = parse_doc(member, resolve)
        rows.append([f"`{shown}`", f"`{value}`" if value else "", " ".join([doc.brief] + doc.body).strip()])
    return rows


def typedef_rows(header: Header, resolve: Any) -> list[list[str]]:
    rows = []
    for member in members(header, "typedef") + members(header, "variable"):
        doc = parse_doc(member, resolve)
        rows.append([f"`{text_of(member.find('name'))}`", f"`{text_of(member.find('definition'))}`",
                     " ".join([doc.brief] + doc.body).strip()])
    return rows


def include_line(name: str, path: str, lang: str) -> str:
    link = f"[{LABELS[lang]['source']}]({github_url(path, 'blob')})"
    return f'`#include "{name}"`（{link}）' if lang == "zh" else f'`#include "{name}"` ({link})'


def header_md(header: Header, xml_dir: Path, lang: str, resolve: Any) -> str:
    labels = LABELS[lang]
    name = Path(header.path).name
    file_doc = parse_doc(header.xml, resolve)
    parts = [f"## {name} {{ #{header.slug} }}", "",
             include_line(name, header.path, lang), ""]
    parts += [b + "\n" for b in [file_doc.brief] + file_doc.body if b]
    parts += [function_md(m, lang, resolve) for m in members(header, "function")]
    parts += [enum_md(m, header, lang, resolve) for m in members(header, "enum")]
    parts += [struct_md(s, lang, resolve) for s in structs(header, xml_dir)]
    typedefs = typedef_rows(header, resolve)
    if typedefs:
        parts += [f"### {labels['typedefs']} {{ #{header.slug}-typedefs }}", "",
                  table([labels["name"], labels["definition"], labels["desc"]], typedefs), ""]
    macros = macro_rows(header, resolve)
    if macros:
        parts += [f"### {labels['macros']} {{ #{header.slug}-macros }}", "",
                  table([labels["name"], labels["value"], labels["desc"]], macros), ""]
    return "\n".join(parts)


def group_page(group: dict[str, Any], headers: dict[str, Header], xml_dir: Path, lang: str,
               anchors: dict[str, str]) -> tuple[dict[str, Any], str]:
    labels = LABELS[lang]

    def resolve(refid: str) -> str | None:
        target = anchors.get(refid)
        if not target:
            return None
        page, _, anchor = target.partition("#")
        return f"#{anchor}" if page == f"{group['id']}.md" else target

    overview = table([labels["header"], labels["functions"], labels["desc"]], [
        [f"[`{Path(p).name}`](#{headers[p].slug})", str(len(members(headers[p], "function"))),
         parse_doc(headers[p].xml, resolve).brief] for p in group["headers"]])
    intro = [f"# {group['title'][lang]}", "", group["summary"][lang]]
    if labels["comment_lang"]:
        intro[-1] += labels["comment_lang"]
    body = "\n".join(intro + ["", overview, ""] + [header_md(headers[p], xml_dir, lang, resolve) for p in group["headers"]])
    meta = {"title": group["title"][lang], "description": group["summary"][lang], "generated": GENERATOR,
            "migrate_from": []}
    return meta, body


def groups_table(data: dict[str, Any], headers: dict[str, Header], lang: str) -> str:
    labels = LABELS[lang]
    rows = [[f"[{g['title'][lang]}]({g['id']}.md)", str(len(g["headers"])),
             str(sum(len(members(headers[p], "function")) for p in g["headers"])), g["summary"][lang]]
            for g in data["groups"]]
    return table([labels["group"], labels["headers"], labels["functions"], labels["contents"]], rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--xml", type=Path, required=True, help="Doxygen XML output directory")
    args = parser.parse_args(argv)
    data = load_yaml(DATA)
    headers = load_headers(args.xml)
    problems = check_groups(data, headers)
    if problems:
        print("gen_api: data/api.yml does not match the XML:\n  " + "\n  ".join(problems), file=sys.stderr)
        return 1
    anchors = build_anchors(data, headers, args.xml)
    pages: dict[str, dict[str, str]] = {lang: {} for lang in LANGS}
    rendered = {}
    for group in data["groups"]:
        for lang in LANGS:
            meta, body = group_page(group, headers, args.xml, lang, anchors)
            rel = f"reference/api/{group['id']}.md"
            rendered[(lang, rel)] = (meta, body)
            pages[lang][rel] = front_matter(meta) + "\n" + body.strip() + "\n"
    try:
        rules = redline_check.public_rules() + redline_check.load_private_rules(None)
    except (FileNotFoundError, ValueError) as exc:
        print(f"gen_api: {exc}", file=sys.stderr)
        return 1
    errors = redline_errors(pages, rules)
    if errors:
        print("gen_api: generated pages break the red lines; fix the header comments:\n  " + "\n  ".join(errors),
              file=sys.stderr)
        return 1
    for (lang, rel), (meta, body) in rendered.items():
        write_page(lang, rel, meta, body)
    for lang in LANGS:
        index = ROOT / "docs" / lang / "reference" / "api" / "index.md"
        text = replace_block(index.read_text(encoding="utf-8"), "api-groups", groups_table(data, headers, lang),
                             ("<!-- ", " -->"))
        index.write_text(text, encoding="utf-8")
    update_nav("api", {lang: [(g["title"][lang], f"reference/api/{g['id']}.md") for g in data["groups"]]
                       for lang in LANGS})
    functions = sum(len(members(h, "function")) for p, h in headers.items() if p not in (data.get("exclude") or []))
    print(f"api: {len(data['groups'])} group pages, {len(headers) - len(data.get('exclude') or [])} headers, "
          f"{functions} functions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
