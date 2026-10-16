"""Doxygen XML to Markdown, for gen_api.py.

Only the parts the IPRO headers use are converted: paragraphs, inline code,
emphasis, links and cross references, lists, code listings, parameter and
return documentation, and note / warning / see-also sections. Unknown tags
fall back to their text.
"""
import re
import xml.etree.ElementTree as ET
from collections.abc import Callable
from dataclasses import dataclass, field

# Resolves a Doxygen refid to a Markdown link target, or None to render plain code.
Resolver = Callable[[str], "str | None"]
SECTIONS = ("note", "warning", "attention", "see", "return", "pre", "post", "remark", "since", "deprecated")


@dataclass
class Doc:
    """The documentation of one symbol, split into the parts a page lays out."""
    brief: str = ""
    body: list[str] = field(default_factory=list)
    params: list[tuple[str, str]] = field(default_factory=list)
    retvals: list[tuple[str, str]] = field(default_factory=list)
    returns: str = ""
    sections: list[tuple[str, str]] = field(default_factory=list)


def escape(text: str) -> str:
    """Escape characters Markdown would read as HTML in prose."""
    return text.replace("<", "&lt;").replace(">", "&gt;")


def text_of(el: ET.Element | None) -> str:
    return "".join(el.itertext()).strip() if el is not None else ""


def inline(el: ET.Element, resolve: Resolver) -> str:
    """Inline Markdown for the content of a <para> or similar element."""
    out = [escape(el.text or "")]
    for child in el:
        out.append(_inline_child(child, resolve))
        out.append(escape(child.tail or ""))
    return re.sub(r"[ \t]+", " ", "".join(out))


def _inline_child(child: ET.Element, resolve: Resolver) -> str:
    tag = child.tag
    if tag == "computeroutput":
        return f"`{text_of(child)}`"
    if tag == "bold":
        return f"**{inline(child, resolve).strip()}**"
    if tag in ("emphasis", "italic"):
        return f"*{inline(child, resolve).strip()}*"
    if tag == "ref":
        target = resolve(child.get("refid", ""))
        name = text_of(child)
        return f"[`{name}`]({target})" if target else f"`{name}`"
    if tag == "ulink":
        return f"[{inline(child, resolve).strip()}]({child.get('url')})"
    if tag == "linebreak":
        return "<br>"
    if tag in ("parameterlist", "simplesect", "programlisting", "itemizedlist", "orderedlist", "verbatim"):
        return ""   # handled as blocks by blocks()
    return escape(text_of(child))


def _code_text(node: ET.Element) -> str:
    """Text of a <codeline> subtree; <sp/> stands for one space."""
    out = [node.text or ""]
    for child in node:
        out.append(" " if child.tag == "sp" else _code_text(child))
        out.append(child.tail or "")
    return "".join(out)


def code_listing(el: ET.Element) -> str:
    lines = [_code_text(line).rstrip() for line in el.findall("codeline")]
    return "```c\n" + "\n".join(lines) + "\n```"


def list_block(el: ET.Element, resolve: Resolver) -> str:
    marker = "1." if el.tag == "orderedlist" else "-"
    items = []
    for item in el.findall("listitem"):
        text = " ".join(paragraphs(item, resolve)).strip()
        items.append(f"{marker} {text}")
    return "\n".join(items)


def paragraphs(el: ET.Element, resolve: Resolver) -> list[str]:
    """Block-level Markdown for every <para> directly under `el`."""
    out = []
    for para in el.findall("para"):
        text = inline(para, resolve).strip()
        if text:
            out.append(text)
        for child in para:
            if child.tag == "programlisting":
                out.append(code_listing(child))
            elif child.tag in ("itemizedlist", "orderedlist"):
                out.append(list_block(child, resolve))
            elif child.tag == "verbatim":
                out.append("```text\n" + (child.text or "").strip("\n") + "\n```")
    return out


def parse_doc(member: ET.Element, resolve: Resolver) -> Doc:
    doc = Doc(brief=" ".join(paragraphs(member.find("briefdescription"), resolve)) if member.find("briefdescription") is not None else "")
    detail = member.find("detaileddescription")
    if detail is None:
        return doc
    doc.body = paragraphs(detail, resolve)
    for plist in detail.iter("parameterlist"):
        rows = []
        for item in plist.findall("parameteritem"):
            names = ", ".join(text_of(n) for n in item.iter("parametername"))
            desc = " ".join(paragraphs(item.find("parameterdescription"), resolve))
            rows.append((names, desc))
        (doc.retvals if plist.get("kind") == "retval" else doc.params).extend(rows)
    for sect in detail.iter("simplesect"):
        kind = sect.get("kind")
        text = " ".join(paragraphs(sect, resolve))
        if kind == "return":
            doc.returns = text
        elif kind in SECTIONS:
            doc.sections.append((kind, text))
    return doc
