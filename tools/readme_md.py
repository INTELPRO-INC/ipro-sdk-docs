"""Turn a GitHub README into Markdown that renders the same under Python-Markdown.

Used by gen_examples.py. Every function works line by line and leaves fenced
code blocks alone, except for re-indenting a fence that sits inside a list.
"""
import posixpath
import re

FENCE = re.compile(r"^(?P<indent>[ \t]*)(?P<mark>```|~~~)")
HEADING = re.compile(r"^(?P<hashes>#{1,6})[ \t]+\S")
LIST_ITEM = re.compile(r"^(?P<indent> *)(?:[-*+]|\d+[.)])[ \t]+")
LINK = re.compile(r"(?P<bang>!?)\[(?P<text>[^\]]*)\]\((?P<target>[^)\s]+)(?P<title>\s+\"[^\"]*\")?\)")
SERIAL = re.compile(r"/dev/cu\.usbserial-(?!XXXX\b)[0-9A-Za-z]+")


class StaleRule(ValueError):
    """A curation rule no longer matches the README it was written for."""


def apply_rules(text: str, rules: list[dict[str, str]]) -> str:
    for rule in rules:
        text, count = re.subn(rule["pattern"], rule["repl"], text, flags=re.M)
        if count == 0:
            raise StaleRule(f"pattern did not match: {rule['pattern']!r}")
    return text


def normalize_serial(text: str) -> str:
    return SERIAL.sub("/dev/cu.usbserial-XXXX", text)


def fence_map(lines: list[str]) -> list[bool]:
    """True for lines inside (or delimiting) a fenced code block."""
    inside = []
    fence = None
    for line in lines:
        match = FENCE.match(line)
        if fence is None and match:
            fence = match.group("mark")
            inside.append(True)
        elif fence is not None:
            inside.append(True)
            if match and match.group("mark") == fence:
                fence = None
        else:
            inside.append(False)
    return inside


def drop_title(lines: list[str]) -> list[str]:
    """Remove the first level-1 heading (the page supplies its own title)."""
    code = fence_map(lines)
    for i, line in enumerate(lines):
        if not code[i] and line.startswith("# "):
            rest = lines[i + 1:]
            while rest and not rest[0].strip():
                rest = rest[1:]
            return lines[:i] + rest
    return lines


def shift_headings(lines: list[str], top: int = 3) -> list[str]:
    """Shift headings so the shallowest one becomes level `top` (max 6)."""
    code = fence_map(lines)
    levels = [len(HEADING.match(l).group("hashes")) for i, l in enumerate(lines)
              if not code[i] and HEADING.match(l)]
    if not levels:
        return lines
    shift = top - min(levels)
    out = []
    for i, line in enumerate(lines):
        match = None if code[i] else HEADING.match(line)
        if match:
            level = min(6, len(match.group("hashes")) + shift)
            line = "#" * level + line[len(match.group("hashes")):]
        out.append(line)
    return out


def rewrite_links(lines: list[str], app_path: str, raw_base: str, blob_base: str, tree_base: str) -> list[str]:
    """Absolute links for relative targets; drop in-page anchor links (keep the text)."""
    code = fence_map(lines)

    def fix(match: re.Match[str]) -> str:
        bang, text, target = match.group("bang"), match.group("text"), match.group("target")
        if re.match(r"^[a-z]+:", target):
            return match.group(0)
        if target.startswith("#"):
            return text
        path, _, anchor = target.partition("#")
        full = posixpath.normpath(posixpath.join(app_path, path))
        if bang:
            url = f"{raw_base}/{full}"
        else:
            url = f"{blob_base if posixpath.splitext(full)[1] else tree_base}/{full}"
        return f"{bang}[{text}]({url}{'#' + anchor if anchor else ''})"

    out = []
    for i, line in enumerate(lines):
        if code[i]:
            out.append(line)
            continue
        parts = re.split(r"(`[^`]*`)", line)
        out.append("".join(p if p.startswith("`") else LINK.sub(fix, p) for p in parts))
    return out


def _level_for(indent: int, stack: list[int]) -> int:
    """Index of the deepest list indent strictly below `indent`."""
    level = -1
    for i, value in enumerate(stack):
        if value < indent:
            level = i
    return level


def normalize_lists(lines: list[str]) -> list[str]:
    """Four-space nesting, and a blank line before lists and tables."""
    code = fence_map(lines)
    out: list[str] = []
    stack: list[int] = []
    fence_shift = 0
    for i, line in enumerate(lines):
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)
        if code[i]:
            opening = FENCE.match(line) and (i == 0 or not code[i - 1])
            if opening and stack and indent > 0:
                fence_shift = 4 * (_level_for(indent, stack) + 1) - indent
            elif opening:
                fence_shift = 0
            out.append(" " * max(0, indent + fence_shift) + stripped if line.strip() else line)
            continue
        if not line.strip():
            out.append(line)
            continue
        item = LIST_ITEM.match(line)
        if item:
            while stack and stack[-1] > indent:
                stack.pop()
            if not stack or stack[-1] < indent:
                stack.append(indent)
            level = stack.index(indent)
            starts_list = level == 0 and (not out or not out[-1].strip() or not _is_list_context(out[-1]))
            if starts_list and out and out[-1].strip():
                out.append("")
            out.append(" " * (4 * level) + stripped)
            continue
        if indent > 0 and stack:
            out.append(" " * (4 * (_level_for(indent, stack) + 1)) + stripped)
            continue
        stack = []
        if stripped.startswith("|") and out and out[-1].strip() and not out[-1].lstrip().startswith("|"):
            out.append("")
        out.append(line)
    return out


def _is_list_context(line: str) -> bool:
    return bool(LIST_ITEM.match(line)) or line.startswith(" ")


def convert(text: str, app_path: str, raw_base: str, blob_base: str, tree_base: str,
            rules: list[dict[str, str]] | None = None) -> str:
    text = apply_rules(text, rules or [])
    text = normalize_serial(text)
    lines = text.replace("\r\n", "\n").split("\n")
    lines = drop_title(lines)
    lines = shift_headings(lines)
    lines = rewrite_links(lines, app_path, raw_base, blob_base, tree_base)
    lines = normalize_lists(lines)
    return "\n".join(lines).strip() + "\n"
