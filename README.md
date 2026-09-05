# webtome

**Turn the web you love into books you can hold.**

webtome collects articles from your feeds (or any URL), keeps them as clean
Markdown, and typesets them into print-ready PDF books: real 6"×9" paperbacks
you can print at home or through any print-on-demand service (Lulu, Amazon KDP,
a local print shop). When you have printed a volume, new articles accumulate
for Volume 2, then Volume 3, and so on: your personal, ever-growing anthology
of the web.

It is built to be driven by AI agents (Claude Code, Codex, anything that can
run a CLI): point an agent at your library and say *"organize the next volume
by theme and build it"*. But every step also works by hand.

```
feeds / URLs  ──▶  articles/*.md  ──▶  volumes/volume-NN  ──▶  dist/volume-NN.pdf
   (ingest)         (your archive)        (curation)             (print-ready)
```

## Why

Read-later apps pile up unread tabs. Paper does not. Existing tools cover only
fragments of the journey: [percollate](https://github.com/danburzo/percollate)
turns pages into PDFs, [RSS2Ebook](https://github.com/MrPike/RSS2Ebook) makes
ebooks from a feed, blog2print is a paid service locked to specific platforms.
None of them give you a **curated, versioned library** where articles arrive
continuously, get organized into well-typeset volumes, and the archive
remembers what is already on your shelf.

## Install

Prerequisites: [uv](https://docs.astral.sh/uv/) and
[pandoc](https://pandoc.org/installing.html) (`sudo apt install pandoc` /
`brew install pandoc`). The Typst compiler is bundled as a Python wheel, so
there is nothing else to install.

```bash
uv tool install git+https://github.com/mazzasaverio/webtome
```

## Quickstart

```bash
webtome init my-library && cd my-library

# Follow a blog (feed URL, or the site URL: the feed is auto-discovered)
webtome source add https://simonwillison.net/atom/everything/

# Fetch new articles (run it whenever you like, or from cron)
webtome sync --limit 10

# Or grab any single article
webtome add https://example.com/some-great-essay

# Make a book
webtome volume new --title "Essays I Want on Paper"
webtome volume fill volume-01        # everything not yet in a volume
webtome build volume-01              # -> dist/volume-01.pdf, ready to print

# Printed it? Freeze it. New articles now accumulate for volume 2.
webtome volume mark-printed volume-01
webtome volume new
```

## Your library is just files

`webtome init` creates a plain-files workspace you can (and should) put under
git:

```
my-library/
├── webtome.yaml          # library name, curator, defaults
├── sources.yaml          # the feeds you follow
├── articles/             # one Markdown file per article, YAML frontmatter
│   └── how-i-write-2026-01-12.md
├── volumes/
│   └── volume-01/
│       └── volume.yaml   # title + ordered article list (or sections)
├── dist/                 # built PDFs (gitignored)
└── AGENTS.md             # workflow guide for AI agents (and humans)
```

A `volume.yaml` can be flat or organized into parts:

```yaml
number: 1
title: Essays I Want on Paper
subtitle: Volume 1
status: draft            # -> printed, once it is on your shelf
sections:
  - title: On Writing
    articles: [how-i-write, why-blogs-matter]
  - title: On Tools
    articles: [the-case-for-plain-text]
```

Everything is human-readable, diffable, and editable by hand or by an agent.
Nothing is locked in: your articles are Markdown, your book definitions are
YAML.

## Using it with AI agents

`webtome init` drops an `AGENTS.md` (plus `CLAUDE.md`) into your library
describing the layout, the commands, and the curation rules. Open the library
in Claude Code and try:

- *"Sync my feeds, then tell me what came in this week."*
- *"Organize the 23 unassigned articles into a coherent volume 2 with thematic
  sections, strongest opener first, and build the PDF."*
- *"This article's extraction has navigation junk at the top, clean it up."*

The agent curates; the CLI guarantees the mechanical parts (fetching,
deduplication by URL, typesetting, volume bookkeeping) stay correct.

## Printing the PDF

Volumes are typeset for a **6"×9" (152×229 mm) trim size**, the most common
paperback format, with mirrored inside/outside margins and no bleed (text-only
interiors do not need it). That means the PDF is accepted as-is by:

- **Home / office printing**: print 2 pages per sheet, or just print A5-ish.
- **Local print shops**: ask for "perfect bound, 6×9, cream paper".
- **[Lulu](https://www.lulu.com/)**: print-on-demand from one copy, private by
  default.
- **Amazon KDP**: works too, but remember these books are for *personal use*;
  do not publish other people's articles for sale.

See [docs/printing.md](docs/printing.md) for details (page counts, paper,
covers).

**Copyright note**: webtome is a tool for personal archiving and reading, like
printing pages from your browser. The articles remain their authors' property.
Each chapter records its source URL and every volume ends with a full source
list. Do not sell or redistribute books made from content you do not own.

## Roadmap

- [ ] Images in articles (downloaded, grayscale, 300 DPI checked)
- [ ] EPUB output alongside PDF
- [ ] More trim sizes and themes (A5, 5.5"×8.5"; font choices)
- [ ] Cover generator (front/back/spine sized from page count)
- [ ] `webtome import` from Pocket/Instapaper/Omnivore exports
- [ ] Optional agent-written volume introductions and section notes

Contributions welcome: this project is deliberately small and file-based so it
is easy to extend.

## Development

```bash
git clone https://github.com/mazzasaverio/webtome && cd webtome
uv sync
uv run webtome --help
```

See [docs/architecture.md](docs/architecture.md) for how the pieces fit.

## License

[MIT](LICENSE)
