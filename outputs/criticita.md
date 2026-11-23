# Criticità e verifiche (generato dal modello)

Revisione modello: P04. Controlli geometrici e di uso sotto ipotesi dichiarate; da validare con il tecnico. Un controllo «non verificabile» non è superato; «coerente» riguarda solo la geometria.

## Riepilogo

| Esito | Numero |
| --- | ---: |
| Conflitto | 3 |
| Non verificabile (dato mancante) | 25 |
| Avviso | 4 |
| Compatibile nelle ipotesi attuali | 10 |
| Coerente (solo geometria) | 16 |

## Requisiti della committenza

| ID | Esito | Dettaglio | Stato dei dati |
| --- | --- | --- | --- |
| REQ-REQ_SCALA_CASSA | Conflitto | luce netta 250 mm fra SCALE (bordo del foro) e ingombro completo di CASSA; richiesta committenza ≥ 1000 mm, obiettivo 1000–1200 mm: insufficiente. Fascia fra fine scala e fondo 850 mm; servono 1600–1800 mm con questo banco: mancano 750–950 mm. | da definire |

## Ingombri dei componenti (pianta = abaco = render)

7 controlli coerenti su 7.

## Vincoli approvati

| ID | Esito | Dettaglio | Stato dei dati |
| --- | --- | --- | --- |
| DEC-ISOLA-P | Compatibile nelle ipotesi attuali | Isola: profondità esterna 390 mm (prodotto P 390 mm), limite approvato 400 mm. | da catalogo |

## Ingombri d'uso, scenari e percorsi

