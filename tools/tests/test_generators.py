"""Unit tests for the page generators (run: python -m pytest tools/tests)."""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import doxy_md  # noqa: E402
import gen_common  # noqa: E402
import gen_documents  # noqa: E402
import gen_redirects  # noqa: E402
import readme_md  # noqa: E402

BASES = ("https://raw/x", "https://blob/x", "https://tree/x")


# ---------- readme_md ----------

def test_drop_title_and_shift_headings():
    lines = ["# App", "", "## Build", "```bash", "# not a heading", "```", "### Flags"]
    out = readme_md.shift_headings(readme_md.drop_title(lines))
    assert out == ["### Build", "```bash", "# not a heading", "```", "#### Flags"]


def test_rewrite_links():
    lines = ["See [src](src/main.c), [docs](../docs/), ![img](img/a.png), [top](#build) and "
             "[web](https://example.com) but not `[x](y.c)`."]
    out = readme_md.rewrite_links(lines, "apps/ble/demo", *BASES)[0]
    assert "[src](https://blob/x/apps/ble/demo/src/main.c)" in out
    assert "[docs](https://tree/x/apps/ble/docs)" in out
    assert "![img](https://raw/x/apps/ble/demo/img/a.png)" in out
    assert "and top" not in out and " top and" in out
    assert "[web](https://example.com)" in out
    assert "`[x](y.c)`" in out


def test_normalize_lists_nesting_and_blank_lines():
    lines = ["Intro text", "- one", "  - nested", "    deeper text", "- two", "", "Table:", "| a | b |"]
    out = readme_md.normalize_lists(lines)
    assert out == ["Intro text", "", "- one", "    - nested", "        deeper text", "- two", "",
                   "Table:", "", "| a | b |"]


def test_normalize_lists_moves_fences_with_the_item():
    lines = ["- step", "  ```bash", "  make", "  ```", "after"]
    out = readme_md.normalize_lists(lines)
    assert out[:4] == ["- step", "    ```bash", "    make", "    ```"]


def test_apply_rules_and_stale_rule():
    text = "ipronet_up MyNet secret123\n"
    rule = {"pattern": r"^(ipronet_up)[ \t]+\S+[ \t]+\S+", "repl": r"\1 <ssid> <psk>"}
    assert readme_md.apply_rules(text, [rule]) == "ipronet_up <ssid> <psk>\n"
    with pytest.raises(readme_md.StaleRule):
        readme_md.apply_rules("nothing here\n", [rule])


def test_normalize_serial_keeps_placeholder():
    text = "open /dev/cu.usbserial-2120 or /dev/cu.usbserial-XXXX"
    assert readme_md.normalize_serial(text) == "open /dev/cu.usbserial-XXXX or /dev/cu.usbserial-XXXX"


# ---------- doxy_md ----------

MEMBER = """<memberdef kind="function" id="f1">
  <name>gpio_write</name>
  <briefdescription><para>Set the output <computeroutput>level</computeroutput>.</para></briefdescription>
  <detaileddescription>
    <para>See <ref refid="f2" kindref="member">gpio_read()</ref> and <ulink url="https://x.io">docs</ulink>; a &lt;b&gt; tag.</para>
    <para><parameterlist kind="param"><parameteritem>
      <parameternamelist><parametername>pin</parametername></parameternamelist>
      <parameterdescription><para>GPIO number.</para></parameterdescription>
    </parameteritem></parameterlist>
    <simplesect kind="return"><para>0 on success.</para></simplesect>
    <simplesect kind="note"><para>Not reentrant.</para></simplesect></para>
  </detaileddescription>
</memberdef>"""


def test_parse_doc():
    member = ET.fromstring(MEMBER)
    doc = doxy_md.parse_doc(member, lambda refid: "#gpio_read" if refid == "f2" else None)
    assert doc.brief == "Set the output `level`."
    assert doc.body == ["See [`gpio_read()`](#gpio_read) and [docs](https://x.io); a &lt;b&gt; tag."]
    assert doc.params == [("pin", "GPIO number.")]
    assert doc.returns == "0 on success."
    assert doc.sections == [("note", "Not reentrant.")]


def test_code_listing_keeps_spaces_and_order():
    listing = ET.fromstring('<programlisting><codeline><highlight class="normal">int<sp/>x<sp/>=<sp/>'
                            '<ref refid="a">f</ref>(1);</highlight></codeline></programlisting>')
    assert doxy_md.code_listing(listing) == "```c\nint x = f(1);\n```"


