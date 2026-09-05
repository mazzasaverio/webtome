# Stampare i tuoi volumi

`webtome build` produce un PDF interno in formato **6"×9" (152×229 mm)**, il
formato più comune per tascabili, con margini speculari (0,875" interno, 0,625"
esterno) e senza abbondanza. Gli interni di solo testo non richiedono abbondanza;
i margini rispettano i requisiti dei principali servizi print-on-demand.

## Opzione 1: stampante domestica o da ufficio

- Stampa fronte-retro, con ribaltamento sul lato lungo.
- Stampa due pagine su A4/Letter e ritaglia, oppure una pagina centrata e ritaglia,
  oppure leggilo come un fascicolo pinzato o rilegato ad anelli.

## Opzione 2: tipografia locale

Chiedi: *brossura fresata, o rilegatura a spirale, 6×9 pollici, interno in bianco
e nero, carta avorio da 80 gsm, fronte-retro*. Consegna `dist/volume-NN.pdf`.

## Opzione 3: print-on-demand (va bene anche una sola copia)

[Lulu](https://www.lulu.com/) è il servizio più adatto a webtome: puoi stampare
una sola copia privata senza pubblicare nulla. Passaggi essenziali:

1. Crea un progetto libro stampato, formato rifilato **6×9 in (US Trade)**.
2. Carica `dist/volume-NN.pdf` come interno. Per raccolte di saggi scegli bianco
   e nero su carta avorio.
3. Crea una copertina con il loro strumento online o caricane una, vedi sotto.
4. Ordina la copia. Non abilitare la distribuzione: questi libri contengono articoli
   di altre persone e sono esclusivamente per uso personale.

Amazon KDP accetta interni 6×9, ma è orientato alla *vendita* dei libri; per
antologie personali preferisci Lulu o una tipografia locale.

### Limiti di pagine

La brossura richiede un numero minimo di pagine, Lulu: 32, KDP: 24, e arriva a
circa 800 pagine. `webtome status` mostra gli articoli per volume; se una build è
troppo sottile, attendi altri articoli, se è troppo spessa dividila in due volumi.

### Copertine

Il PDF interno è solo l'interno del libro. I servizi print-on-demand richiedono
un PDF separato per la copertina intera, retro + dorso + fronte, la cui larghezza
del dorso dipende dal numero finale di pagine. Lulu e KDP forniscono calcolatori
e template; un generatore di copertine è nella roadmap di webtome.

## Copyright, in modo diretto

Stampare articoli web per te stesso è archiviazione per uso personale, come
stampare dal browser. Venderli o distribuirli non lo è. Mantieni privati i volumi;
webtome imprime su ogni capitolo il suo URL sorgente e aggiunge l'elenco completo
delle fonti, così l'attribuzione accompagna sempre la carta.
