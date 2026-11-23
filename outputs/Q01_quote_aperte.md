# Q01 - Registro quote aperte, conflitti e decisioni

Revisione P04, generato il 2026-11-23 da config/geometry.json. Ogni riga resta aperta finché il dato non è inserito con stato `verified` e fonte (rilievo, scheda firmata).

| Rif. | Dato | Valore attuale | Stato | Fonte |
| --- | --- | --- | --- | --- |
| FACCIATA | lato [0, 0] → [7500, 0] | 7500 | ipotesi | S1 (coincide con S0 e S3: 7,50 m; 4,75 / 4,30 m; rientro 2,00 x 0,45 m) |
| PARETE_DESTRA | lato [7500, 0] → [7500, 4300] | 4300 | ipotesi | S1 (coincide con S0 e S3: 7,50 m; 4,75 / 4,30 m; rientro 2,00 x 0,45 m) |
| RIENTRO_FONDO | lato [7500, 4300] → [5500, 4300] | 2000 | ipotesi | S1 (coincide con S0 e S3: 7,50 m; 4,75 / 4,30 m; rientro 2,00 x 0,45 m) |
| RIENTRO_SPALLA | lato [5500, 4300] → [5500, 4750] | 450 | ipotesi | S1 (coincide con S0 e S3: 7,50 m; 4,75 / 4,30 m; rientro 2,00 x 0,45 m) |
| FONDO | lato [5500, 4750] → [0, 4750] | 5500 | ipotesi | S1 (coincide con S0 e S3: 7,50 m; 4,75 / 4,30 m; rientro 2,00 x 0,45 m) |
| PARETE_SINISTRA | lato [0, 4750] → [0, 0] | 4750 | ipotesi | S1 (coincide con S0 e S3: 7,50 m; 4,75 / 4,30 m; rientro 2,00 x 0,45 m) |
| ENVELOPE | spessori dei muri esistenti, diagonali, fuori squadra | - | da definire | rilievo |
| SOFFITTO | quota interna del soffitto e ribassamenti | 4150 | ipotesi | S3 |
| FAC_PIL_1 | facciata pier x 0–850 | 850 | ipotesi | S1 misurato sul disegno 1:40 |
| P_ING | facciata door x 850–1750 | 900 | ipotesi | S1 misurato sul disegno 1:40 |
| VET_1 | facciata glazing x 1750–3350 | 1600 | ipotesi | S1 misurato sul disegno 1:40 |
| FAC_PIL_2 | facciata pier x 3350–4250 | 900 | ipotesi | S1 misurato sul disegno 1:40 |
| VET_2 | facciata glazing x 4250–6750 | 2500 | ipotesi | S1 misurato sul disegno 1:40 (vetrina fissa) |
| FAC_PIL_3 | facciata pier x 6750–7500 | 750 | ipotesi | S1 misurato sul disegno 1:40 |
| W_SAL_O | tramezzo saletta lato scala (parete smart): x 3390, y 2680, 100 × 2070 | - | ipotesi | S1; spessore 10 cm ipotizzato; lunghezza coerente con S2 (2,07 m) |
| W_SAL_S1 | tramezzo saletta fronte, tratto sinistro: x 3490, y 2680, 2930 × 100 | - | ipotesi | S1 |
| W_SAL_S2 | tramezzo saletta fronte, spalla destra della porta: x 7320, y 2680, 180 × 100 | - | ipotesi | S1 misurato sul disegno 1:40 |
| P_SAL | porta saletta di refrazione: vano 6420–7320, luce 850, verso | 900 | ipotesi | S1/S3: vano 90 cm, passaggio utile 85 cm, porta a destra verso l'interno; distanze dalle spallette da rilevare |
| P_SAL | altezza del vano, spallette, serramento | - | da definire | rilievo |
| P_ING | porta d'ingresso: vano 850–1750, luce da rilevare, verso | 900 | ipotesi | S1 misurato sul disegno 1:40; luce netta, serramento e verso da rilevare |
| P_ING | altezza del vano, spallette, serramento | - | da definire | rilievo |
| SALETTA | dimensioni nette (dal poligono netto) | 4010 × 1970 / 1520; 7.00 m² | ipotesi | S1/S3: 4,01 m di larghezza netta; 1,97 m e 1,52 m di profondita' netta; 7,00 m2 netti di progetto; poligoni ricavati dai tramezzi W_SAL_O e W_SAL_S1 (bounded_by) |
| SCALE | posizione e dimensioni | - | ipotesi | S1 (posizione) e S3 (foro 0,85 x 2,40 m) |
| RINGHIERA | posizione e dimensioni (spessore e sporgenza corrimano) | - | ipotesi | S1; spessore e sporgenza del corrimano da rilevare |
| RINGHIERA_TESTATA | posizione e dimensioni (spessore e sporgenza corrimano) | - | ipotesi | indicazione utente 23/11/2026: protezione sul lato della scala verso C1. Posizione sul bordo del foro come ipotesi topologica; tracciato, estremita', spessore e sporgenze da rilevare |
| SCALE | fine della scala lato fondo, parapetto in testa: confronto P00 (y 1450–3850) / S1 (y 1500–3900) | 3900 | ipotesi | S1 scelta in P01; da rilevare (determina la luce scala-cassa) |
| CASSA | prodotto L × P (lungo il fronte × profondità) | 1200 × 600 | da definire | DEC: fianco a muro sinistro; ingombro segnaposto |
| CASSA | posizione nel locale | x 0, y 4150, fronte -y | ipotesi | DEC: fianco a muro sinistro; ingombro segnaposto |
| CASSA | altezza | 1000 | ipotesi | scheda prodotto da archiviare |
| C1 | prodotto L × P (lungo il fronte × profondità) | 1500 × 400 | ipotesi | DEC: fondo di fronte alla vetrina; 1200 o 1500 |
| C1 | posizione nel locale | x 1840, y 4350, fronte -y | ipotesi | DEC: fondo di fronte alla vetrina; 1200 o 1500 |
| C1 | altezza | 800 | ipotesi | scheda prodotto da archiviare |
| C2 | prodotto L × P (lungo il fronte × profondità) | 1200 × 400 | ipotesi | DEC: fronte saletta; 120 cm candidata |
| C2 | posizione nel locale | x 3600, y 2280, fronte -y | ipotesi | DEC: fronte saletta; 120 cm candidata |
| C2 | altezza | 800 | ipotesi | scheda prodotto da archiviare |
| C3 | prodotto L × P (lungo il fronte × profondità) | 1200 × 400 | ipotesi | DEC: fronte saletta; 120 cm candidata |
| C3 | posizione nel locale | x 4800, y 2280, fronte -y | ipotesi | DEC: fronte saletta; 120 cm candidata |
| C3 | altezza | 800 | ipotesi | scheda prodotto da archiviare |
| C4 | prodotto L × P (lungo il fronte × profondità) | 1500 × 400 | ipotesi | DEC: parete laterale parallela alla scrivania; 150 cm candidata |
| C4 | posizione nel locale | x 7100, y 300, fronte -x | ipotesi | DEC: parete laterale parallela alla scrivania; 150 cm candidata |
| C4 | altezza | 800 | ipotesi | scheda prodotto da archiviare |
| SCRIVANIA | prodotto L × P (lungo il fronte × profondità) | 1600 × 700 | ipotesi | DEC: angolo verso la vetrina, parallela a C4; Homary 1600 x 700 da ricontrollare |
| SCRIVANIA | posizione nel locale | x 4950, y 100, fronte -x | ipotesi | DEC: angolo verso la vetrina, parallela a C4; Homary 1600 x 700 da ricontrollare |
| SCRIVANIA | altezza | 760 | ipotesi | scheda prodotto da archiviare |
| ISOLA_SMART | prodotto L × P (lungo il fronte × profondità) | 1600 × 390 | da catalogo | DEC: Monfero 1600 x 390 x 830 da confermare sulla variante; lato lungo lungo la ringhiera, ante verso la vendita |
| ISOLA_SMART | posizione nel locale | x 900, y 1500, fronte +x | ipotesi | DEC: Monfero 1600 x 390 x 830 da confermare sulla variante; lato lungo lungo la ringhiera, ante verso la vendita |
| ISOLA_SMART | altezza | 830 | da catalogo | scheda prodotto da archiviare |
| PARTI | zoccoli, top e pannelli dei mobili (spessori) | vedi furniture_parts | ipotesi | PROP |
| USO | drawer_extension: corsa cassetti; da scheda Lumio; cassetti normalmente chiusi, aperti brevemente all'occorrenza (indicazione utente 23/11/2026) | 350 | ipotesi | PROP |
| USO | door_leaf_island: apertura ante Monfero; da scheda | 390 | da definire | PROP |
| USO | chair_zone: sedia occupata e arretrata; lati da definire; fascia convenzionale storica (P01-V5), non prescrizione approvata: in V5b sostituita dalle sedute reali | 750 | ipotesi | PROP |
| USO | operator_zone: lato operatore della cassa non definito | 800 | da definire | PROP |
| USO | screening_passage: soglia di screening, non requisito normativo | 900 | ipotesi | PROP |
| USO | railing_thickness: spessore e sporgenza del corrimano rispetto all'asse | - | da definire | rilievo |
| USO | drawer_user_zone: spazio della persona davanti ai cassetti aperti (oltre la corsa): dato da definire, non sostituito da ipotesi | - | da definire | PROP |
| USO | seat_operator: ingombro della sedia reale dell'operatore occupata (uso compatto, parte sotto il piano): da scheda della sedia; non sostituito con 750 | - | da definire | indicazione utente 23/11/2026 (V5b) |
| USO | seat_client: ingombro della sedia reale del cliente occupata: da scheda della sedia; non sostituito con 750 | - | da definire | indicazione utente 23/11/2026 (V5b) |
| USO | seat_move: manovra occasionale della seduta (avvicinamento, alzata, arretramento): da rilevare con la sedia reale | - | da definire | indicazione utente 23/11/2026 (V5b) |
| REQ_SCALA_CASSA | requisito committenza: luce netta fra il limite fisico più sporgente di scala/parapetto/corrimano e l'ingombro completo della cassa (top compreso), a banco chiuso | ≥ 1000 (obiettivo 1000–1200) | requisito | committenza, indicazione del 21/11/2026: «tra la scala e la cassa un metro / un metro e venti» |
| SMART | fascia smart | 1820 | ipotesi | S2: fascia smart riservata 1,82 m (precedente progetto, da riconciliare) |
| SMART | telaio esterno / immagine / distanza libera / interasse / altezza / base | 410 / 380 / 60 / 470 / 700 / 1150 | ipotesi | PROP da S4: quattro pannelli con immagine e titolo |
| SMART | rivestimento mattoni: spessore e fissaggio | 20 | ipotesi | DEC; spessore rivestimento ipotizzato |
| SMART | immagini dei pannelli | - | da definire | immagini dei quattro pannelli non presenti nel repository: segnaposto dichiarati nelle tavole e nei render |
| ESPOSIZIONE | livelli mensole (base), cubotti, listelli e specchi | [1250, 1550, 1850, 2150] | ipotesi | PROP da S4 |
| ESPOSIZIONE | sommità listelli | soffitto - 400 | ipotesi | PROP da S4 |
| ESPOSIZIONE | linee LED cassettiere (assi, frazione di H) | [0.38, 0.7] | ipotesi | PROP da S4: due linee LED incassate nel frontale |
| E01 | posizione X/Y (Cassa: POS, rete dati, stampante, monitor) | 0, 4450 | ipotesi | S0 (modello P00, punto senza fonte propria), riportato sul supporto attuale in P01/P02: da documentare con l'elettricista |
| E01 | quota Z | - | da definire | da documentare |
| E01 | quantità, supporto, alimentatore, percorso, circuiti e protezioni | - | da definire | elettricista |
| E02 | posizione X/Y (C1: due linee LED frontali e luci mensole fondo) | 1800, 4750 | ipotesi | S0 (modello P00, punto senza fonte propria), riportato sul supporto attuale in P01/P02: da documentare con l'elettricista |
| E02 | quota Z | - | da definire | da documentare |
| E02 | quantità, supporto, alimentatore, percorso, circuiti e protezioni | - | da definire | elettricista |
| E03A | posizione X/Y (C2: LED frontali e luci mensole) | 3550, 2680 | ipotesi | S0 (modello P00, punto senza fonte propria), riportato sul supporto attuale in P01/P02: da documentare con l'elettricista |
| E03A | quota Z | - | da definire | da documentare |
| E03A | quantità, supporto, alimentatore, percorso, circuiti e protezioni | - | da definire | elettricista |
| E03B | posizione X/Y (C3: LED frontali e luci mensole) | 6080, 2680 | ipotesi | S0 (modello P00, punto senza fonte propria), riportato sul supporto attuale in P01/P02: da documentare con l'elettricista |
| E03B | quota Z | - | da definire | da documentare |
| E03B | quantità, supporto, alimentatore, percorso, circuiti e protezioni | - | da definire | elettricista |
| E03C | posizione X/Y (C4: LED frontali e luci mensole) | 7500, 1900 | ipotesi | S0 (modello P00, punto senza fonte propria), riportato sul supporto attuale in P01/P02: da documentare con l'elettricista |
| E03C | quota Z | - | da definire | da documentare |
| E03C | quantità, supporto, alimentatore, percorso, circuiti e protezioni | - | da definire | elettricista |
| E04 | posizione X/Y (Parete smart: quattro telai con immagine e luce prodotto) | 3370, 3715 | ipotesi | S0 (modello P00, punto senza fonte propria), riportato sul supporto attuale in P01/P02: da documentare con l'elettricista |
| E04 | quota Z | - | da definire | da documentare |
| E04 | quantità, supporto, alimentatore, percorso, circuiti e protezioni | - | da definire | elettricista |
| E05 | posizione X/Y (Isola smart: ricarica e luce espositiva) | 1070, 2450 | ipotesi | S0 (modello P00, punto senza fonte propria), riportato sul supporto attuale in P01/P02: da documentare con l'elettricista |
| E05 | quota Z | - | da definire | da documentare |
| E05 | quantità, supporto, alimentatore, percorso, circuiti e protezioni | - | da definire | elettricista |
| E06 | posizione X/Y (Scrivania consulenza: presa integrata, PC, rete) | 5300, 750 | ipotesi | S0 (modello P00, punto senza fonte propria), riportato sul supporto attuale in P01/P02: da documentare con l'elettricista |
| E06 | quota Z | - | da definire | da documentare |
| E06 | quantità, supporto, alimentatore, percorso, circuiti e protezioni | - | da definire | elettricista |
| E07 | posizione X/Y (Scala: illuminazione gradini e corrimano) | da definire | da definire | da documentare |
| E07 | quota Z | - | da definire | da documentare |
| E07 | quantità, supporto, alimentatore, percorso, circuiti e protezioni | - | da definire | elettricista |
| E08 | posizione X/Y (Saletta: strumenti di refrazione, poltrona, rete) | da definire | da definire | da documentare |
| E08 | quota Z | - | da definire | da documentare |
| E08 | quantità, supporto, alimentatore, percorso, circuiti e protezioni | - | da definire | elettricista |
| E09 | posizione X/Y (Illuminazione generale ed esposizione (binari a soffitto)) | da definire | da definire | da documentare |
| E09 | quota Z | - | da definire | da documentare |
| E09 | quantità, supporto, alimentatore, percorso, circuiti e protezioni | - | da definire | elettricista |
| PT_DICHIARATO | superficie dichiarata: criterio non indicato (lorda, netta o catastale): da riconciliare con il rilievo, non usare per scalare la pianta | 45 | da definire | LOC |

