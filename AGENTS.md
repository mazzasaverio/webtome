# webtome (sviluppo)

CLI che trasforma feed e articoli web in PDF di libri 6×9 pronti per la stampa,
organizzati in volumi. Leggi `docs/architecture.md` prima di intervenire sulla pipeline.

## Comandi

- `uv sync` then `uv run webtome --help`
- Verifica e2e manuale: `uv run webtome init /tmp/lib && cd /tmp/lib`, aggiungi un
  feed, `sync --limit 3`, `volume new`, `volume fill volume-01`, `build volume-01`,
  quindi apri `dist/volume-01.pdf` e controlla visivamente frontespizio, indice e
  apertura di un capitolo.
- Prerequisito di sistema per le build: `pandoc` (Typst è incluso tramite la wheel
  `typst`).

## Regole

- La libreria che l'utente crea con `webtome init` è semplice Markdown + YAML;
  non introdurre mai stato che non sia un file nella libreria.
- `templates/book.typ` è l'unica fonte autorevole per tipografia e geometria delle
  pagine; il codice di build assembla solo markup Typst e non applica stili.
- Non abilitare l'opzione `deduplicate` di trafilatura, perché elimina paragrafi ripetuti.
- I volumi stampati (`status: printed`) sono congelati; nessun percorso del codice può modificarli.
- La documentazione e le istruzioni per agenti di questo repository sono in italiano.

<!-- BEGIN:ops-agent-kernel -->
## Nucleo operativo degli agenti

Nucleo operativo canonico degli agenti: `/home/sm/projects/ops/AGENTS.md`

Prima di un lavoro sostanziale, leggi e segui il nucleo canonico, incluso il suo router a caricamento progressivo.
Le istruzioni locali possono restringere i requisiti, ma non possono indebolire le regole canoniche su autorizzazione, sicurezza, identità, fatturazione, email o produzione.
Non duplicare in questo file le regole canoniche.
Se il nucleo canonico non è disponibile, fermati prima di iniziare un lavoro sostanziale e segnala il problema.
<!-- END:ops-agent-kernel -->
