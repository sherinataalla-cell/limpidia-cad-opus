# Criticità e verifiche (generato dal modello)

Revisione modello: P01. Controlli geometrici e di uso sotto ipotesi dichiarate; da validare con il tecnico. Un controllo «non verificabile» non è superato.

## Riepilogo

| Esito | Numero |
| --- | ---: |
| Conflitto | 2 |
| Non verificabile (dato mancante) | 17 |
| Avviso | 4 |
| Compatibile nelle ipotesi attuali | 6 |
| Coerente con decisione | 7 |

## Ingombri d'uso e coppie funzionali

| ID | Esito | Dettaglio | Stato dei dati |
| --- | --- | --- | --- |
| FP02 | Conflitto | C3–SCRIVANIA (uso cassetti C3, sedute e percorso verso la saletta): distanza 580 mm; luce residua stimata 230 mm sotto la soglia di screening 900 mm. | ipotesi |
| FP01 | Non verificabile (dato mancante) | CASSA–SCALE (lato operatore / accesso cassa): distanza 250 mm; manca: operator_zone. | da definire |
| FP03 | Non verificabile (dato mancante) | CASSA–C1 (intervallo laterale cassa-fondo: servizio o passaggio da stabilire): distanza 640 mm; manca: operator_zone. | da definire |
| FP06 | Non verificabile (dato mancante) | SCRIVANIA–FACCIATA (serramento, pulizia e sporgenze verso la vetrina): distanza 100 mm; manca: nessun criterio documentato (serramento, sporgenze, spessori da rilevare). | ipotesi |
| FP07 | Non verificabile (dato mancante) | ISOLA_SMART–RINGHIERA (luce netta tra isola e corrimano): distanza 50 mm; manca: railing_thickness. | ipotesi |
| FP04 | Compatibile nelle ipotesi attuali | C4–P_SAL (cassetti C4 aperti vicino alla porta della saletta): distanza 879 mm, nessuna interferenza con le ipotesi d'uso. | ipotesi |
| FP05 | Compatibile nelle ipotesi attuali | SCRIVANIA–C4 (sedia operatore e cassetti C4 aperti): distanza 1450 mm, nessuna interferenza con le ipotesi d'uso. | ipotesi |

## Porte

