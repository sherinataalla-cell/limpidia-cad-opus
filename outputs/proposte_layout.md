# Proposte di layout quotate

Revisione base P04 (2026-11-23). Le varianti sono **proposte da approvare**: il modello di base resta invariato. Ogni variante è valutata con gli stessi controlli della base. Misure in mm, tutte preliminari.

## Luce scala–cassa con la cassa sul muro sinistro

Scala fino a y 3900 (S1; da P00 sarebbe 3850), fondo a y 4750: fascia disponibile 850 mm. Lungo il muro sinistro, verso la vetrina, la scala inizia a y 1500 e la porta d'ingresso occupa x 850–1750 con apertura di 900 mm.

| Banco (profondità P) | Fascia necessaria (P + 1000 / P + 1200) | Fine scala necessaria (y ≤) | Con la scala del modello |
| --- | --- | --- | --- |
| 600 | 1600 / 1800 | 3150 | manca 750 mm |
| 500 | 1500 / 1700 | 3250 | manca 650 mm |
| 450 | 1450 / 1650 | 3300 | manca 600 mm |

Verso la vetrina: la cassa dovrebbe finire entro y 500, cioè una profondità massima di 500 mm nella fascia y 0–500, dentro l'apertura della porta d'ingresso: non praticabile.

**Conclusione nelle ipotesi P04:** con la cassa sul muro sinistro il requisito non si ottiene finché il rilievo conferma la scala fino a y 3900. Servono: rilievo della fine scala e del parapetto, profondità reale del banco, oppure, solo come studio da approvare, una deroga al vincolo «cassa sul muro sinistro» (V1).

## V1 — Cassa sulla parete di fondo

G05: con la cassa sul muro sinistro la fascia fra fine scala e fondo e' 850 mm contro 1600-1800 necessari. La variante sposta il banco sulla parete di fondo (x 1850-3050) e C1 nell'angolo sinistro (x 0-1500). La distanza minima fra foro scala e cassa diventa circa 1031 mm, ma e' una distanza DIAGONALE fra due ingombri schematici (angolo scala 850,3900 - angolo cassa 1850,4150): non dimostra un percorso utilizzabile e non tiene conto di parapetto, corrimano, persona e cassetti. Introduce inoltre un restringimento fra C1 e la scala (FP08).

**Vincoli toccati:** Deroga: cassa non piu' sul muro sinistro (vincolo bloccato in docs/decisioni.md). Studio, non soluzione: richiede rilievo e approvazione.

| Elemento | Prima | Dopo |
| --- | --- | --- |
| CASSA | x 0 | x 1850 |
| C1 | x 1840 | x 0 |
| LS3 | x 1360 | x 1515 |

| Controllo | Base | Variante |
| --- | --- | --- |
| REQ-REQ_SCALA_CASSA | Conflitto, 250 mm | Non verificabile (dato mancante), 1031 mm |
| ADJ_CASSA_SINISTRA | Coerente (solo geometria), 0 mm | Conflitto, 1850 mm |
| ACC-SCALE | Compatibile nelle ipotesi attuali, 900 mm | Compatibile nelle ipotesi attuali, 900 mm |
| FP01 | Non verificabile (dato mancante), 250 mm | Non verificabile (dato mancante), 1031 mm |
| FP03 | Non verificabile (dato mancante), 640 mm | Non verificabile (dato mancante), 350 mm |
| FP07 | Non verificabile (dato mancante), 50 mm | Non verificabile (dato mancante), 50 mm |
| FP08 | Non verificabile (dato mancante), 1087 mm | Non verificabile (dato mancante), 450 mm |
| PROT-C1-RINGHIERA | - | Non verificabile (dato mancante), 100 mm |
| PROT-C1-RINGHIERA_TESTATA | - | Non verificabile (dato mancante), 100 mm |
| FP02 | Compatibile nelle ipotesi attuali, 580 mm | Compatibile nelle ipotesi attuali, 580 mm |
| FP02-PERCORSO | Conflitto, 230 mm | Conflitto, 230 mm |
| FP09 | Compatibile nelle ipotesi attuali, 599 mm | Compatibile nelle ipotesi attuali, 599 mm |
| FP05 | Compatibile nelle ipotesi attuali, 1450 mm | Compatibile nelle ipotesi attuali, 1450 mm |
| FP05-PERCORSO | Non verificabile (dato mancante), 350 mm | Non verificabile (dato mancante), 350 mm |
| FP06 | Non verificabile (dato mancante), 100 mm | Non verificabile (dato mancante), 100 mm |
| APPR-P_SAL | Conflitto | Conflitto |
| FP04 | Compatibile nelle ipotesi attuali, 879 mm | Compatibile nelle ipotesi attuali, 879 mm |

