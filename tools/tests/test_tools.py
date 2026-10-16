"""Unit tests for the docs CI tools (run: python -m pytest tools/tests)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import parity_check  # noqa: E402
import redline_check  # noqa: E402
import stub_report  # noqa: E402

PRIVATE_YAML = """
rules:
  - id: secret-project
    pattern: '\\bfoobar\\b'
    ignore_case: true
    message: internal project name
  - id: soft
    pattern: 'Vendorname'
    severity: warning
"""


# ---------- parity_check ----------

def test_headings_counts_h2_and_explicit_ids_outside_code():
    body = "\n".join([
        "# Title",
        "## One { #one }",
        "### Sub { #sub }",
        "```bash",
        "## not a heading { #fake }",
        "```",
        "## Two",
    ])
    assert parity_check.headings(body) == (2, ["one", "sub"])


def test_split_front_matter_returns_meta_and_body():
    meta, body = parity_check.split_front_matter("---\nstatus: stub\n---\n# Page\n")
    assert meta == {"status": "stub"}
    assert body == "# Page\n"


def test_split_front_matter_without_meta():
    assert parity_check.split_front_matter("# Page\n") == ({}, "# Page\n")


# ---------- redline_check ----------

@pytest.fixture
def private_rules(monkeypatch):
    monkeypatch.setenv("REDLINE_RULES", PRIVATE_YAML)
    return redline_check.load_private_rules(None)


def scan(tmp_path, rel, text, rules):
    path = tmp_path / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return list(redline_check.scan_file(path, rules))


def ids(findings):
    return [f.rule.id for f in findings]


def test_public_rules_flag_paths_tty_and_hashes(tmp_path):
    rules = redline_check.public_rules()
    text = "\n".join([
        "see /Users/someone/project",
        "port /dev/tty.usbserial-1234",
        "built from 4c5d7a662b",
        "port /dev/cu.usbserial-XXXX",
        "value 1234567890 and deadbeef",
    ])
    assert ids(scan(tmp_path, "x.md", text, rules)) == ["local-path", "tty-serial", "commit-hash"]


def test_wifi_rule_skips_lines_that_explain_the_companion(tmp_path):
    rules = redline_check.public_rules()
    bad = scan(tmp_path, "a.md", "IPRO7 supports Wi-Fi out of the box", rules)
    good = scan(tmp_path, "b.md", "IPRO7 has no built-in Wi-Fi; add an IPRO6S over SDIO", rules)
    anchor = scan(tmp_path, "c.md", "### IPRO7 要怎麼連網？ { #wifi }", rules)
    assert ids(bad) == ["ipro7-wifi"]
    assert good == []
    assert anchor == []


def test_zh_terms_apply_to_zh_pages_only(tmp_path):
    rules = redline_check.public_rules()
    root = redline_check.ROOT
    zh = root / "docs" / "zh" / "_redline_test.md"
    en = root / "docs" / "en" / "_redline_test.md"
    try:
        zh.write_text("藍芽連線\n", encoding="utf-8")
        en.write_text("藍芽連線\n", encoding="utf-8")
        assert ids(redline_check.scan_file(zh, rules)) == ["zh-term:藍芽"]
        assert ids(redline_check.scan_file(en, rules)) == []
    finally:
        zh.unlink(missing_ok=True)
        en.unlink(missing_ok=True)


def test_term_pattern_override_skips_compound_words():
    rules = redline_check.public_rules()
    zh = redline_check.ROOT / "docs" / "zh" / "_redline_term_test.md"
    try:
        zh.write_text("不需額外設定\n外設控制器\n", encoding="utf-8")
        assert [f.line for f in redline_check.scan_file(zh, rules)] == [2]
    finally:
        zh.unlink(missing_ok=True)


def test_verbatim_region_skips_terms_only(private_rules):
    rules = redline_check.public_rules() + private_rules
    zh = redline_check.ROOT / "docs" / "zh" / "_redline_verbatim_test.md"
    try:
        zh.write_text("<!-- verbatim:start -->\n默認設定\nfoobar\n<!-- verbatim:end -->\n默認\n", encoding="utf-8")
        found = [(f.line, f.rule.id) for f in redline_check.scan_file(zh, rules)]
        assert found == [(3, "secret-project"), (5, "zh-term:默認")]
    finally:
        zh.unlink(missing_ok=True)


def test_ignore_comment_on_same_or_previous_line(tmp_path, private_rules):
    text = "\n".join([
        "FooBar here <!-- redline-ignore: secret-project -->",
        "<!-- redline-ignore: secret-project -->",
        "foobar again",
        "foobar not ignored",
    ])
    found = scan(tmp_path, "x.md", text, private_rules)
    assert [(f.line, f.rule.id) for f in found] == [(4, "secret-project")]


def test_private_rule_unless_skips_the_line(monkeypatch, tmp_path):
    monkeypatch.setenv("REDLINE_RULES", "rules:\n  - {id: p, pattern: 'foobar', ignore_case: true, unless: 'pin|signal'}\n")
    rules = redline_check.load_private_rules(None)
    found = scan(tmp_path, "x.md", "15 FOOBAR pin\nthe foobar plan\n", rules)
    assert [f.line for f in found] == [2]


def test_private_matches_are_redacted_unless_requested(tmp_path, private_rules):
    finding = scan(tmp_path, "x.md", "the FOOBAR board", private_rules)[0]
    assert "FOOBAR" not in redline_check.format_finding(finding, show_private=False)
    assert "«FOOBAR»" in redline_check.format_finding(finding, show_private=True)


def test_private_rules_missing_is_an_error(monkeypatch, tmp_path):
    monkeypatch.delenv("REDLINE_RULES", raising=False)
    monkeypatch.delenv("IPRO_REDLINE_RULES", raising=False)
    monkeypatch.setattr(redline_check, "DEFAULT_PRIVATE_RULES", tmp_path / "missing.yml")
    with pytest.raises(FileNotFoundError):
        redline_check.load_private_rules(None)


def test_bad_severity_is_rejected(monkeypatch):
    monkeypatch.setenv("REDLINE_RULES", "rules:\n  - {id: x, pattern: y, severity: fatal}\n")
    with pytest.raises(ValueError):
        redline_check.load_private_rules(None)


def test_main_exit_codes(monkeypatch, tmp_path):
    monkeypatch.setenv("REDLINE_RULES", PRIVATE_YAML)
    clean = tmp_path / "clean.md"
    clean.write_text("nothing to see\n", encoding="utf-8")
    warn = tmp_path / "warn.md"
    warn.write_text("Vendorname only\n", encoding="utf-8")
    dirty = tmp_path / "dirty.md"
    dirty.write_text("foobar\n", encoding="utf-8")
    assert redline_check.main([str(clean)]) == 0
    assert redline_check.main([str(warn)]) == 0
    assert redline_check.main([str(dirty)]) == 1
    monkeypatch.setenv("REDLINE_RULES", "rules: []\n")
    assert redline_check.main([str(clean)]) == 2


# ---------- stub_report ----------

def test_claimed_splits_pages_and_sections():
    pages, sections = stub_report.claimed([
        "ble-development.html",
        "hardware.html#ipro6s",
        "hardware.html — IPRO7 overview",
        "api-reference.html — generated later",
    ])
    assert pages == {"ble-development.html", "hardware.html", "api-reference.html"}
    assert sections == {"hardware.html#ipro6s"}
