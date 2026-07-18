"""Scaffold a new library workspace."""

from __future__ import annotations

from pathlib import Path

from .library import CONFIG_FILE, SOURCES_FILE, LibraryError

_CONFIG_TEMPLATE = """\
# webtome library configuration
name: {name}
# Shown as "Curated by ..." on the title page. Uncomment and set:
# author: Your Name
language: en
"""

_SOURCES_TEMPLATE = """\
# Feeds this library follows. Managed by 'webtome source add', or edit by hand.
feeds: []
"""

_GITIGNORE = """\
dist/
"""

_AGENTS_TEMPLATE = """\
# Agent guide for this webtome library

This directory is a webtome library: a personal archive of web articles that
gets curated into print-ready books ("volumes"). You can drive the whole
workflow with the `webtome` CLI.

## Layout

- `sources.yaml` - followed feeds
- `articles/*.md` - one article per file, YAML frontmatter + Markdown body
- `volumes/volume-NN/volume.yaml` - which articles go in each book, in order
- `dist/` - built PDFs (never commit)

## Commands

- `webtome sync` - fetch new articles from all feeds
- `webtome add <url>` - grab a single article
- `webtome list --unassigned` - articles not yet in any volume
- `webtome volume new --title "..."` - start the next volume
- `webtome volume add <volume> <slug>...` - append articles in reading order
- `webtome build <volume>` - produce `dist/<volume>.pdf` (6x9in, print-ready)
- `webtome volume mark-printed <volume>` - freeze a volume once printed

## Typical curation tasks

When asked to "organize the next volume":
1. Run `webtome list --unassigned` and read the articles in `articles/`.
2. Group them by theme. Propose an order that reads well (strong opener,
   related pieces adjacent, strong closer).
3. Create the volume, then either use `webtome volume add` for a flat book or
   edit `volume.yaml` to use thematic sections:

   ```yaml
   sections:
     - title: On Writing
       articles: [slug-one, slug-two]
     - title: On Tools
       articles: [slug-three]
   ```

4. Build it and report the PDF path and page count.

Rules:
- Never edit article bodies except to fix extraction glitches (leftover
  navigation text, broken tables); never rewrite the author's prose.
- Never reorder or edit a volume whose `status` is `printed`.
- Frontmatter `volume` must stay consistent with `volume.yaml`.
"""

_README_TEMPLATE = """\
# {name}

A [webtome](https://github.com/mazzasaverio/webtome) library: articles
collected from the web, curated into print-ready books.

- `webtome sync` fetches new articles from the feeds in `sources.yaml`
- `webtome build volume-01` produces a printable PDF in `dist/`

See `AGENTS.md` for the full workflow (also useful for humans).
"""


def init_library(directory: Path, name: str | None = None) -> Path:
    root = directory.expanduser().resolve()
    if (root / CONFIG_FILE).exists():
        raise LibraryError(f"{root} is already a webtome library.")
    root.mkdir(parents=True, exist_ok=True)
    library_name = name or root.name.replace("-", " ").replace("_", " ").title()

    (root / "articles").mkdir(exist_ok=True)
    (root / "volumes").mkdir(exist_ok=True)
    (root / CONFIG_FILE).write_text(_CONFIG_TEMPLATE.format(name=library_name), encoding="utf-8")
    (root / SOURCES_FILE).write_text(_SOURCES_TEMPLATE, encoding="utf-8")
    (root / ".gitignore").write_text(_GITIGNORE, encoding="utf-8")
    (root / "AGENTS.md").write_text(_AGENTS_TEMPLATE, encoding="utf-8")
    (root / "CLAUDE.md").write_text("See AGENTS.md.\n", encoding="utf-8")
    (root / "README.md").write_text(_README_TEMPLATE.format(name=library_name), encoding="utf-8")
    return root
