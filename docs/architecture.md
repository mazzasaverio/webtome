# Architettura

webtome è deliberatamente piccolo: una CLI sottile su un workspace di semplici
file, con due componenti esterni, pandoc e il compilatore Typst incluso.

## La pipeline

```
                 ┌─────────────┐
 feeds/URLs ───▶ │   ingest    │  feedparser + trafilatura
                 └─────┬───────┘
                       ▼
                 articles/*.md          Markdown + YAML frontmatter
                       │
                       ▼
                 ┌─────────────┐
                 │  curatela    │  persone e/o agenti modificano volume.yaml
                 └─────┬───────┘
                       ▼
                 volumes/volume-NN/volume.yaml
                       │
                       ▼
                 ┌─────────────┐
                 │   build     │  pandoc (md -> typst) + typst wheel (typst -> pdf)
                 └─────┬───────┘
                       ▼
                 dist/volume-NN.pdf     interno 6"x9" pronto per la stampa
```

## Decisioni progettuali

**File invece di database.** La libreria è Markdown + YAML in una directory.
Questo rende l'intero stato versionabile con Git, modificabile a mano o da agenti
e senza vincoli. La deduplicazione non richiede un indice: un articolo è noto se
il `source_url` di un file corrisponde.

**La curatela è dati, non codice.** Un libro è un `volume.yaml` che elenca slug
in ordine di lettura, facoltativamente raggruppati in sezioni. Riorganizzare un
libro significa modificare dieci righe YAML. È ciò che rende il progetto adatto
agli agenti: il lavoro creativo, selezione, raggruppamento e ordine, è proprio
quello in cui gli LLM sono efficaci e avviene in un solo piccolo file.

**Typst invece di LaTeX.** L'interno è composto da Typst: output di qualità LaTeX,
compilazione in millisecondi e, soprattutto, disponibilità come wheel Python
autosufficiente nel pacchetto `typst`. L'utente installa quindi solo `uv tool install
webtome` e pandoc. Pandoc converte il corpo Markdown di ogni articolo in markup Typst;
`templates/book.typ` fornisce la struttura del libro, frontespizio, colophon, indice,
aperture dei capitoli e appendice delle fonti.

**I volumi sono storia append-only.** Quando un volume è `printed`, è congelato;
`webtome volume fill` recupera solo articoli il cui frontmatter non ha `volume`.
Lo scaffale cresce in modo monotono: volume 1, volume 2 e così via.

**L'estrazione usa trafilatura.** Ha il miglior compromesso precisione/recall tra
gli estrattori di contenuti open source e produce Markdown direttamente. L'HTML
della voce feed è il fallback quando il recupero di una pagina fallisce o non
restituisce nulla. Non abilitare l'opzione `deduplicate` di trafilatura: può
eliminare silenziosamente paragrafi ripetuti in modo legittimo.

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
