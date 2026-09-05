# webtome

**Trasforma il web che ami in libri da tenere in mano.**

webtome raccoglie gli articoli dai tuoi feed, o da qualsiasi URL, li conserva
come Markdown pulito e li compone in PDF di libri pronti per la stampa: veri
tascabili 6"×9" da stampare a casa o con un servizio print-on-demand come Lulu,
Amazon KDP o una tipografia locale. Quando stampi un volume, i nuovi articoli si
accumulano per il Volume 2, poi il Volume 3 e così via: la tua antologia del web,
personale e in costante crescita.

È progettato per essere guidato da agenti AI, come Claude Code, Codex o qualunque
strumento possa eseguire una CLI: indica a un agente la libreria e chiedi
*"organizza il prossimo volume per tema e costruiscilo"*. Ogni passaggio funziona
anche manualmente.

```
feeds / URLs  ──▶  articles/*.md  ──▶  volumes/volume-NN  ──▶  dist/volume-NN.pdf
 (acquisizione)      (il tuo archivio)    (curatela)          (pronto per la stampa)
```

## Perché

Le app di lettura differita accumulano schede non lette. La carta no. Gli strumenti
esistenti coprono solo frammenti del percorso: [percollate](https://github.com/danburzo/percollate)
trasforma pagine in PDF, [RSS2Ebook](https://github.com/MrPike/RSS2Ebook) crea ebook
da un feed, blog2print è un servizio a pagamento vincolato a piattaforme specifiche.
Nessuno offre una **libreria curata e versionata** in cui gli articoli arrivano in
modo continuo, vengono organizzati in volumi ben composti e l'archivio ricorda cosa
è già sul tuo scaffale.

## Installazione

Prerequisiti: [uv](https://docs.astral.sh/uv/) e
[pandoc](https://pandoc.org/installing.html) (`sudo apt install pandoc` /
`brew install pandoc`). Il compilatore Typst è incluso come wheel Python, quindi
non serve installare altro.

```bash
uv tool install git+https://github.com/mazzasaverio/webtome
```

## Avvio rapido

```bash
webtome init my-library && cd my-library

# Segui un blog (URL del feed o del sito: il feed viene scoperto automaticamente)
webtome source add https://simonwillison.net/atom/everything/

# Recupera nuovi articoli (quando preferisci o tramite cron)
webtome sync --limit 10

# Oppure recupera un singolo articolo
webtome add https://example.com/some-great-essay

# Crea un libro
webtome volume new --title "Essays I Want on Paper"
webtome volume fill volume-01        # tutto ciò che non è ancora in un volume
webtome build volume-01              # -> dist/volume-01.pdf, pronto per la stampa

# Lo hai stampato? Congelalo. I nuovi articoli ora si accumulano per il volume 2.
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
