# Revisione P03: correzioni dell'audit sulla P02

Revisione modello **P03** (2026-11-22). Risponde al file di audit «Limpidia_Correzioni_Claude_P02». Tutte le tavole, i registri e i render sono rigenerati dalla stessa revisione. Lo stato resta **PRELIMINARE - NON PER CANTIERE**.

Layout di base invariato: la cassa resta sul muro sinistro e **G05 resta aperto** (luce scala–cassa 250 mm contro 1000–1200 richiesti). Nessun mobile è stato spostato nel modello di base.

## 1. Problemi software risolti

| # | Problema segnalato | Correzione | Verifica |
| --- | --- | --- | --- |
| 1 | Il calcolo scala–cassa sottraeva lo spessore del parapetto senza tenerne la posizione e l'estensione. | `src/checks.py` costruisce l'ingombro fisico come unione fra il foro scala e il parapetto, che è un segmento inizio–fine con buffer pari a metà spessore e testate squadrate. La distanza si misura da quell'ingombro. Se il parapetto o lo spessore mancano, l'esito è **non verificabile**, non un numero. | Test A1: parapetto fino a y 3900, sp. 50, dà compatibile 1000,6 mm; parapetto fino a y 4400 dà conflitto 975 mm; spessore assente dà non verificabile. |
| 2 | Il 1031 mm di V1 era presentato come luce di passaggio. | Il testo, la quota DXF e le proposte lo dichiarano **distanza diagonale minima fra ingombri** (angoli 850,3900 e 1850,4150): non è la larghezza di un percorso. | Test A2 sul testo del controllo e di `proposte_layout.md`; nota in A01_V1. |
| 3 | Mancava il controllo fra C1 e la scala, che in V1 si restringe. | Nuova coppia **FP08** C1–scala, con scenario «cassetti C1 aperti» e controllo di percorso (screening 900 mm). Il residuo dei controlli funzionali ora è una distanza geometrica fra ingombri estesi, non una sottrazione lineare, quindi vale anche per coppie in diagonale. | Base: FP08 1087 mm, percorso 995 mm. V1: FP08 450 mm, percorso **100 mm, conflitto**. C1–cassa in V1: 350 mm (FP03). Test A2. |
| 4 | Le varianti non mostravano la verifica completa. | `proposte_layout.md` elenca per ogni variante gli stessi 13 controlli chiave, sempre presenti anche quando non cambiano, e chiude con un **esito complessivo**: conflitti tolti, conflitti passati a non verificabile, conflitti che restano o nascono, dati mancanti. | Lettura del file rigenerato. |
| 5 | Il controllo di approccio alla porta (APPR) ignorava i mobili vicini nelle dipendenze. | Le dipendenze includono lo stato di ogni mobile entro 300 mm dalla zona di approccio. Con C4 a y 280 (assunta), APPR-P_SAL risulta **compatibile nelle ipotesi**, non superato, e il testo cita «vicini: C4». | Test A3. |
| 6 | Il testo HOST affermava cerniera e verso coerenti anche quando non documentati. | Senza cerniera il testo dice «cerniera/anta/verso non documentati, non valutati». | Test A3. |
| 7 | D01.3 disegnava lo zoccolo a mano (360 mm, rientri 20+20). | La sezione D01.3 proietta i componenti di C1 dal modello: zoccolo **370 mm**, rientro frontale 30 mm. Il passo mensole di D01.2 si ricava dai livelli `shelf_levels` del modello. | Test A4 (370 nelle quote, passo 320 con livelli sintetici); controllo visivo del PDF. |
| 8 | Le fonti X/Y e Z dei punti elettrici erano generiche e E07–E09 ricevevano «S0» in automatico. | Ogni punto ha `xy_source` e `z_source` propri. E01–E06 dichiarano la provenienza reale (punti del modello P00 senza fonte propria, da documentare con l'elettricista); E07–E09 e tutte le quote Z risultano «da documentare». Q01 aggiunge la riga su quantità, supporti, alimentatori, percorsi, circuiti e protezioni a carico dell'elettricista. E01 ha le colonne «Fonte X, Y» e «Fonte Z». | Test A5; `E01_registro_utenze.md`. |
| 9 | Test Blender: confrontava solo una parte delle dimensioni. | Il test bpy confronta tutte e tre le dimensioni e i tre centri dei solidi. | Test T09. |
| 10 | Il test del set di render veniva saltato. | Ora fallisce se i render non sono della revisione corrente. `render_meta.json` registra revisione e **impronta** (hash di modello, configurazione render e codice): se uno dei file cambia dopo il render, MANIFEST lo segnala e il test fallisce. | T23 e nuovo test sull'impronta. |
| 11 | T20 cambiava il campo `desc` invece di `function`. | T20 modifica `function`. | Test T20. |
| 12 | La tabella A01 troncava i testi. | I testi vanno a capo su massimo 3 righe da 150 caratteri. | Controllo visivo del PDF A01. |
| 13 | Il conteggio dei test nella descrizione della PR era vecchio. | Aggiornato con il risultato di questa revisione (sotto). | — |

## 2. Dati ancora ipotizzati (non promossi a verificati)

Nessuna quota `assumed` è diventata `verified`. Restano da rilevare o documentare, in ordine di impatto:

1. **Fine scala e parapetto** (posizione, estensione, spessore): decidono G05 e la valutazione di V1. Oggi la scala finisce a y 3900 in ipotesi S1 (P00 diceva 3850).
2. **Profondità reale del banco cassa**: con 600 mm mancano 750 mm alla fascia necessaria, con 450 mm ne mancano 600.
3. **Serramento della vetrina e distanza C4–facciata**: servono per V2 (C4 a 280 mm).
4. **Dimensioni della scrivania da catalogo**: servono per V3 (1400 invece di 1600).
5. **Porta saletta**: cerniera, anta e verso non documentati; APPR e HOST li dichiarano non valutati.
6. **Punti elettrici**: posizioni X/Y da P00 senza fonte propria, tutte le quote Z, E07–E09 senza posizione; quantità, supporti, alimentatori, percorsi, circuiti e protezioni sono dell'elettricista.
7. **Mensole, zoccoli e vani driver**: dimensioni da scheda prodotto o falegname; i fissaggi restano da validare.

## 3. Scelte di layout da approvare (Sherin)

| Decisione | Stato nel modello | Cosa serve |
| --- | --- | --- |
| G05, luce scala–cassa | Base: conflitto 250 mm. | Rilievo della fine scala e del parapetto, poi scegliere fra banco più corto e V1. |
| V1, cassa sulla parete di fondo | **Solo studio**, deroga a un vincolo bloccato. La distanza scala–cassa diventa non verificabile (1031 mm diagonale) e nasce un conflitto: il percorso fra C1 e scala con cassetti aperti è 100 mm. | Non è una soluzione: andrebbe ripensata la posizione di C1 prima di presentarla. |
| V2, C4 arretrata di 20 mm | Toglie il conflitto APPR-P_SAL nelle ipotesi. | Conferma della distanza dalla facciata. |
| V3 / V4, scrivania e percorso verso la saletta | V3 porta il percorso C3–scrivania da 230 a 430 mm (resta sotto 900). V4 non risolve: sposta il conflitto sul corridoio scrivania–C4 (350 mm). | Scegliere il criterio di accesso alla saletta e verificare il catalogo. |
| E05 / E06, collegamento isola e scrivania | Punti dentro l'ingombro dei mobili. | Pavimento o parete, da decidere con l'elettricista. |

## 4. Risultati dei test e comandi

```
pytest -q            -> 64 passed, 0 failed, 0 skipped (compreso il test del set di render P03)
python -m src.generate
python -m src.render  (4 viste P03, impronta registrata in outputs/render/render_meta.json)
```

## File consegnati (rev. P03)

- `A01_pianta_arredi_preliminare.pdf/.dxf`, `A01_V1_proposta.pdf/.dxf`
- `E01_punti_utenza_preliminari.pdf/.dxf`, `E01_registro_utenze.md`
- `F01`–`F04` prospetti, `D01_dettagli_schema_preliminare.pdf/.dxf`
- `AB01_abaco_arredi.md`, `Q01_quote_aperte.md`, `criticita.md`, `proposte_layout.md`, `MANIFEST.md`
- `render/` (4 viste, non sono fonti metriche)
