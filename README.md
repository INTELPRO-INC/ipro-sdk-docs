# IPRO SDK Documentation Website

Public documentation site for the IPRO SDK, hosted on GitHub Pages:
<https://intelpro-inc.github.io/ipro-sdk-docs/>

The site is bilingual — Traditional Chinese pages live at the repository root,
English pages under `en/`. Every `*.html` page at the root has a same-named
counterpart in `en/`.

The current documentation baseline is **IPRO-SDK-V2.0.1**, released
**2026-09-09** (`VERSION.txt`), for IPRO7 and IPRO6S. Verify availability
against the release files and application configurations, not just its README.

Windows setup covers **Online Installer 3.4.0** and **Extension 3.3.0**,
with retained instructions for the fixed 3.3.0 installer. As checked on
2026-09-10, `packages/index.json` still selects SDK **1.2.1**; it does not
yet register 2.0.1. Link directly to the V2.0.1 release for the latest SDK,
and do not imply the installer's `latest` option installs it.

## 📁 Structure

```
ipro-sdk-docs/
├── _config.yml           # Jekyll configuration + navigation (single source of truth)
├── _layouts/
│   └── default.html      # Main layout (navbar, release notice, footer)
├── assets/
│   ├── css/site.css      # Custom styles
│   ├── js/main.js        # Navigation / UI behavior
│   └── favicon.svg
├── index.html            # Home (zh-TW)
├── *.html                # Documentation pages (zh-TW)
└── en/*.html             # English counterparts (same filenames)
```

Navigation is defined once in `_config.yml` (`nav` / `nav_en`) and rendered by
`_layouts/default.html`. To add or remove a page from the menus, edit
`_config.yml` only.

## 🛠️ Local Preview

```bash
bundle install
bundle exec jekyll serve
# open http://localhost:4000/ipro-sdk-docs/
```

## ✍️ Updating Documentation

1. Edit the Chinese page and its English counterpart in the same change.
2. Keep section anchor `id`s identical between the zh and en versions.
3. Preview locally, then commit the **specific files you changed** and push:

```bash
git add index.html en/index.html
git commit -m "docs(index): describe the change"
git push
```

> ⚠️ Never use `git add .` in this repository. Only `README.md` and the site
> pages belong here — working notes and internal documents must not be
> committed. Internal write-ups belong in the SDK repository under
> `docs/internal-notes/`.

## ✅ Content Rules (public site)

- **IPRO7 has no built-in Wi-Fi.** Network connectivity is provided by the
  IPRO6 companion chip over SDIO. Never describe Wi-Fi as an IPRO7 feature.
- **No customer or internal project codenames.** Reference designs are
  described generically ("contact INTELPRO for availability").
- **Document the Release SDK scope** (see `release_notice` in `_config.yml`),
  not the internal development tree. Features outside the release are marked
  as roadmap items.
- **No internal infrastructure details** (CI pipelines, issue trackers,
  internal hostnames or ports).

## 🎨 Adding a New Page

1. Create `your-page.html` at the root (zh-TW) **and** `en/your-page.html`.
2. Add front matter to both:
   ```yaml
   ---
   layout: default
   title: Page Title
   ---
   ```
3. Register the page in `_config.yml` under `nav` and `nav_en`.
4. Add a sidebar TOC (`doc-sidebar`) for long pages, matching existing pages.