# ---------- gen_common ----------

def test_replace_block_and_nav_lines():
    text = "a\n<!-- BEGIN generated: t -->\nold\n<!-- END generated: t -->\nb\n"
    out = gen_common.replace_block(text, "t", "new", ("<!-- ", " -->"))
    assert out == "a\n<!-- BEGIN generated: t -->\nnew\n<!-- END generated: t -->\nb\n"
    with pytest.raises(KeyError):
        gen_common.replace_block(text, "missing", "x", ("<!-- ", " -->"))
    assert gen_common.nav_lines([("G", [("p", "p.md")])], "  ") == ['  - "G":', '      - "p": p.md']


def test_table_escapes_pipes_and_newlines():
    assert gen_common.table(["a"], [["x | y\nz"]]) == "| a |\n|---|\n| x \\| y z |"


# ---------- gen_documents ----------

def doc(access, files=None):
    return {"id": "d", "title": {"zh": "文件", "en": "Doc"}, "version": "V1", "languages": ["zh-TW", "en"],
            "summary": {"zh": "s", "en": "s"}, "access": access, "files": files or {}}


def test_documents_validation():
    assert gen_documents.validate({"categories": [{"documents": [doc("request")]}]}) == []
    errors = gen_documents.validate({"categories": [{"documents": [doc("public", {"en": "https://x"})]}]})
    assert errors == ["d: public but no file for zh-TW"]


def test_documents_availability():
    assert gen_documents.availability(doc("request"), "zh") == "向 INTELPRO 索取"
    public = doc("public", {"zh-TW": "https://z.pdf", "en": "https://e.pdf"})
    assert gen_documents.availability(public, "en") == "[zh-TW](https://z.pdf) / [English](https://e.pdf)"


# ---------- gen_redirects ----------

BUILT = {
    "get-started/": '<h2 id="intro">x</h2>',
    "get-started/flash/": '<h2 id="flashing">x</h2><h2 id="overview">x</h2>',
    "": "<h1>home</h1>",
}


def read_built(url):
    return BUILT.get(url)


def test_page_url():
    assert gen_redirects.page_url("index.md") == ("", "")
    assert gen_redirects.page_url("get-started/index.md") == ("get-started/", "")
    assert gen_redirects.page_url("guides/ble.md#le-audio") == ("guides/ble/", "le-audio")
    with pytest.raises(ValueError):
        gen_redirects.page_url("guides/ble/")


def test_resolve_keeps_ids_follows_map_and_honours_top():
    entry = {"to": "get-started/index.md",
             "anchors": {"flashing": "get-started/flash.md", "overview": "get-started/flash.md#", "x": "index.md"}}
    default, anchors = gen_redirects.resolve("p", entry, ["intro", "flashing", "overview", "gone"], "/b/", read_built)
    assert default == "/b/get-started/"
    assert anchors == {"intro": "/b/get-started/#intro", "flashing": "/b/get-started/flash/#flashing",
                       "overview": "/b/get-started/flash/", "x": "/b/"}


def test_redirect_validation():
    sections = {"p": ["flashing"], "q": []}
    data = {"pages": {"p": {"to": "get-started/index.md",
                            "anchors": {"flashing": "get-started/flash.md#nope", "typo": "index.md"}},
                      "r": {"to": "missing.md"}}}
    errors = gen_redirects.validate(data, sections, read_built)
    assert "q: old page has no redirect entry" in errors
    assert "r: no such page in legacy/" in errors
    assert "p#typo: the old page has no such section" in errors
    assert "p #flashing: get-started/flash.md#nope has no heading #nope" in errors
    assert "r to: missing.md is not a built page" in errors


def test_redirect_page_escapes_and_falls_back():
    redirect = gen_redirects.Redirect("p", "/b/x/", {"a": "/b/y/#a"}, "A <b> & c")
    page = gen_redirects.render(redirect, "en", "https://h.io")
    assert '<link rel="canonical" href="https://h.io/b/x/">' in page
    assert '<meta http-equiv="refresh" content="0; url=/b/x/">' in page
    assert 'var anchors = {"a": "/b/y/#a"};' in page
    assert "A &lt;b&gt; &amp; c" in page and "A <b>" not in page
