# Proposta V5: cassa verso Smart, C1 a sinistra, scrivania parallela a VET_2

Modello **P04** (2026-11-23). Risponde al documento «Limpidia — integrazione per Claude / proposta V5» del 23/11/2026. V5 è una **proposta da approvare**: la base di confronto resta la configurazione P03 (cassa sul muro sinistro), invariata nel modello. Tutto è PRELIMINARE - NON PER CANTIERE. Lo schema PNG citato nel documento non era allegato: V5 è costruita sulle coordinate scritte nel testo.

Elaborati: `A01_V5_proposta.pdf/.dxf` (pianta), `E01_V5_proposta.pdf/.dxf` (punti utenza), `proposte_layout.md` (sezione V5: controlli e tabella delle distanze), `render/V5/` (4 viste). La base resta in `A01_pianta_arredi_preliminare.pdf`, con lo stesso orientamento, la stessa scala 1:50 e lo stesso riquadro: le due tavole si sovrappongono.

## 1. Cosa cambia nel modello (vale anche per la base)

- **Scala.** L'accesso e la discesa sono dal lato vetrina (`SCALE.access_side = -y`, indicazione utente). Sul lato verso C1 c'è una protezione: è modellata come linea distinta `RINGHIERA_TESTATA` sul bordo del foro a y 3900, x 0–850. È un'**ipotesi topologica** con fonte utente: tracciato, estremità, spessore e sporgenze sono da rilevare. La ringhiera longitudinale non è stata allungata.
- **Controlli sulla scala, separati come richiesto:**
  - `ACC-SCALE`: fascia di sbarco davanti all'imbocco lato vetrina (900 mm di screening × 850 mm), libera da mobili e fasce d'uso. Esito: compatibile nelle ipotesi, sia in P03 sia in V5.
  - `PROT-<mobile>-<protezione>`: vicinanza di mobili e fasce d'uso a **tutte** le protezioni, non solo alla prima linea. Senza spessore rilevato l'esito è non verificabile.
  - `FP08`: uso di C1 (cassetti e persona davanti a C1). Lo spazio della persona oltre la corsa dei cassetti è un dato nuovo, `drawer_user_zone`, lasciato **da definire**.
  - Il vecchio `FP08-PERCORSO` (percorso obbligatorio fra C1 e scala) è stato tolto: non c'è un accesso da quel lato.
- **Requisito scala–cassa 1000–1200 mm:** resta. Ora si misura dall'unione del foro con tutte le protezioni.
- **Sedute della scrivania:** stessa regola per tavole e controlli (`use_bands`): fasce da 750 mm sui due lati lunghi, qualunque sia l'orientamento. In A01 le sedute sono su un layer proprio, distinto da cassetti e ante.
- **Nuova coppia FP09** (C2–scrivania), e scenario «seduta occupata e cassetti aperti» anche su FP02.

## 2. Posizioni V5 (mm)

| Elemento | P03 | V5 | Nota |
| --- | --- | --- | --- |
| CASSA | x 0–1200, y 4150–4750 | x 1850–3050, y 4150–4750, fronte −Y | retro contro la parete di fondo (ADJ_CASSA_FONDO) |
| C1 | x 1840–3340 | x 0–1500, y 4350–4750 | |
| LS3 | x 1360–1680 | x 1515–1835 | fra C1 e cassa, non sopra C1 |
| SCRIVANIA | x 4950–5650, y 100–1700 (lato lungo su Y) | x 4250–5850, y 750–1450 (lato lungo su X) | rotazione reale: sedute sui lati lunghi; fronte +Y solo come ipotesi di modello |
| C2, C3, C4, isola | invariati | invariati | |

La traslazione della cassa fino a x 2170 non è stata adottata: nel modello interferisce con il cartellino Smart e va sotto la prima mensola Smart. Da x 1850 la cassa dista 170 mm in pianta dal primo elemento Smart sporgente.

## 3. Distanze V5 con fonte

| Misura | Valore | Fonte e ipotesi |
| --- | --- | --- |
| Cassa – foro scala | 1031 diagonale | Spigoli (850,3900)–(1850,4150). **Non è un passaggio** e non è la luce dalle protezioni: il requisito non si dichiara soddisfatto. |
| Cassa – protezioni | da rilevare | Spessore e sporgenze di RINGHIERA e RINGHIERA_TESTATA mancanti. |
| C1 chiusa – foro / testata | 450 | Testata come ipotesi topologica sul bordo del foro. |
| C1 a cassetti aperti – foro / testata | 100 | Corsa 350 (ipotesi), senza spessore della protezione e senza persona: criticità d'uso, non accesso alla scala. |
| C1 – cassa | 350 | Non è un accesso operatore finché lato di lavoro e posto cassa non sono definiti. |
| Scrivania – C4 | 1250 chiusa / 900 a cassetti aperti | 900 coincide con la soglia di screening, senza tolleranze: non è una verifica di percorso. |
| Scrivania – C2/C3 | 830 chiusi / 480 a cassetti aperti | |
| Seduta 750 verso C2/C3 | 80 dai fronti chiusi; −270 con i cassetti aperti | Gli usi si sovrappongono: FP02 e FP09 in conflitto. |
| Seduta 750 verso la vetrina | 0 | Arriva al fronte y 0; serramento non rilevato. |
| 2 sedute + piano + cassetti | 2550 contro 2280 disponibili | Mancano 270 mm. Traslare la scrivania in Y non basta finché resta davanti a C2/C3. |

