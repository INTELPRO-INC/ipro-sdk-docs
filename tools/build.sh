#!/bin/sh
# Build both languages: zh-TW into site/, English into site/en/.
#   ENGINE=zensical (default)  primary builder
#   ENGINE=material            fallback builder (Material for MkDocs on MkDocs 1.x)
# Both run in strict mode, so any warning fails the build.
set -eu
cd "$(dirname "$0")/.."
[ -f .venv/bin/activate ] && . .venv/bin/activate

ENGINE=${ENGINE:-zensical}
rm -rf site
case "$ENGINE" in
  zensical)
    zensical build --strict -f mkdocs.zh.yml
    zensical build --strict -f mkdocs.en.yml
    ;;
  material)
    mkdocs build --strict -f mkdocs.zh.yml
    mkdocs build --strict -f mkdocs.en.yml
    ;;
  *)
    echo "unknown ENGINE '$ENGINE' (zensical | material)" >&2
    exit 2
    ;;
esac
echo "built with $ENGINE: $(find site -name '*.html' | wc -l | tr -d ' ') pages in site/"