**Esito complessivo della variante:** conflitti tolti nelle ipotesi: nessuno; da conflitto a non verificabile (serve il dato): REQ-REQ_SCALA_CASSA; conflitti che restano o nascono: ADJ_CASSA_SINISTRA, APPR-P_SAL, FP02-PERCORSO; non verificabili per dati mancanti: REQ-REQ_SCALA_CASSA, FP01, FP03, FP07, FP08, PROT-C1-RINGHIERA, PROT-C1-RINGHIERA_TESTATA, FP05-PERCORSO, FP06. La variante non è una soluzione chiusa finché restano conflitti o dati mancanti.

## V2 — C4 arretrata di 20 mm verso la vetrina

APPR-P_SAL: C4 invade di 220 x 20 mm la zona di approccio alla porta saletta.

**Vincoli toccati:** C4 resta sulla parete destra; distanza C4-facciata 280 mm, da confermare con il rilievo del serramento.

| Elemento | Prima | Dopo |
| --- | --- | --- |
| C4 | y 300 | y 280 |

| Controllo | Base | Variante |
| --- | --- | --- |
| REQ-REQ_SCALA_CASSA | Conflitto, 250 mm | Conflitto, 250 mm |
| ADJ_CASSA_SINISTRA | Coerente (solo geometria), 0 mm | Coerente (solo geometria), 0 mm |
| ACC-SCALE | Compatibile nelle ipotesi attuali, 900 mm | Compatibile nelle ipotesi attuali, 900 mm |
| FP01 | Non verificabile (dato mancante), 250 mm | Non verificabile (dato mancante), 250 mm |
| FP03 | Non verificabile (dato mancante), 640 mm | Non verificabile (dato mancante), 640 mm |
| FP07 | Non verificabile (dato mancante), 50 mm | Non verificabile (dato mancante), 50 mm |
| FP08 | Non verificabile (dato mancante), 1087 mm | Non verificabile (dato mancante), 1087 mm |
| FP02 | Compatibile nelle ipotesi attuali, 580 mm | Compatibile nelle ipotesi attuali, 580 mm |
| FP02-PERCORSO | Conflitto, 230 mm | Conflitto, 230 mm |
| FP09 | Compatibile nelle ipotesi attuali, 599 mm | Compatibile nelle ipotesi attuali, 599 mm |
| FP05 | Compatibile nelle ipotesi attuali, 1450 mm | Compatibile nelle ipotesi attuali, 1450 mm |
| FP05-PERCORSO | Non verificabile (dato mancante), 350 mm | Non verificabile (dato mancante), 350 mm |
| FP06 | Non verificabile (dato mancante), 100 mm | Non verificabile (dato mancante), 100 mm |
| APPR-P_SAL | Conflitto | Compatibile nelle ipotesi attuali, 900 mm |
| FP04 | Compatibile nelle ipotesi attuali, 879 mm | Compatibile nelle ipotesi attuali, 899 mm |

**Esito complessivo della variante:** conflitti tolti nelle ipotesi: APPR-P_SAL; da conflitto a non verificabile (serve il dato): nessuno; conflitti che restano o nascono: REQ-REQ_SCALA_CASSA, FP02-PERCORSO; non verificabili per dati mancanti: FP01, FP03, FP07, FP08, FP05-PERCORSO, FP06. La variante non è una soluzione chiusa finché restano conflitti o dati mancanti.

## V3 — Scrivania lunga 1400 mm invece di 1600 (da verificare con il catalogo)

