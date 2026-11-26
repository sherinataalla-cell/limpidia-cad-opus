# Criticità e verifiche (generato dal modello)

Revisione modello: P05-V5b. Controlli geometrici e di uso sotto ipotesi dichiarate; da validare con il tecnico. Un controllo «non verificabile» non è superato; «coerente» riguarda solo la geometria.

## Riepilogo

| Esito | Numero |
| --- | ---: |
| Conflitto | 1 |
| Non verificabile (dato mancante) | 29 |
| Avviso | 3 |
| Compatibile nelle ipotesi attuali | 9 |
| Coerente (solo geometria) | 16 |

## Requisiti della committenza

| ID | Esito | Dettaglio | Stato dei dati |
| --- | --- | --- | --- |
| REQ-REQ_SCALA_CASSA | Non verificabile (dato mancante) | luce netta 1127 mm fra SCALE (bordo del foro) e ingombro completo di CASSA; richiesta committenza ≥ 1000 mm, obiettivo 1000–1200 mm: criterio numerico soddisfatto sul solo foro, ma sagoma, estremità e spessore di parapetto/corrimano da rilevare (spessore e sporgenze non rilevati per RINGHIERA, RINGHIERA_TESTATA): la luce reale può essere minore. È una distanza minima fra ingombri, non la larghezza di un percorso. | da definire |

## Ingombri dei componenti (pianta = abaco = render)

7 controlli coerenti su 7.

## Vincoli approvati

| ID | Esito | Dettaglio | Stato dei dati |
| --- | --- | --- | --- |
| DEC-ISOLA-P | Compatibile nelle ipotesi attuali | Isola: profondità esterna 390 mm (prodotto P 390 mm), limite approvato 400 mm. | da catalogo |

## Ingombri d'uso, scenari e percorsi