## Conflitti e verifiche non eseguibili

| ID | Esito | Dettaglio |
| --- | --- | --- |
| APPR-P_SAL | Conflitto | P_SAL: nella zona di accesso di 900 mm davanti al vano (screening): C4 (220 × 20 mm dentro la zona). |
| REQ-REQ_SCALA_CASSA | Conflitto | luce netta 250 mm fra SCALE (bordo del foro) e ingombro completo di CASSA; richiesta committenza ≥ 1000 mm, obiettivo 1000–1200 mm: insufficiente. Fascia fra fine scala e fondo 850 mm; servono 1600–1800 mm con questo banco: mancano 750–950 mm. |
| FP02-PERCORSO | Conflitto | C3–SCRIVANIA: percorso/accesso nello scenario «cassetti C3 aperti»: residuo 230 mm < soglia di screening 900 mm (parametro di progetto, non requisito normativo). |
| CLEAR-P_ING | Non verificabile (dato mancante) | P_ING: luce netta di passaggio non documentata. |
| SMART-IMG | Non verificabile (dato mancante) | Immagini dei pannelli: immagini dei quattro pannelli non presenti nel repository: segnaposto dichiarati nelle tavole e nei render. |
| AREA-PT_DICHIARATO | Non verificabile (dato mancante) | Dato 45 m² (LOC, criterio non indicato (lorda, netta o catastale): da riconciliare con il rilievo, non usare per scalare la pianta) contro 34.73 m² del poligono interno: è una questione di fonti da riconciliare con il rilievo, la pianta non va riscalata. |
| FP01 | Non verificabile (dato mancante) | CASSA–SCALE (lato operatore / accesso cassa): distanza statica 250 mm; posto operatore: manca operator_zone. |
| FP03 | Non verificabile (dato mancante) | CASSA–C1 (intervallo laterale cassa-fondo: servizio o passaggio da stabilire): distanza statica 640 mm; posto operatore: manca operator_zone. |
| FP05-PERCORSO | Non verificabile (dato mancante) | SCRIVANIA–C4: percorso/accesso nello scenario «seduta occupata e cassetti aperti (simultaneità da confermare)»: residuo 350 mm; criterio di passaggio e simultaneità degli usi non stabiliti (accesso all'esposizione C4 e passaggio verso la saletta: criterio e simultaneità non stabiliti). |
| FP06 | Non verificabile (dato mancante) | SCRIVANIA–FACCIATA (serramento, pulizia e sporgenze verso la vetrina): distanza statica 100 mm; manca il criterio: serramento, sporgenze e uso del bordo da rilevare. |
| FP07 | Non verificabile (dato mancante) | ISOLA_SMART–RINGHIERA (luce netta tra isola e corrimano): distanza statica 50 mm; luce netta: manca railing_thickness. |
| FP08 | Non verificabile (dato mancante) | C1–SCALE (uso di C1: cassetti aperti e persona davanti a C1 verso il foro scala (l'accesso alla scala e' dal lato vetrina, ACC-SCALE)): distanza statica 1087 mm; mobili chiusi: residuo 1087 mm; cassetti C1 aperti: residuo 995 mm; persona che usa C1 a cassetti aperti: manca drawer_user_zone. |
| PROT-CASSA-RINGHIERA | Non verificabile (dato mancante) | CASSA verso la protezione RINGHIERA: 250 mm a mobile chiuso, 250 mm con le fasce d'uso, misurati dall'asse della protezione; spessore, sporgenze e tracciato della protezione da rilevare: la distanza reale è minore. Non dimostra l'uso del mobile. |
| PROT-CASSA-RINGHIERA_TESTATA | Non verificabile (dato mancante) | CASSA verso la protezione RINGHIERA_TESTATA: 250 mm a mobile chiuso, 250 mm con le fasce d'uso, misurati dall'asse della protezione; spessore, sporgenze e tracciato della protezione da rilevare: la distanza reale è minore. Non dimostra l'uso del mobile. |
| USE-door_leaf_island | Non verificabile (dato mancante) | door_leaf_island per ISOLA_SMART: apertura ante Monfero; da scheda; verifica da eseguire con il dato. |
| USE-drawer_user_zone | Non verificabile (dato mancante) | drawer_user_zone per C1, C2, C3, C4: spazio della persona davanti ai cassetti aperti (oltre la corsa): dato da definire, non sostituito da ipotesi; verifica da eseguire con il dato. |
| USE-operator_zone | Non verificabile (dato mancante) | operator_zone per CASSA: lato operatore della cassa non definito; verifica da eseguire con il dato. |
| USE-seat_client | Non verificabile (dato mancante) | seat_client per SCRIVANIA: ingombro della sedia reale del cliente occupata: da scheda della sedia; non sostituito con 750; verifica da eseguire con il dato. |
| USE-seat_move | Non verificabile (dato mancante) | seat_move per SCRIVANIA: manovra occasionale della seduta (avvicinamento, alzata, arretramento): da rilevare con la sedia reale; verifica da eseguire con il dato. |
| USE-seat_operator | Non verificabile (dato mancante) | seat_operator per SCRIVANIA: ingombro della sedia reale dell'operatore occupata (uso compatto, parte sotto il piano): da scheda della sedia; non sostituito con 750; verifica da eseguire con il dato. |
| EL-E07 | Non verificabile (dato mancante) | E07 (Scala: illuminazione gradini e corrimano): posizione da definire. |
| EL-E08 | Non verificabile (dato mancante) | E08 (Saletta: strumenti di refrazione, poltrona, rete): posizione da definire. |
| EL-E09 | Non verificabile (dato mancante) | E09 (Illuminazione generale ed esposizione (binari a soffitto)): posizione da definire. |
| EL-Z-E01 | Non verificabile (dato mancante) | E01: quota Z da rilevare. |
| EL-Z-E02 | Non verificabile (dato mancante) | E02: quota Z da rilevare. |
| EL-Z-E03A | Non verificabile (dato mancante) | E03A: quota Z da rilevare. |
| EL-Z-E03B | Non verificabile (dato mancante) | E03B: quota Z da rilevare. |
| EL-Z-E03C | Non verificabile (dato mancante) | E03C: quota Z da rilevare. |
| EL-Z-E04 | Non verificabile (dato mancante) | E04: quota Z da rilevare. |
| EL-Z-E05 | Non verificabile (dato mancante) | E05: quota Z da rilevare. |
| EL-Z-E06 | Non verificabile (dato mancante) | E06: quota Z da rilevare. |

## Decisioni da prendere (alternative quotate in proposte_layout.md)

- Luce scala–cassa ≥ 1000 mm richiesta: con la scala fino a y 3900 e la cassa sul muro sinistro non è ottenibile; scegliere fra le alternative.
- Lato operatore della cassa e prodotto reale (oggi segnaposto 1200 × 600).
- C3–scrivania (percorso verso la saletta) e C4 nella zona di accesso alla saletta.
- Lati di seduta della scrivania e simultaneità degli usi fra scrivania e C4.
- Collegamento di E05 ed E06 (alternative nel registro utenze).
- Immagini dei pannelli smart e prodotti esposti.
- Verbale di rilievo: data, tecnico, foto e strumenti per ogni quota inserita come verificata.