FP02: passaggio fra C3 e scrivania 230 mm con cassetti aperti; un piano lungo 1400 mm (lato verso C3) aumenta il margine.

**Vincoli toccati:** Dimensione da confermare con scheda prodotto; il passaggio resta inferiore a 900 mm.

| Elemento | Prima | Dopo |
| --- | --- | --- |
| SCRIVANIA | depth 1600 | depth 1400 |

| Controllo | Base | Variante |
| --- | --- | --- |
| REQ-REQ_SCALA_CASSA | Conflitto, 250 mm | Conflitto, 250 mm |
| ADJ_CASSA_SINISTRA | Coerente (solo geometria), 0 mm | Coerente (solo geometria), 0 mm |
| ACC-SCALE | Compatibile nelle ipotesi attuali, 900 mm | Compatibile nelle ipotesi attuali, 900 mm |
| FP01 | Non verificabile (dato mancante), 250 mm | Non verificabile (dato mancante), 250 mm |
| FP03 | Non verificabile (dato mancante), 640 mm | Non verificabile (dato mancante), 640 mm |
| FP07 | Non verificabile (dato mancante), 50 mm | Non verificabile (dato mancante), 50 mm |
| FP08 | Non verificabile (dato mancante), 1087 mm | Non verificabile (dato mancante), 1087 mm |
| FP02 | Compatibile nelle ipotesi attuali, 580 mm | Compatibile nelle ipotesi attuali, 780 mm |
| FP02-PERCORSO | Conflitto, 230 mm | Conflitto, 430 mm |
| FP09 | Compatibile nelle ipotesi attuali, 599 mm | Compatibile nelle ipotesi attuali, 794 mm |
| FP05 | Compatibile nelle ipotesi attuali, 1450 mm | Compatibile nelle ipotesi attuali, 1450 mm |
| FP05-PERCORSO | Non verificabile (dato mancante), 350 mm | Non verificabile (dato mancante), 350 mm |
| FP06 | Non verificabile (dato mancante), 100 mm | Non verificabile (dato mancante), 100 mm |
| APPR-P_SAL | Conflitto | Conflitto |
| FP04 | Compatibile nelle ipotesi attuali, 879 mm | Compatibile nelle ipotesi attuali, 879 mm |

**Esito complessivo della variante:** conflitti tolti nelle ipotesi: nessuno; da conflitto a non verificabile (serve il dato): nessuno; conflitti che restano o nascono: APPR-P_SAL, REQ-REQ_SCALA_CASSA, FP02-PERCORSO; non verificabili per dati mancanti: FP01, FP03, FP07, FP08, FP05-PERCORSO, FP06. La variante non è una soluzione chiusa finché restano conflitti o dati mancanti.

## V4 — Accesso alla saletta dal corridoio scrivania-C4

FP02-PERCORSO: invece di passare fra C3 e scrivania, il percorso verso la saletta usa il corridoio fra scrivania e C4.

**Vincoli toccati:** Nessun mobile spostato; cambia il criterio di percorso, da confermare con l'uso reale (seduta occupata e cassetti aperti).

| Elemento | Prima | Dopo |
| --- | --- | --- |
| FP02 | criterio di percorso base | {"required": false, "criterion": null, "scenario": null, "note": "percorso spostato su FP05 (V4)"} |
| FP05 | criterio di percorso base | {"required": true, "criterion": "screening_passage", "scenario": "seduta occupata e cassetti aperti (simultaneità da confermare)", "note": "percorso principale verso la saletta (V4)"} |

