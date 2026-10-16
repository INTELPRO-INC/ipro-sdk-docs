#!/bin/sh
# Build, then serve the site at http://localhost:${PORT:-8000}/ipro-sdk-docs/
# (the same base path as GitHub Pages, so absolute links and the language
# switch behave as in production).
set -eu
cd "$(dirname "$0")/.."
./tools/build.sh
mkdir -p .preview
ln -sfn ../site .preview/ipro-sdk-docs
printf '<meta http-equiv="refresh" content="0; url=/ipro-sdk-docs/">\n' > .preview/index.html
[ -f .venv/bin/activate ] && . .venv/bin/activate
exec python3 -m http.server "${PORT:-8000}" --bind 127.0.0.1 --protocol HTTP/1.1 --directory .preview
