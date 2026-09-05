# webtome (development)

CLI that turns web feeds/articles into print-ready 6×9 book PDFs, organized in
volumes. Read `docs/architecture.md` before touching the pipeline.

## Commands

- `uv sync` then `uv run webtome --help`
- Manual e2e check: `uv run webtome init /tmp/lib && cd /tmp/lib`, add a feed,
  `sync --limit 3`, `volume new`, `volume fill volume-01`, `build volume-01`,
  then open `dist/volume-01.pdf` and eyeball the title page, TOC, and a
  chapter opener.
- System prerequisite for builds: `pandoc` (Typst is bundled via the `typst`
  wheel).

## Rules

- The library a user creates with `webtome init` is plain Markdown + YAML;
  never introduce state that is not a file in the library.
- `templates/book.typ` is the single source of truth for typography and page
  geometry; build code only assembles Typst markup, it never styles.
- Do not enable trafilatura's `deduplicate` option (drops repeated paragraphs).
- Printed volumes (`status: printed`) are frozen; no code path may mutate them.
- Everything in this repo is English (code, docs, comments, commits).
