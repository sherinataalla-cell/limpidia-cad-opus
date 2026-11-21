# Proposte di layout quotate (R02)

Revisione base P02 (2026-11-21). Le varianti sono **proposte da approvare**: il modello di base resta invariato. Ogni variante è valutata con gli stessi controlli della base. Misure in mm, tutte preliminari.

## Luce scala–cassa con la cassa sul muro sinistro

Scala fino a y 3900 (S1; da P00 sarebbe 3850), fondo a y 4750: fascia disponibile 850 mm. Lungo il muro sinistro, verso la vetrina, la scala inizia a y 1500 e la porta d'ingresso occupa x 850–1750 con apertura di 900 mm.

| Banco (profondità P) | Fascia necessaria (P + 1000 / P + 1200) | Fine scala necessaria (y ≤) | Con la scala del modello |
| --- | --- | --- | --- |
| 600 | 1600 / 1800 | 3150 | manca 750 mm |
| 500 | 1500 / 1700 | 3250 | manca 650 mm |
| 450 | 1450 / 1650 | 3300 | manca 600 mm |

Verso la vetrina: la cassa dovrebbe finire entro y 500, cioè una profondità massima di 500 mm nella fascia y 0–500, dentro l'apertura della porta d'ingresso: non praticabile.

**Conclusione nelle ipotesi P02:** con la cassa sul muro sinistro il requisito non si ottiene finché il rilievo conferma la scala fino a y 3900. Servono: rilievo della fine scala e del parapetto, profondità reale del banco, oppure una deroga al vincolo «cassa sul muro sinistro» (V1).

## V1 — Cassa sulla parete di fondo

G05: con la cassa sul muro sinistro la fascia fra fine scala e fondo e' 850 mm contro 1600-1800 necessari; la variante sposta il banco sulla parete di fondo (x 1850-3050) e C1 nell'angolo sinistro (x 0-1500) per ottenere >= 1000 mm netti dalla scala.

**Vincoli toccati:** Deroga: cassa non piu' sul muro sinistro (decisione bloccata in docs/decisioni.md). Richiede approvazione esplicita.

| Elemento | Prima | Dopo |
| --- | --- | --- |
| CASSA | x 0 | x 1850 |
| C1 | x 1840 | x 0 |
| LS3 | x 1360 | x 1515 |

| Controllo | Base | Variante |
| --- | --- | --- |
| REQ-REQ_SCALA_CASSA | Conflitto, 250 mm | Non verificabile (dato mancante), 1031 mm |
| ADJ_CASSA_SINISTRA | Coerente (solo geometria), 0 mm | Conflitto, 1850 mm |
| FP01 | Non verificabile (dato mancante), 250 mm | Non verificabile (dato mancante), 1031 mm |
| FP03 | Non verificabile (dato mancante), 640 mm | Non verificabile (dato mancante), 350 mm |

## V2 — C4 arretrata di 20 mm verso la vetrina

APPR-P_SAL: C4 invade di 220 x 20 mm la zona di approccio alla porta saletta.

**Vincoli toccati:** C4 resta sulla parete destra; distanza C4-facciata 280 mm, da confermare con il rilievo del serramento.

| Elemento | Prima | Dopo |
| --- | --- | --- |
| C4 | y 300 | y 280 |

| Controllo | Base | Variante |
| --- | --- | --- |
| APPR-P_SAL | Conflitto | Compatibile nelle ipotesi attuali, 900 mm |
| FP04 | Compatibile nelle ipotesi attuali, 879 mm | Compatibile nelle ipotesi attuali, 899 mm |

## V3 — Scrivania lunga 1400 mm invece di 1600 (da verificare con il catalogo)

FP02: passaggio fra C3 e scrivania 230 mm con cassetti aperti; un piano lungo 1400 mm (lato verso C3) aumenta il margine.

**Vincoli toccati:** Dimensione da confermare con scheda prodotto; il passaggio resta inferiore a 900 mm.

| Elemento | Prima | Dopo |
| --- | --- | --- |
| SCRIVANIA | depth 1600 | depth 1400 |

| Controllo | Base | Variante |
| --- | --- | --- |
| FP02 | Compatibile nelle ipotesi attuali, 580 mm | Compatibile nelle ipotesi attuali, 780 mm |
| FP02-PERCORSO | Conflitto, 230 mm | Conflitto, 430 mm |

## V4 — Accesso alla saletta dal corridoio scrivania-C4

FP02-PERCORSO: invece di passare fra C3 e scrivania, il percorso verso la saletta usa il corridoio fra scrivania e C4.

**Vincoli toccati:** Nessun mobile spostato; cambia il criterio di percorso, da confermare con l'uso reale (seduta occupata e cassetti aperti).

| Elemento | Prima | Dopo |
| --- | --- | --- |
| FP02 | criterio di percorso base | {"required": false, "criterion": null, "scenario": null, "note": "percorso spostato su FP05 (V4)"} |
| FP05 | criterio di percorso base | {"required": true, "criterion": "screening_passage", "scenario": "seduta occupata e cassetti aperti (simultaneità da confermare)", "note": "percorso principale verso la saletta (V4)"} |

| Controllo | Base | Variante |
| --- | --- | --- |
| FP02-PERCORSO | Conflitto, 230 mm | - |
| FP05-PERCORSO | Non verificabile (dato mancante), 350 mm | Conflitto, 350 mm |

