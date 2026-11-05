#!/bin/sh
# Build every language: zh-TW into site/, then English, Simplified Chinese and
# Japanese into site/en/, site/zh-cn/ and site/ja/ (zh-TW first: its build cleans site/).
#   ENGINE=zensical (default)  primary builder
#   ENGINE=material            fallback builder (Material for MkDocs on MkDocs 1.x)
# Both run in strict mode, so any warning fails the build. Afterwards the old
# Jekyll URLs get redirect pages (tools/gen_redirects.py, data/redirects.yml).
set -eu
cd "$(dirname "$0")/.."
[ -f .venv/bin/activate ] && . .venv/bin/activate

ENGINE=${ENGINE:-zensical}
rm -rf site
case "$ENGINE" in
  zensical)
    for lang in zh en zh-cn ja; do zensical build --strict -f "mkdocs.$lang.yml"; done
    ;;
  material)
    for lang in zh en zh-cn ja; do mkdocs build --strict -f "mkdocs.$lang.yml"; done
    ;;
  *)
    echo "unknown ENGINE '$ENGINE' (zensical | material)" >&2
    exit 2
    ;;
esac
# Old Jekyll URLs (getting-started.html, en/faq.html, ...) redirect to the new pages.
python3 tools/gen_redirects.py
echo "built with $ENGINE: $(find site -name '*.html' | wc -l | tr -d ' ') pages in site/"
