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

## Mappa del codice

| File | Responsabilità |
|---|---|
| `src/webtome/cli.py` | CLI Typer; tutte le interazioni utente |
| `src/webtome/library.py` | Modello workspace: configurazione, articoli, volumi, I/O frontmatter |
| `src/webtome/ingest.py` | Sincronizzazione feed, recupero singolo URL, scoperta automatica feed |
| `src/webtome/build.py` | volume.yaml -> main.typ -> PDF |
| `src/webtome/scaffold.py` | Template `webtome init`, incluso l'AGENTS.md della libreria |
| `src/webtome/templates/book.typ` | Il libro: geometria pagina, tipografia, parti iniziali e finali |

## Punti di estensione

- **Nuovi formati e temi**: parametrizza `book.typ`, dimensione pagina e font, da
  `webtome.yaml`; la build passa già la configurazione.
- **EPUB**: stesso assemblaggio dei capitoli, con pandoc `-t epub3` al posto del
  percorso Typst.
- **Immagini**: scaricale durante l'acquisizione in `articles/assets/<slug>/`, riscrivi
  i riferimenti Markdown, lascia che pandoc/Typst le incorpori e verifica 300 DPI al
  formato di stampa.
- **Importatori** (Pocket, Instapaper, segnalibri browser): ogni sorgente che termina
  in `library.save_article(meta, body)` è valida.