| ID | Esito | Dettaglio | Stato dei dati |
| --- | --- | --- | --- |
| APPR-P_SAL | Conflitto | P_SAL: nella zona di accesso di 900 mm davanti al vano: C4 (220 × 20 mm dentro la zona). | ipotesi |
| CLEAR-P_ING | Non verificabile (dato mancante) | P_ING: luce netta di passaggio non documentata. | da definire |
| SWING-P_ING | Compatibile nelle ipotesi attuali | P_ING: vano 900 mm, anta 900 mm (verso l'interno, cerniera a sinistra): nessuna interferenza. | ipotesi |
| SWING-P_SAL | Compatibile nelle ipotesi attuali | P_SAL: vano 900 mm, anta 850 mm (verso l'interno della saletta, cerniera a destra): nessuna interferenza. | ipotesi |

## Accostamenti dichiarati

| ID | Esito | Dettaglio | Stato dei dati |
| --- | --- | --- | --- |
| ADJ-C1-ENV | Coerente con decisione | C1: retro contro la parete di fondo, distanza dal muro 0 mm. | ipotesi |
| ADJ-C2-C3 | Coerente con decisione | C2–C3: accostamento dichiarato (affiancate sul fronte saletta), distanza 0 mm. | ipotesi |
| ADJ-C2-W_SAL_S1 | Coerente con decisione | C2–W_SAL_S1: accostamento dichiarato (retro contro il tramezzo), distanza 0 mm. | ipotesi |
| ADJ-C3-W_SAL_S1 | Coerente con decisione | C3–W_SAL_S1: accostamento dichiarato (retro contro il tramezzo), distanza 0 mm. | ipotesi |
| ADJ-C4-ENV | Coerente con decisione | C4: retro contro la parete laterale destra, distanza dal muro 0 mm. | ipotesi |
| ADJ-CASSA-ENV | Coerente con decisione | CASSA: fianco a contatto con il muro sinistro, distanza dal muro 0 mm. | da definire |
| ADJ-ISOLA_SMART-SCALE | Coerente con decisione | ISOLA_SMART–SCALE: accostamento dichiarato (lato lungo accostato alla ringhiera), distanza 50 mm. | ipotesi |

## Prossimità non dichiarate

| ID | Esito | Dettaglio | Stato dei dati |
| --- | --- | --- | --- |
| PRX-C1-W_SAL_O | Avviso | C1–W_SAL_O: 50 mm, relazione non dichiarata (accostamento o passaggio da stabilire). | ipotesi |
| PRX-C2-W_SAL_O | Avviso | C2–W_SAL_O: 110 mm, relazione non dichiarata (accostamento o passaggio da stabilire). | ipotesi |

## Parete smart

| ID | Esito | Dettaglio | Stato dei dati |
| --- | --- | --- | --- |
| SMART-FIT | Compatibile nelle ipotesi attuali | Parete smart 2070 mm: composizione 1820 mm (4 × 410 + 3 × 60), margini 125 / 125 mm. | ipotesi |

## Utenze

| ID | Esito | Dettaglio | Stato dei dati |
| --- | --- | --- | --- |
| EL-E07 | Non verificabile (dato mancante) | E07 (Scala: illuminazione gradini e corrimano): posizione da definire. | da definire |
| EL-E08 | Non verificabile (dato mancante) | E08 (Saletta: strumenti di refrazione, poltrona, rete): posizione da definire. | da definire |
| EL-E09 | Non verificabile (dato mancante) | E09 (Illuminazione generale ed esposizione (binari a soffitto)): posizione da definire. | da definire |
| EL-Z-E01 | Non verificabile (dato mancante) | E01: quota Z da rilevare. | da definire |
| EL-Z-E02 | Non verificabile (dato mancante) | E02: quota Z da rilevare. | da definire |
| EL-Z-E03A | Non verificabile (dato mancante) | E03A: quota Z da rilevare. | da definire |
| EL-Z-E03B | Non verificabile (dato mancante) | E03B: quota Z da rilevare. | da definire |
| EL-Z-E03C | Non verificabile (dato mancante) | E03C: quota Z da rilevare. | da definire |
| EL-Z-E04 | Non verificabile (dato mancante) | E04: quota Z da rilevare. | da definire |
| EL-Z-E05 | Non verificabile (dato mancante) | E05: quota Z da rilevare. | da definire |
| EL-Z-E06 | Non verificabile (dato mancante) | E06: quota Z da rilevare. | da definire |
| EL-IN-E05 | Avviso | E05 cade dentro l'ingombro di ISOLA_SMART: punto dentro l'ingombro dell'isola: serve dettaglio di collegamento e apertura per manutenzione. | ipotesi |
| EL-IN-E06 | Avviso | E06 cade dentro l'ingombro di SCRIVANIA: punto dentro l'ingombro della scrivania: serve passacavi e accesso da sotto il piano. | ipotesi |

## Superfici

| ID | Esito | Dettaglio | Stato dei dati |
| --- | --- | --- | --- |
| AREA-PT_DICHIARATO | Non verificabile (dato mancante) | Dato 45 m² (LOC, criterio non indicato (lorda, netta o catastale): da riconciliare con il rilievo, non usare per scalare la pianta) contro 34.73 m² del poligono interno: è una questione di fonti da riconciliare con il rilievo, la pianta non va riscalata. | da definire |
| AREA-SAL | Compatibile nelle ipotesi attuali | Saletta netta 7.00 m² sulle facce interne dei tramezzi (S1/S3 dichiarano 7,00 m² netti di progetto). | ipotesi |

## Superfici

| Definizione | m² |
| --- | ---: |
| involucro (poligono delle facce interne, foro scala incluso) | 34.725 |
| foro scala | 2.040 |
| tramezzi saletta (impronta) | 0.518 |
| saletta netta (facce interne dei tramezzi) | 7.000 |
| saletta lorda (con tramezzi) | 7.608 |
| zona vendita calpestabile (involucro - foro scala - saletta lorda) | 25.077 |