| Controllo | Base | Variante |
| --- | --- | --- |
| REQ-REQ_SCALA_CASSA | Conflitto, 250 mm | Conflitto, 250 mm |
| ADJ_CASSA_SINISTRA | Coerente (solo geometria), 0 mm | Coerente (solo geometria), 0 mm |
| ACC-SCALE | Compatibile nelle ipotesi attuali, 900 mm | Compatibile nelle ipotesi attuali, 900 mm |
| FP01 | Non verificabile (dato mancante), 250 mm | Non verificabile (dato mancante), 250 mm |
| FP03 | Non verificabile (dato mancante), 640 mm | Non verificabile (dato mancante), 640 mm |
| FP07 | Non verificabile (dato mancante), 50 mm | Non verificabile (dato mancante), 50 mm |
| FP08 | Non verificabile (dato mancante), 1087 mm | Non verificabile (dato mancante), 1087 mm |
| FP02 | Compatibile nelle ipotesi attuali, 580 mm | Compatibile nelle ipotesi attuali, 580 mm |
| FP02-PERCORSO | Conflitto, 230 mm | - |
| FP09 | Compatibile nelle ipotesi attuali, 599 mm | Compatibile nelle ipotesi attuali, 599 mm |
| FP05 | Compatibile nelle ipotesi attuali, 1450 mm | Compatibile nelle ipotesi attuali, 1450 mm |
| FP05-PERCORSO | Non verificabile (dato mancante), 350 mm | Conflitto, 350 mm |
| FP06 | Non verificabile (dato mancante), 100 mm | Non verificabile (dato mancante), 100 mm |
| APPR-P_SAL | Conflitto | Conflitto |
| FP04 | Compatibile nelle ipotesi attuali, 879 mm | Compatibile nelle ipotesi attuali, 879 mm |

**Esito complessivo della variante:** conflitti tolti nelle ipotesi: nessuno; da conflitto a non verificabile (serve il dato): nessuno; conflitti che restano o nascono: APPR-P_SAL, REQ-REQ_SCALA_CASSA, FP05-PERCORSO; non verificabili per dati mancanti: FP01, FP03, FP07, FP08, FP06. La variante non è una soluzione chiusa finché restano conflitti o dati mancanti.

## V5 — Cassa verso Smart, C1 a sinistra, scrivania parallela a VET_2

Proposta dell'utente: cassa sulla parte destra della parete di fondo vicino alla parete Smart, C1 con la sua esposizione sulla parte sinistra; scrivania 1600 x 700 con il lato lungo parallelo a VET_2 (asse X). Stesse posizioni di cassa e C1 della V1. La distanza cassa-foro scala di circa 1031 mm e' DIAGONALE fra ingombri (850,3900 - 1850,4150): non e' un passaggio ne' una luce verificata dalle protezioni.

**Vincoli toccati:** Studio da approvare: cassa non piu' sul muro sinistro (vincolo P03). P03 resta la base di confronto.

