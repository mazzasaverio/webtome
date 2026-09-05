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
Git:

```
my-library/
├── webtome.yaml          # nome libreria, curatore, valori predefiniti
├── sources.yaml          # i feed che segui
├── articles/             # un file Markdown per articolo, frontmatter YAML
│   └── how-i-write-2026-01-12.md
├── volumes/
│   └── volume-01/
│       └── volume.yaml   # titolo + elenco ordinato di articoli (o sezioni)
├── dist/                 # PDF generati (ignorati da Git)
└── AGENTS.md             # guida al flusso per agenti AI e persone
```

Un `volume.yaml` può essere piatto oppure organizzato in parti:

```yaml
number: 1
title: Essays I Want on Paper
subtitle: Volume 1
status: draft            # -> printed, una volta sul tuo scaffale
sections:
  - title: On Writing
    articles: [how-i-write, why-blogs-matter]
  - title: On Tools
    articles: [the-case-for-plain-text]
```

Tutto è leggibile, confrontabile e modificabile a mano o da un agente. Non c'è
alcun vincolo: gli articoli sono Markdown e le definizioni dei libri sono YAML.

## Uso con gli agenti AI

`webtome init` inserisce un `AGENTS.md`, insieme a `CLAUDE.md`, nella libreria:
descrive struttura, comandi e regole di curatela. Apri la libreria in Claude Code
e prova:

- *"Sincronizza i miei feed e dimmi cosa è arrivato questa settimana."*
- *"Organizza i 23 articoli non assegnati in un coerente volume 2 con sezioni
  tematiche, l'apertura più forte per prima, e genera il PDF."*
- *"L'estrazione di questo articolo contiene elementi di navigazione all'inizio, ripuliscila."*

L'agente cura i contenuti; la CLI garantisce che le parti meccaniche, recupero,
deduplicazione per URL, composizione e gestione dei volumi, restino corrette.

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
