# Architecture

webtome is deliberately small: a thin CLI over a plain-files workspace, with
two external moving parts (pandoc and the bundled Typst compiler).

## The pipeline

```
                 ┌─────────────┐
 feeds/URLs ───▶ │   ingest    │  feedparser + trafilatura
                 └─────┬───────┘
                       ▼
                 articles/*.md          Markdown + YAML frontmatter
                       │
                       ▼
                 ┌─────────────┐
                 │  curation   │  humans and/or agents edit volume.yaml
                 └─────┬───────┘
                       ▼
                 volumes/volume-NN/volume.yaml
                       │
                       ▼
                 ┌─────────────┐
                 │   build     │  pandoc (md -> typst) + typst wheel (typst -> pdf)
                 └─────┬───────┘
                       ▼
                 dist/volume-NN.pdf     6"x9" print-ready interior
```

## Design decisions

**Files over databases.** The library is Markdown + YAML in a directory. This
makes the whole state git-versionable, hand-editable, agent-editable, and
impossible to lock in. Deduplication needs no index: an article is "known" if
any file's `source_url` matches.

**Curation is data, not code.** A book is a `volume.yaml` listing slugs in
reading order, optionally grouped into sections. Reorganizing a book is
editing a ten-line YAML file. This is also what makes the project agent-first:
the creative work (selecting, grouping, ordering) is exactly the part LLMs are
good at, and it happens entirely in one small file.

**Typst over LaTeX.** The interior is typeset by Typst: LaTeX-quality output,
milliseconds to compile, and, decisively, available as a self-contained Python
wheel (the `typst` package), so users install nothing but `uv tool install
webtome` plus pandoc. Pandoc converts each article's Markdown body to Typst
markup; `templates/book.typ` provides the book frame (title page, colophon,
TOC, chapter openers, sources appendix).

**Volumes are append-only history.** Once a volume is `printed` it is frozen;
`webtome volume fill` only ever pulls articles whose frontmatter has no
`volume`. The shelf grows monotonically: volume 1, volume 2, ...

**Extraction is trafilatura.** It has the best precision/recall trade-off of
the open-source content extractors and outputs Markdown directly. The feed
entry's own HTML is the fallback when a page fetch fails or yields nothing.
Note: do not enable trafilatura's `deduplicate` option; it can silently drop
legitimately repeated paragraphs.

## Code map

| File | Responsibility |
|---|---|
| `src/webtome/cli.py` | Typer CLI; all user interaction |
| `src/webtome/library.py` | Workspace model: config, articles, volumes, frontmatter I/O |
| `src/webtome/ingest.py` | Feed sync, single-URL fetch, feed auto-discovery |
| `src/webtome/build.py` | volume.yaml -> main.typ -> PDF |
| `src/webtome/scaffold.py` | `webtome init` templates (incl. the library AGENTS.md) |
| `src/webtome/templates/book.typ` | The book: page geometry, typography, front/back matter |

## Extension points

- **New trim sizes / themes**: parameterize `book.typ` (page size, fonts) from
  `webtome.yaml`; the build already passes config through.
- **EPUB**: same chapter assembly, pandoc `-t epub3` instead of the Typst path.
- **Images**: download at ingest time into `articles/assets/<slug>/`, rewrite
  Markdown refs, let pandoc/Typst embed them; validate 300 DPI at print size.
- **Importers** (Pocket, Instapaper, browser bookmarks): anything that ends in
  `library.save_article(meta, body)` is a valid source.