| Elemento | Prima | Dopo |
| --- | --- | --- |
| CASSA | x 0 | x 1850 |
| C1 | x 1840 | x 0 |
| SCRIVANIA | x 4950, y 100, width 700, depth 1600, front -x | x 4250, y 750, width 1600, depth 700, front +y |
| LS3 | x 1360 | x 1515 |
| ADJ_CASSA_SINISTRA | accostamento della base | non più valido nella variante |
| ADJ_CASSA_FONDO | - | retro contro la parete di fondo (V5) |
| E01 | x 0, y 4450 | x 2450, y 4750 (fonte: V5: centro del retro della cassa, solo riferimento grafico; posizione da definire con l'elettricista in base al lato operatore; Z da rilevare) |
| E02 | x 1800, y 4750 | x 750, y 4750 (fonte: V5: centro del retro di C1, solo riferimento grafico; da documentare con l'elettricista; Z da rilevare) |
| E06 | x 5300, y 750 | x 5050, y 1100 (fonte: V5: centro della scrivania ruotata, solo riferimento grafico; lato contenitore e sedute da verificare sul prodotto reale; Z da rilevare) |

| Controllo | Base | Variante |
| --- | --- | --- |
| REQ-REQ_SCALA_CASSA | Conflitto, 250 mm | Non verificabile (dato mancante), 1031 mm |
| ADJ_CASSA_SINISTRA | Coerente (solo geometria), 0 mm | - |
| ADJ_CASSA_FONDO | - | Coerente (solo geometria), 0 mm |
| ACC-SCALE | Compatibile nelle ipotesi attuali, 900 mm | Compatibile nelle ipotesi attuali, 900 mm |
| FP01 | Non verificabile (dato mancante), 250 mm | Non verificabile (dato mancante), 1031 mm |
| FP03 | Non verificabile (dato mancante), 640 mm | Non verificabile (dato mancante), 350 mm |
| FP07 | Non verificabile (dato mancante), 50 mm | Non verificabile (dato mancante), 50 mm |
| FP08 | Non verificabile (dato mancante), 1087 mm | Non verificabile (dato mancante), 450 mm |
| PROT-C1-RINGHIERA | - | Non verificabile (dato mancante), 100 mm |
| PROT-C1-RINGHIERA_TESTATA | - | Non verificabile (dato mancante), 100 mm |
| FP02 | Compatibile nelle ipotesi attuali, 580 mm | Conflitto, 830 mm |
| FP02-PERCORSO | Conflitto, 230 mm | Conflitto, 480 mm |
| FP09 | Compatibile nelle ipotesi attuali, 599 mm | Conflitto, 830 mm |
| FP05 | Compatibile nelle ipotesi attuali, 1450 mm | Compatibile nelle ipotesi attuali, 1250 mm |
| FP05-PERCORSO | Non verificabile (dato mancante), 350 mm | Non verificabile (dato mancante), 900 mm |
| FP06 | Non verificabile (dato mancante), 100 mm | Non verificabile (dato mancante), 750 mm |
| APPR-P_SAL | Conflitto | Conflitto |
| FP04 | Compatibile nelle ipotesi attuali, 879 mm | Compatibile nelle ipotesi attuali, 879 mm |

**Esito complessivo della variante:** conflitti tolti nelle ipotesi: nessuno; da conflitto a non verificabile (serve il dato): REQ-REQ_SCALA_CASSA; conflitti che restano o nascono: APPR-P_SAL, FP02, FP02-PERCORSO, FP09; non verificabili per dati mancanti: REQ-REQ_SCALA_CASSA, FP01, FP03, FP07, FP08, PROT-C1-RINGHIERA, PROT-C1-RINGHIERA_TESTATA, FP05-PERCORSO, FP06. La variante non è una soluzione chiusa finché restano conflitti o dati mancanti.

**Distanze della variante** (mm; quote del modello, non rilievo):

| Misura | Valore | Fonte e ipotesi | Nota |
| --- | --- | --- | --- |
| Cassa – foro scala (minima) | 1031 | modello: S1 (scala), ingombro completo cassa (componenti) | DIAGONALE fra spigoli: non è un passaggio né la luce dalle protezioni |
| Cassa – protezioni scala | da rilevare | RINGHIERA, RINGHIERA_TESTATA: spessore e sporgenze non rilevati | la richiesta 1000–1200 mm non si dichiara soddisfatta |
| C1 chiusa – foro / testata (asse) | 450 | modello; testata = ipotesi topologica da indicazione utente | distanza dal bordo del foro |
| C1 cassetti aperti – foro / testata (asse) | 100 | corsa cassetti 350 mm (ipotesi) | criticità d'uso; non comprende spessore della protezione né la persona |
| C1 – cassa | 350 | modello | non è un accesso operatore finché lato di lavoro e posto cassa non sono definiti |
| Cassa – primo elemento Smart (in pianta) | 170 | componenti SMART (telai, cartellini, mensole) | il tratto fino alla parete Smart contiene elementi sporgenti |
| Scrivania – C4 chiusa | 1250 | modello |  |
| Scrivania – C4 cassetti aperti | 900 | corsa 350 mm (ipotesi) | pari alla soglia di screening 900: nessuna tolleranza, non è verifica di percorso |
| Scrivania – fronti C2/C3 chiusi | 830 | modello |  |
| Scrivania – C2/C3 cassetti aperti | 480 | corsa 350 mm (ipotesi) |  |
| Fascia seduta 750 lato C2/C3 – fronti chiusi | 80 | seduta 750 mm (ipotesi) |  |
| Fascia seduta 750 lato C2/C3 – cassetti aperti | -270 | ipotesi | valore negativo = sovrapposizione degli usi |
| Fascia seduta 750 lato vetrina – fronte y 0 | 0 | ipotesi; serramento non rilevato | nessun margine |
| Sedute 2 × 750 + piano 700 + cassetti 350 contro vetrina–C2/C3 | 2550 / 2280 | ipotesi di screening | mancano 270 mm: traslare in Y non basta |

