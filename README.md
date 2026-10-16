# IPRO SDK Documentation Website

Public documentation for the IPRO SDK, published on GitHub Pages:
<https://intelpro-inc.github.io/ipro-sdk-docs/>

The site is bilingual: Traditional Chinese at the site root, English under
`/en/`. Pages are Markdown, built with [Zensical](https://zensical.org/);
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) builds the
same sources in CI as a fallback.

> **Redesign in progress (branch `redesign`).** The previous hand-written
> Jekyll site lives in `legacy/` until every page has been migrated. Run
> `tools/stub_report.py` to see what is left.

## Structure

```
mkdocs.base.yml      shared settings: theme, Markdown extensions, release version (extra.release)
mkdocs.zh.yml        zh-TW site: nav, language, banner text → site/
mkdocs.en.yml        English site: same nav order and files → site/en/
docs/zh/, docs/en/   page sources; every page exists in both languages under the same path
overrides/           theme overrides: home page, release banner, brand CSS, language switch
tools/               build, preview and CI checks (see below)
legacy/              old Jekyll site, kept as migration source until cutover
```

The release version and date shown in the banner and on the home page come
from `extra.release` in `mkdocs.base.yml`. Change them there only.

## Build and preview

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
./tools/preview.sh            # build, then serve http://localhost:8000/ipro-sdk-docs/
ENGINE=material ./tools/build.sh   # fallback builder
```

Builds run in strict mode: a broken link, a missing anchor or a page left out
of the nav fails the build.

## Checks

| Tool | Checks |
|---|---|
| `tools/parity_check.py` | zh and en have the same pages, nav order, level-2 heading count and explicit heading ids |
| `tools/redline_check.py` | public-content rules (below) and Taiwan terminology on zh-TW pages (`tools/zh_tw_terms.yml`) |
| `tools/stub_report.py` | pages still marked `status: stub`, and legacy sections no page claims |
| `python -m pytest tools/tests` | unit tests for the tools above |

The red-line check also loads a **private** rule set (internal project,
customer and vendor names). It is never committed here: CI reads it from the
`REDLINE_RULES` repository secret, and maintainers keep a local copy in the SDK
repository (path in `tools/redline_check.py`). Findings from private rules
never print the matched text.

## Writing pages

1. Add the page under the same path in `docs/zh/` **and** `docs/en/`.
2. Register it in the `nav` of **both** `mkdocs.zh.yml` and `mkdocs.en.yml`, at the same position.
3. Give section headings explicit ids so links and the language switch keep working:
   `## 控制器配置 { #controller-variants }` ↔ `## Controller Configuration { #controller-variants }`.
4. Record where migrated content came from in front matter (`migrate_from:`), and
   remove `status: stub` once the page is written.
5. Run `./tools/preview.sh` and the checks above before committing.

## Content rules (public site)

- **Networking on IPRO7**: describe how it connects — Ethernet (RMII), or Wi-Fi
  through an IPRO6S companion over SDIO. Never present Wi-Fi as an IPRO7 feature,
  but do not headline its absence either (no banners or lead sentences about it).
- **IPRO6S (SDK V2.0.1)** is covered on its chip page, the release notes and the
  FAQ only; other pages do not repeat the pointer.
- **No internal or customer names.** Reference designs are described generically
  ("contact INTELPRO for availability").
- **Document the released SDK**, not the development tree. Anything not in the
  release is marked as such or as a roadmap item.
- **No internal infrastructure**: CI pipelines, issue trackers, internal hosts,
  local paths. Serial ports on macOS are written `/dev/cu.usbserial-XXXX`.

## Publishing

`.github/workflows/docs.yml` runs the checks and both builds on every push and
pull request. Pushes to `main` deploy the Zensical build to GitHub Pages, which
requires **Settings → Pages → Source = GitHub Actions** (switched at cutover).