Le distanze sono generate dal modello in `proposte_layout.md`; i test di `tests/test_v5.py` le controllano.

## 4. Confronto dei controlli principali

| Controllo | P03 | V5 |
| --- | --- | --- |
| Scala–cassa (REQ) | conflitto, 250 | non verificabile, 1031 in diagonale dal solo foro |
| Accesso scala lato vetrina (ACC-SCALE) | compatibile nelle ipotesi | compatibile nelle ipotesi |
| C1 verso le protezioni (PROT-C1) | lontano | non verificabile, 100 dall'asse a cassetti aperti |
| Cassa–C1 (FP03) | non verificabile, 640 | non verificabile, 350; posto operatore da definire |
| Scrivania–C3 percorso (FP02-PERCORSO) | conflitto, 230 | conflitto, 480 |
| Scrivania–C2/C3 sedute e cassetti (FP02, FP09) | compatibili nelle ipotesi | **conflitto** (sovrapposizione 270) |
| Scrivania–C4 (FP05) | compatibile; percorso non verificabile 350 | compatibile, 1250; percorso non verificabile 900 |
| Porta saletta (APPR-P_SAL) | conflitto, C4 dentro 220 × 20 | conflitto invariato: la rotazione non lo risolve (vedi V2) |

## 5. Incompatibilità ancora aperte

1. **Consulenza davanti a C2/C3:** con due sedute e cassetti aperti mancano 270 mm. Prima di proporre una geometria diversa servono posti cliente e operatore, sedute reali e quali usi devono essere simultanei. Le fasce non sono state ridotte per chiudere il controllo.
2. **Posto operatore cassa:** lato di lavoro, accesso al banco, uso del vano e spazio cliente non definiti. I 350 mm fra C1 e cassa non sono un accesso.
3. **Uso di C1:** con i cassetti aperti restano 100 mm dall'asse della testata, senza contare spessore e persona.
4. **Scala–cassa:** 1031 mm è una diagonale dal solo foro. Il requisito resta da verificare sulle protezioni reali.
5. **C4 e porta saletta:** interferenza 220 × 20 mm invariata; V2 resta l'opzione studiata.
6. **Esposizione sopra la cassa vicino a Smart:** nessuna interferenza dei componenti a x 1850. Va coordinata se la cassa si sposta verso Smart.

## 6. Misure da rilevare (in ordine di impatto per V5)

1. Protezione di testata verso C1: tracciato, estremità, spessore, sporgenze, altezza.
2. Ringhiera longitudinale: spessore e sporgenza del corrimano.
3. Sedute reali della consulenza e posti cliente/operatore; scheda della scrivania (lato contenitore).
4. Corsa reale dei cassetti Lumio e spazio della persona davanti ai cassetti.
5. Banco cassa: modello, profondità, lato operatore.
6. Serramento e sporgenze di VET_2.

## 7. Punti impianto riallineati (E01-V5)

| ID | P03 | V5 | Stato |
| --- | --- | --- | --- |
| E01 cassa | 0, 4450 | 2450, 4750 (centro del retro cassa) | Riferimento grafico. Dipende dal lato operatore; Z, quantità e percorso da definire con l'elettricista. |
| E02 C1 | 1800, 4750 | 750, 4750 (centro del retro di C1) | Riferimento grafico. Z e vano driver da definire. |
| E06 scrivania | 5300, 750 | 5050, 1100 (centro della scrivania) | Dentro l'ingombro: serve la scelta fra scatola a pavimento e canalina. La parete C4 è a 1250 mm. |

Nessun circuito, sezione, protezione o allaccio è stato attribuito.

## 8. Render

Le 4 viste V5 in `outputs/render/V5/` usano la stessa geometria di A01-V5 (`apply_overrides` dalla base), senza modifiche a muri o proporzioni. `render_meta.json` registra la revisione `P04-V5` e l'impronta di modello e codice. Le protezioni della scala sono disegnate tutte, compresa la testata in ipotesi. I render non sono fonti metriche.

## 9. Verifiche

```
pytest -q                          -> 74 passed, 0 failed, 0 skipped (compresi i set di render P04 e P04-V5)
python -m src.generate
python -m src.render               (base P04)
python -m src.render --variante=V5 (V5)
```

## Decisioni da prendere

- Se V5 diventa la base al posto di P03. Oggi è solo uno studio: deroga al vincolo «cassa al muro sinistro».
- Come usare la consulenza: quante sedute, su quali lati, e se cassetti C2/C3 e sedute si usano insieme.
- Lato di lavoro della cassa.