| ID | Esito | Dettaglio | Stato dei dati |
| --- | --- | --- | --- |
| FP02-PERCORSO | Conflitto | C3–SCRIVANIA: percorso/accesso nello scenario «cassetti C3 aperti»: residuo 230 mm < soglia di screening 900 mm (parametro di progetto, non requisito normativo). | ipotesi |
| FP01 | Non verificabile (dato mancante) | CASSA–SCALE (lato operatore / accesso cassa): distanza statica 250 mm; posto operatore: manca operator_zone. | da definire |
| FP03 | Non verificabile (dato mancante) | CASSA–C1 (intervallo laterale cassa-fondo: servizio o passaggio da stabilire): distanza statica 640 mm; posto operatore: manca operator_zone. | da definire |
| FP05-PERCORSO | Non verificabile (dato mancante) | SCRIVANIA–C4: percorso/accesso nello scenario «seduta occupata e cassetti aperti (simultaneità da confermare)»: residuo 350 mm; criterio di passaggio e simultaneità degli usi non stabiliti (accesso all'esposizione C4 e passaggio verso la saletta: criterio e simultaneità non stabiliti). | ipotesi |
| FP06 | Non verificabile (dato mancante) | SCRIVANIA–FACCIATA (serramento, pulizia e sporgenze verso la vetrina): distanza statica 100 mm; manca il criterio: serramento, sporgenze e uso del bordo da rilevare. | ipotesi |
| FP07 | Non verificabile (dato mancante) | ISOLA_SMART–RINGHIERA (luce netta tra isola e corrimano): distanza statica 50 mm; luce netta: manca railing_thickness. | ipotesi |
| FP08 | Non verificabile (dato mancante) | C1–SCALE (uso di C1: cassetti aperti e persona davanti a C1 verso il foro scala (l'accesso alla scala e' dal lato vetrina, ACC-SCALE)): distanza statica 1087 mm; mobili chiusi: residuo 1087 mm; cassetti C1 aperti: residuo 995 mm; persona che usa C1 a cassetti aperti: manca drawer_user_zone. | ipotesi |
| PROT-CASSA-RINGHIERA | Non verificabile (dato mancante) | CASSA verso la protezione RINGHIERA: 250 mm a mobile chiuso, 250 mm con le fasce d'uso, misurati dall'asse della protezione; spessore, sporgenze e tracciato della protezione da rilevare: la distanza reale è minore. Non dimostra l'uso del mobile. | da definire |
| PROT-CASSA-RINGHIERA_TESTATA | Non verificabile (dato mancante) | CASSA verso la protezione RINGHIERA_TESTATA: 250 mm a mobile chiuso, 250 mm con le fasce d'uso, misurati dall'asse della protezione; spessore, sporgenze e tracciato della protezione da rilevare: la distanza reale è minore. Non dimostra l'uso del mobile. | da definire |
| USE-door_leaf_island | Non verificabile (dato mancante) | door_leaf_island per ISOLA_SMART: apertura ante Monfero; da scheda; verifica da eseguire con il dato. | da definire |
| USE-drawer_user_zone | Non verificabile (dato mancante) | drawer_user_zone per C1, C2, C3, C4: spazio della persona davanti ai cassetti aperti (oltre la corsa): dato da definire, non sostituito da ipotesi; verifica da eseguire con il dato. | da definire |
| USE-operator_zone | Non verificabile (dato mancante) | operator_zone per CASSA: lato operatore della cassa non definito; verifica da eseguire con il dato. | da definire |
| ACC-SCALE | Compatibile nelle ipotesi attuali | Accesso a SCALE dal lato -y (indicazione utente 23/11/2026: accesso e discesa dal lato vetrina; il lato verso C1 non e' un accesso): fascia di sbarco 900 mm × 850 mm libera da mobili e fasce d'uso nelle ipotesi. Soglia di screening, non verifica normativa; gradini, alzate e corrimano da rilevare. | ipotesi |
| FP02 | Compatibile nelle ipotesi attuali | C3–SCRIVANIA (uso cassetti C3, sedute e percorso verso la saletta): distanza statica 580 mm; mobili chiusi: residuo 580 mm; cassetti C3 aperti: residuo 230 mm; seduta occupata: residuo 580 mm; seduta occupata e cassetti C3 aperti: residuo 230 mm. Esito limitato alla non sovrapposizione degli ingombri d'uso. | ipotesi |
| FP04 | Compatibile nelle ipotesi attuali | C4–P_SAL (cassetti C4 aperti vicino alla porta della saletta): distanza statica 879 mm; cassetti C4 aperti: residuo 879 mm. Esito limitato alla non sovrapposizione degli ingombri d'uso. | ipotesi |
| FP05 | Compatibile nelle ipotesi attuali | SCRIVANIA–C4 (sedia operatore e cassetti C4 aperti): distanza statica 1450 mm; mobili chiusi: residuo 1450 mm; seduta occupata: residuo 700 mm; cassetti C4 aperti: residuo 1100 mm; seduta occupata e cassetti aperti (simultaneità da confermare): residuo 350 mm. Esito limitato alla non sovrapposizione degli ingombri d'uso. | ipotesi |
| FP09 | Compatibile nelle ipotesi attuali | C2–SCRIVANIA (uso cassetti C2 e sedute della scrivania): distanza statica 599 mm; mobili chiusi: residuo 599 mm; cassetti C2 aperti: residuo 275 mm; seduta occupata: residuo 580 mm; seduta occupata e cassetti C2 aperti: residuo 230 mm. Esito limitato alla non sovrapposizione degli ingombri d'uso. | ipotesi |

## Porte

| ID | Esito | Dettaglio | Stato dei dati |
| --- | --- | --- | --- |
| APPR-P_SAL | Conflitto | P_SAL: nella zona di accesso di 900 mm davanti al vano (screening): C4 (220 × 20 mm dentro la zona). | ipotesi |
| CLEAR-P_ING | Non verificabile (dato mancante) | P_ING: luce netta di passaggio non documentata. | da definire |
| SWING-P_ING | Compatibile nelle ipotesi attuali | P_ING: vano 900 mm, anta 900 mm (verso l'interno, cerniera a sinistra): nessuna interferenza; stato delle dipendenze (porta, muro, ostacoli vicini): ipotesi. | ipotesi |
| SWING-P_SAL | Compatibile nelle ipotesi attuali | P_SAL: vano 900 mm, anta 850 mm (verso l'interno della saletta, cerniera a destra): nessuna interferenza; stato delle dipendenze (porta, muro, ostacoli vicini): ipotesi. | ipotesi |
| HOST-P_ING | Coerente (solo geometria) | P_ING: vano e muro ospite coerenti; cerniera, anta e verso coerenti. | ipotesi |
| HOST-P_SAL | Coerente (solo geometria) | P_SAL: vano e muro ospite coerenti; cerniera, anta e verso coerenti. | ipotesi |

## Accostamenti dichiarati (muro e lato)

| ID | Esito | Dettaglio | Stato dei dati |
| --- | --- | --- | --- |
| ADJ_C1_FONDO | Coerente (solo geometria) | C1 lato y1 → FONDO (retro contro la parete di fondo): distanza 0 mm, tratto di affaccio 1500 mm. Solo vincolo geometrico: posto operatore e uso a parte. | ipotesi |
| ADJ_C2_C3 | Coerente (solo geometria) | C2 lato x1 → C3 lato x0 (affiancate sul fronte saletta): distanza 0 mm, tratto di affaccio 400 mm. Solo vincolo geometrico: posto operatore e uso a parte. | ipotesi |
| ADJ_C2_WSAL | Coerente (solo geometria) | C2 lato y1 → W_SAL_S1 lato y0 (retro contro il tramezzo): distanza 0 mm, tratto di affaccio 1200 mm. Solo vincolo geometrico: posto operatore e uso a parte. | ipotesi |
| ADJ_C3_WSAL | Coerente (solo geometria) | C3 lato y1 → W_SAL_S1 lato y0 (retro contro il tramezzo): distanza 0 mm, tratto di affaccio 1200 mm. Solo vincolo geometrico: posto operatore e uso a parte. | ipotesi |
| ADJ_C4_DESTRA | Coerente (solo geometria) | C4 lato x1 → PARETE_DESTRA (retro contro la parete laterale destra): distanza 0 mm, tratto di affaccio 1500 mm. Solo vincolo geometrico: posto operatore e uso a parte. | ipotesi |
| ADJ_CASSA_SINISTRA | Coerente (solo geometria) | CASSA lato x0 → PARETE_SINISTRA (fianco a contatto con il muro sinistro): distanza 0 mm, tratto di affaccio 600 mm. Solo vincolo geometrico: posto operatore e uso a parte. | da definire |
| ADJ_ISOLA_RINGHIERA | Coerente (solo geometria) | ISOLA_SMART lato x0 → RINGHIERA (asse) (lato lungo parallelo alla ringhiera (distanza dall'asse; luce netta in FP07)): distanza 50 mm, tratto di affaccio 1600 mm. Solo vincolo geometrico: posto operatore e uso a parte. | ipotesi |

## Prossimità non dichiarate

| ID | Esito | Dettaglio | Stato dei dati |
| --- | --- | --- | --- |
| PRX-C1-W_SAL_O | Avviso | C1–W_SAL_O: 50 mm, relazione non dichiarata (accostamento o passaggio da stabilire). | ipotesi |
| PRX-C2-W_SAL_O | Avviso | C2–W_SAL_O: 110 mm, relazione non dichiarata (accostamento o passaggio da stabilire). | ipotesi |

## Parete smart

| ID | Esito | Dettaglio | Stato dei dati |
| --- | --- | --- | --- |
| SMART-IMG | Non verificabile (dato mancante) | Immagini dei pannelli: immagini dei quattro pannelli non presenti nel repository: segnaposto dichiarati nelle tavole e nei render. | da definire |
| SMART-FIT | Compatibile nelle ipotesi attuali | Parete smart 2070 mm: 4 telai esterni da 410 mm (immagine 380 mm), distanza libera fra telai 60 mm, interasse 470 mm; sviluppo dei telai 1820 mm; margini 125 / 125 mm. | ipotesi |

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
| EL-IN-E05 | Avviso | E05 cade dentro l'ingombro di ISOLA_SMART: alternative A: scatola a pavimento sotto l'isola, passacavo nel fondo del mobile e accesso dall'anta / B: canalina dalla parete di fondo lungo la ringhiera (visibile: da valutare con l'estetica) / C: isola solo espositiva senza alimentazione (luce prodotto a batteria). scegliere A/B/C; la posa sotto arredo non è disegnata come definitiva | ipotesi |
| EL-IN-E06 | Avviso | E06 cade dentro l'ingombro di SCRIVANIA: alternative A: torretta o scatola a pavimento sotto la scrivania con passacavi nel piano / B: dalla parete laterale (zona C4) con canalina a pavimento fino alla scrivania (attraversa la zona sedia). scegliere A/B; la posa sotto arredo non è disegnata come definitiva | ipotesi |

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
