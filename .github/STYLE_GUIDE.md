# Writing Style Guide

How pages on this site are written. Applies to both languages. Read the
content rules in `README.md` first; this guide covers structure and wording.

## Principles

1. **Readers come with a task.** An embedded engineer wants to bring up a
   board, build a sample, add BLE, or find a config key. Every page serves one
   task or one topic, says what it is for in the first paragraph, and puts
   conclusions before background.
2. **Everything is checked against the released SDK.** Commands, paths,
   `CONFIG_*` keys, app names, counts and versions must exist in the current
   release package. If something cannot be confirmed, leave it out.
   Things the release does not ship are stated as such:
   「未包含於 V2.1.0，請洽 INTELPRO。」 / "Not included in V2.1.0; contact INTELPRO."
3. **One fact, one place.** Version-specific notes about older releases (for
   example IPRO6S on V2.0.1) live on their own page; other pages link to it.
   Release version and date come from `extra.release`; in prose, write the
   version only where the sentence depends on it.
4. **Runnable over descriptive.** Prefer a command, its expected output and
   how to tell it worked, over a paragraph describing what the command does.
5. **Short.** No preambles ("本節將介紹…", "In this section we will…"), no
   marketing adjectives, no repeating the heading in the first sentence.

## Page types

### Task page (Get Started, Tutorials)

```
# <Goal as a title>
One-paragraph goal: what you will have at the end, on which board.
## 前置需求 / Prerequisites { #prerequisites }
## Steps, wrapped in <div class="ipro-steps" markdown> … </div>
   each step: action → command → expected result
## 確認結果 / Verify { #verify }
## 疑難排解 / Troubleshooting { #troubleshooting }   (symptom → cause → fix)
## 下一步 / Next steps { #next-steps }
```

### Guide page (Guides)

```
# <Topic>
Two or three sentences: what it is, when to use it, what the SDK provides.
!!! abstract "重點" / "At a glance"   (3–5 bullets: supported / not included / key config)
## Architecture / how it fits
## Configuration (exact CONFIG_* keys and values, as a table or an .config block)
## Usage (code taken from or matching a shipped app; name the app)
## Limitations in this release
## Related examples and documents
```

### Board page (Hardware → Boards)

Follow `hardware/boards/reef-evk.md`: intro, `ipro-facts` strip, on-board
features table, warning admonition for power-on requirements, quick start
steps (per-OS tabs for flashing), out-of-box firmware, supported examples,
SDK board support, related documents.

### Chip page (Hardware → Chips)

Overview, key specifications table (public specifications only), SDK support
in this release, boards that carry the chip, related documents.

### Reference page (Reference)

Tables first. Commands as `command` / options / example. Alphabetical or
grouped by task; no narrative.

### Section index (`<section>/index.md`)

One sentence of purpose, then grid cards (`<div class="grid cards" markdown>`)
linking every page in the section with a one-line description.

## Markdown conventions

- **Front matter**: `title`, `description` (one sentence), and `migrate_from`
  (legacy sources). Remove `status: stub` when the page is written.
- **Headings**: one `#` title per page. Every `##` has an explicit id:
  `## 控制器配置 { #controller-variants }`. The zh and en pages use the same ids
  in the same order. Reuse the legacy section id when the content corresponds.
  Ids are lowercase ASCII with hyphens.
- **Links**: relative links to `.md` files. Link to another section's page
  without an anchor unless you know the anchor exists.
- **Code**: always give a language (`bash`, `c`, `ini`, `text`, `powershell`);
  add `title="…"` when the block is a file or a named example.
- **OS differences**: content tabs (`=== "macOS"`, `=== "Linux"`, `=== "Windows"`).
- **Admonitions**: `note` (extra information), `tip` (shortcut), `warning`
  (can break the board or the build), `danger` (data loss or hardware damage),
  `info` (availability, "contact INTELPRO"), `abstract` (at-a-glance summary).
- **Diagrams**: Mermaid for flows and sequences; `ipro-stack` blocks for layer
  diagrams; tables for matrices. No ASCII art.
- **Components** available in `overrides/assets/stylesheets/components.css`:
  `ipro-steps`, `ipro-facts`, `ipro-stack`, `ipro-badge`, grid cards.
- **Placeholders**: serial ports `/dev/cu.usbserial-XXXX` (macOS),
  `/dev/ttyUSB0` (Linux), `COM5` (Windows); SDK root `<SDK>`.
- **Examples default to the IPRO7AI Reef EVK** where a board must be chosen;
  state facts about other boards as they are.

## zh-TW wording

- Taiwan terminology; `tools/zh_tw_terms.yml` is enforced. Preferred forms:
  建置 (build)、設定 (configuration)、燒錄、韌體、主控台、序列埠、腳位、周邊、
  協定堆疊、範例、預設、執行緒、記憶體、位址、計時器、重置、即時。
- Address the reader as 「您」 only when unavoidable; prefer imperative steps
  (「執行」「確認」「接上」).
- Full-width punctuation in Chinese text （，。：；（）「」）; half-width inside
  code and English terms. Put a space between Chinese and Latin letters or
  numbers: 「支援 IPRO7 EVB」「2 MB Flash」.
- Keep product, API and file names in their original form: `bt_enable()`,
  `CONFIG_BT_CONN`, IPRO7AI Reef EVK, IntelProCube.

## English wording

- US spelling, plain and direct; second person ("you") and imperatives.
- Page titles in Title Case; section headings in sentence case.
- Write natural English for the same content and structure; do not translate
  sentence by sentence.