| ID | Esito | Dettaglio | Stato dei dati |
| --- | --- | --- | --- |
| FP01 | Non verificabile (dato mancante) | CASSA–SCALE (lato operatore / accesso cassa): distanza statica 1127 mm; posto operatore: manca operator_zone. | da definire |
| FP02 | Non verificabile (dato mancante) | C3–SCRIVANIA (C3-scrivania: uso ordinario, movimento seduta e apertura breve dei cassetti C3 (V5b)): distanza statica 980 mm; A uso ordinario: cassetti chiusi, sedute occupate: manca seat_client, seat_operator; mobili chiusi, senza sedute: residuo 980 mm; B movimento occasionale della seduta: manca seat_move; C apertura breve cassetti C3: residuo 630 mm; C apertura breve cassetti C3 con cliente seduto: manca seat_client. | ipotesi |
| FP02-PERCORSO | Non verificabile (dato mancante) | C3–SCRIVANIA: percorso/accesso, scenario «A uso ordinario: cassetti chiusi, sedute occupate» senza dati. | ipotesi |
| FP03 | Non verificabile (dato mancante) | CASSA–C1 (intervallo laterale cassa-fondo: servizio o passaggio da stabilire): distanza statica 350 mm; posto operatore: manca operator_zone. | da definire |
| FP06 | Non verificabile (dato mancante) | SCRIVANIA–FACCIATA (serramento, pulizia e sporgenze verso la vetrina): distanza statica 600 mm; manca il criterio: serramento, sporgenze e uso del bordo da rilevare. | ipotesi |
| FP07 | Non verificabile (dato mancante) | ISOLA_SMART–RINGHIERA (luce netta tra isola e corrimano): distanza statica 50 mm; luce netta: manca railing_thickness. | ipotesi |
| FP08 | Non verificabile (dato mancante) | C1–SCALE (uso di C1: cassetti aperti e persona davanti a C1 verso il foro scala (l'accesso alla scala e' dal lato vetrina, ACC-SCALE)): distanza statica 720 mm; mobili chiusi: residuo 720 mm; cassetti C1 aperti: residuo 370 mm; persona che usa C1 a cassetti aperti: manca drawer_user_zone. | ipotesi |
| FP09 | Non verificabile (dato mancante) | C2–SCRIVANIA (C2-scrivania: uso ordinario, movimento seduta e apertura breve dei cassetti C2 (V5b)): distanza statica 980 mm; A uso ordinario: cassetti chiusi, sedute occupate: manca seat_client, seat_operator; mobili chiusi, senza sedute: residuo 980 mm; B movimento occasionale della seduta: manca seat_move; C apertura breve cassetti C2: residuo 630 mm; C apertura breve cassetti C2 con cliente seduto: manca seat_client. | ipotesi |
| USE-door_leaf_island | Non verificabile (dato mancante) | door_leaf_island per ISOLA_SMART: apertura ante Monfero; da scheda; verifica da eseguire con il dato. | da definire |
| USE-drawer_user_zone | Non verificabile (dato mancante) | drawer_user_zone per C1, C2, C3, C4: spazio della persona davanti ai cassetti aperti (oltre la corsa): dato da definire, non sostituito da ipotesi; verifica da eseguire con il dato. | da definire |
| USE-operator_zone | Non verificabile (dato mancante) | operator_zone per CASSA: lato operatore della cassa non definito; verifica da eseguire con il dato. | da definire |
| USE-seat_client | Non verificabile (dato mancante) | seat_client per SCRIVANIA: ingombro della sedia reale del cliente occupata: da scheda della sedia; non sostituito con 750; verifica da eseguire con il dato. | da definire |
| USE-seat_move | Non verificabile (dato mancante) | seat_move per SCRIVANIA: manovra occasionale della seduta (avvicinamento, alzata, arretramento): da rilevare con la sedia reale; verifica da eseguire con il dato. | da definire |
| USE-seat_operator | Non verificabile (dato mancante) | seat_operator per SCRIVANIA: ingombro della sedia reale dell'operatore occupata (uso compatto, parte sotto il piano): da scheda della sedia; non sostituito con 750; verifica da eseguire con il dato. | da definire |
| ACC-SCALE | Compatibile nelle ipotesi attuali | Accesso a SCALE dal lato -y (indicazione utente 23/11/2026: accesso e discesa dal lato vetrina; il lato verso C1 non e' un accesso): fascia di sbarco 900 mm × 850 mm libera da mobili e fasce d'uso nelle ipotesi. Soglia di screening, non verifica normativa; gradini, alzate e corrimano da rilevare. | ipotesi |
| FP04 | Compatibile nelle ipotesi attuali | C4–P_SAL (cassetti C4 aperti vicino alla porta della saletta): distanza statica 879 mm; cassetti C4 aperti: residuo 879 mm. Esito limitato alla non sovrapposizione degli ingombri d'uso. | ipotesi |
| FP05 | Compatibile nelle ipotesi attuali | SCRIVANIA–C4 (scrivania-C4: percorso ordinario verso saletta ed esposizione C4; apertura breve cassetti separata (V5b)): distanza statica 1540 mm; A uso ordinario: cassetti chiusi: residuo 1540 mm; C apertura breve cassetti C4: residuo 1190 mm. Esito limitato alla non sovrapposizione degli ingombri d'uso. | ipotesi |
| FP05-PERCORSO | Compatibile nelle ipotesi attuali | SCRIVANIA–C4: percorso/accesso nello scenario «A uso ordinario: cassetti chiusi»: residuo 1540 mm ≥ soglia di screening 900 mm (parametro di progetto, non requisito normativo). | ipotesi |

## Porte

| ID | Esito | Dettaglio | Stato dei dati |
| --- | --- | --- | --- |
| APPR-P_SAL | Conflitto | P_SAL: nella zona di accesso di 900 mm davanti al vano (screening): C4 (230 × 20 mm dentro la zona). | ipotesi |
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
| ADJ_CASSA_FONDO | Coerente (solo geometria) | CASSA lato y1 → FONDO (retro contro la parete di fondo (V5)): distanza 0 mm, tratto di affaccio 1200 mm. Solo vincolo geometrico: posto operatore e uso a parte. | da definire |
| ADJ_ISOLA_RINGHIERA | Coerente (solo geometria) | ISOLA_SMART lato x0 → RINGHIERA (asse) (lato lungo parallelo alla ringhiera (distanza dall'asse; luce netta in FP07)): distanza 50 mm, tratto di affaccio 1600 mm. Solo vincolo geometrico: posto operatore e uso a parte. | ipotesi |

## Prossimità non dichiarate

| ID | Esito | Dettaglio | Stato dei dati |
| --- | --- | --- | --- |
| PRX-C2-W_SAL_O | Avviso | C2–W_SAL_O: 110 mm, relazione non dichiarata (accostamento o passaggio da stabilire). | ipotesi |

## Parete smart

| ID | Esito | Dettaglio | Stato dei dati |
| --- | --- | --- | --- |
| SMART-IMG | Non verificabile (dato mancante) | Immagini dei pannelli: immagini dei quattro pannelli non presenti nel repository: segnaposto dichiarati nelle tavole e nei render. | da definire |
| SMART-FIT | Compatibile nelle ipotesi attuali | Parete smart 2260 mm: 4 telai esterni da 410 mm (immagine 380 mm), distanza libera fra telai 60 mm, interasse 470 mm; sviluppo dei telai 1820 mm; margini 125 / 315 mm. | ipotesi |

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
| AREA-PT_DICHIARATO | Non verificabile (dato mancante) | Dato 45 m² (LOC, criterio non indicato (lorda, netta o catastale): da riconciliare con il rilievo, non usare per scalare la pianta) contro 36.01 m² del poligono interno: è una questione di fonti da riconciliare con il rilievo, la pianta non va riscalata. | da definire |
| AREA-SAL | Compatibile nelle ipotesi attuali | Saletta netta 7.65 m² sulle facce interne dei tramezzi (S1/S3 dichiarano 7,00 m² netti di progetto). | ipotesi |

## Superfici

| Definizione | m² |
| --- | ---: |
| involucro (poligono delle facce interne, foro scala incluso) | 36.011 |
| foro scala | 1.972 |
| tramezzi saletta (impronta) | 0.536 |
| saletta netta (facce interne dei tramezzi) | 7.650 |
| saletta lorda (con tramezzi) | 8.276 |
| zona vendita calpestabile (involucro - foro scala - saletta lorda) | 25.763 |
