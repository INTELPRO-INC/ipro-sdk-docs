#!/usr/bin/env python3
"""Red-line check for the public documentation.

Two rule sets apply:

* Public rules (this file and tools/zh_tw_terms.yml): local absolute paths,
  macOS tty serial devices, commit-hash-like strings, the IPRO7 Wi-Fi wording
  and Taiwan terminology on zh-TW pages.
* Private rules: internal project, customer and vendor names. They must never
  be committed to this public repository and are loaded from the first of:
      --rules PATH
      $REDLINE_RULES            YAML text (GitHub Actions secret)
      $IPRO_REDLINE_RULES       path to a YAML file
      ../docs/internal/docs_site/redline_rules.yml   (SDK checkout layout)
  Missing private rules is an error.

Findings from private rules never print the matched text, because CI logs of
a public repository are public. Use --show-private locally to see it.

Suppress one finding with `<!-- redline-ignore: <rule-id> -->` on the same
line or on the line before.

Exit status: 0 clean (warnings allowed), 1 errors found, 2 rules unavailable.
"""
import argparse
import os
import re
import sys
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PRIVATE_RULES = ROOT.parent / "docs" / "internal" / "docs_site" / "redline_rules.yml"
TERMS_FILE = ROOT / "tools" / "zh_tw_terms.yml"
SCAN_GLOBS = ("docs/**/*.md", "overrides/**/*.html", "overrides/**/*.css", "overrides/**/*.js",
              "mkdocs*.yml", "README.md")
IGNORE = re.compile(r"redline-ignore:\s*([\w:-]+)")
SEVERITIES = ("error", "warning")


@dataclass(frozen=True)
class Rule:
    id: str
    pattern: re.Pattern[str]
    severity: str
    message: str
    private: bool = False
    lang: str | None = None          # "zh" / "en" limits the rule to that language's pages
    unless: re.Pattern[str] | None = None  # skip the line when this also matches


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    column: int
    rule: Rule
    text: str


def public_rules() -> list[Rule]:
    rules = [
        Rule("local-path", re.compile(r"/Users/[\w.-]+|/home/[\w.-]+|[A-Za-z]:\\Users\\"),
             "error", "local absolute path"),
        Rule("tty-serial", re.compile(r"/dev/tty\.(?:usb|SLAB|wch)\w*"),
             "error", "macOS serial ports must be written as /dev/cu.*"),
        Rule("commit-hash", re.compile(r"\b(?=[0-9a-f]*[a-f])(?=[0-9a-f]*\d)[0-9a-f]{9,40}\b"),
             "error", "looks like a commit hash; release docs must not carry internal revisions"),
        # Case-sensitive "Wi-Fi"/"WiFi" only, so anchors (#wifi) and config keys (..._WIFI) do not match.
        Rule("ipro7-wifi", re.compile(r"IPRO7(?:AI)?\b.*\bWi-?Fi\b|\bWi-?Fi\b.*IPRO7(?:AI)?\b"),
             "warning", "IPRO7 has no built-in Wi-Fi; say how Wi-Fi is added (IPRO6S over SDIO, FIN card)",
             unless=re.compile(r"不內建|未內建|沒有內建|無內建|no built-in|IPRO6S?|FIN|companion|SDIO|"
                               r"AIC8800|ATBM|乙太網路|Ethernet", re.I)),
    ]
    terms = yaml.safe_load(TERMS_FILE.read_text(encoding="utf-8")) or {}
    for item in terms.get("terms", []):
        note = f"; {item['note']}" if item.get("note") else ""
        pattern = item.get("pattern") or re.escape(item["term"])
        rules.append(Rule(f"zh-term:{item['term']}", re.compile(pattern),
                          item.get("severity", "error"), f"use 「{item['use']}」{note}", lang="zh"))
    return rules


def load_private_rules(path_arg: str | None) -> list[Rule]:
    text = None
    if path_arg:
        text = Path(path_arg).read_text(encoding="utf-8")
    elif os.environ.get("REDLINE_RULES", "").strip():
        text = os.environ["REDLINE_RULES"]
    elif os.environ.get("IPRO_REDLINE_RULES"):
        text = Path(os.environ["IPRO_REDLINE_RULES"]).read_text(encoding="utf-8")
    elif DEFAULT_PRIVATE_RULES.is_file():
        text = DEFAULT_PRIVATE_RULES.read_text(encoding="utf-8")
    if text is None:
        raise FileNotFoundError(
            "private red-line rules not found: pass --rules, set REDLINE_RULES (CI secret) or "
            f"IPRO_REDLINE_RULES, or create {DEFAULT_PRIVATE_RULES}")
    data = yaml.safe_load(text) or {}
    rules = []
    for item in data.get("rules", []):
        severity = item.get("severity", "error")
        if severity not in SEVERITIES:
            raise ValueError(f"rule {item.get('id')}: severity must be one of {SEVERITIES}")
        flags = re.I if item.get("ignore_case") else 0
        rules.append(Rule(item["id"], re.compile(item["pattern"], flags), severity,
                          item.get("message", "private red-line term"), private=True))
    if not rules:
        raise ValueError("private red-line rules file has no rules")
    return rules


def files_to_scan(paths: list[str]) -> list[Path]:
    if paths:
        found: list[Path] = []
        for p in paths:
            base = (ROOT / p) if not Path(p).is_absolute() else Path(p)
            found += [base] if base.is_file() else sorted(f for f in base.rglob("*") if f.is_file())
        return found
    return sorted({f for pattern in SCAN_GLOBS for f in ROOT.glob(pattern) if f.is_file()})


def page_lang(path: Path) -> str | None:
    parts = path.relative_to(ROOT).parts if path.is_relative_to(ROOT) else path.parts
    if len(parts) > 1 and parts[0] == "docs" and parts[1] in ("zh", "en"):
        return parts[1]
    return None


def scan_file(path: Path, rules: Iterable[Rule]) -> Iterator[Finding]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return
    lang = page_lang(path)
    shown = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
    for number, line in enumerate(lines, start=1):
        ignored = set(IGNORE.findall(line))
        if number > 1:
            ignored |= set(IGNORE.findall(lines[number - 2]))
        for rule in rules:
            if rule.lang and rule.lang != lang:
                continue
            if rule.id in ignored:
                continue
            for match in rule.pattern.finditer(line):
                if rule.unless and rule.unless.search(line):
                    break
                yield Finding(shown, number, match.start() + 1, rule, match.group(0))


def format_finding(f: Finding, show_private: bool) -> str:
    where = f"{f.path}:{f.line}:{f.column}"
    text = f" «{f.text}»" if (show_private or not f.rule.private) else ""
    return f"{where}: {f.rule.severity} [{f.rule.id}] {f.rule.message}{text}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("paths", nargs="*", help="files or directories (default: site sources)")
    parser.add_argument("--rules", help="private rules YAML file")
    parser.add_argument("--show-private", action="store_true",
                        help="print the matched text of private rules (local use only)")
    args = parser.parse_args(argv)

    try:
        rules = public_rules() + load_private_rules(args.rules)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"redline: {exc}", file=sys.stderr)
        return 2

    findings = [f for path in files_to_scan(args.paths) for f in scan_file(path, rules)]
    for f in findings:
        print(format_finding(f, args.show_private))
    errors = sum(f.rule.severity == "error" for f in findings)
    warnings = len(findings) - errors
    print(f"redline: {errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
