# Revisione R02 — correzioni, verifiche e punti aperti

Modello **P02** (da P01, baseline `129e25f`), 21/11/2026. Elaborati PRELIMINARE - NON PER CANTIERE.
Fonte unica: `config/geometry.json`; geometria 3D unica: `src/components.py` (stessi solidi per pianta, prospetti, D01, abaco, controlli e render).

## Sintesi

- **Corretti nel software:** ingombri esterni (H01), quote Z comuni 2D/3D (H02), L×P×H prodotto separato da X×Y di posa (H03), prospetti e registri ricavati dalle pareti per ID (H04), lessico 60 = distanza libera / 470 = interasse (H06), raccordo mensola–cubotto senza sovrapposizioni non spiegate (H07), registro utenze completo (H08), accostamenti per muro e lato (G01), stato dalle dipendenze (G02), muro ospite delle porte (G03), percorso separato dalla collisione (G04), requisito scala–cassa misurato sugli ingombri completi (G05).
- **Restano aperti (decisione o dato):** il requisito scala–cassa **non è soddisfatto** con la cassa sul muro sinistro (luce 250 mm, mancano 750–950 mm di fascia); passaggio C3–scrivania 230 mm con cassetti aperti; C4 dentro la zona d'accesso alla saletta per 220 × 20 mm. Per ciascuno ci sono proposte quotate in `proposte_layout.md` (V1–V4) e nessun mobile del layout approvato è stato spostato.
- **Nessuna quota è stata promossa a `verified`.** Tutti i «compatibile» valgono solo nelle ipotesi attuali.

## Tre livelli distinti

| Livello | Significato | Dove si vede |
| --- | --- | --- |
| Corretto nel software | Il codice ora calcola o disegna correttamente dal modello; lo provano i test. | Stato «corretto ora» nella tabella, test indicati |
| Compatibile nelle ipotesi | Il controllo non trova conflitti con quote `assumed`/`catalog`/`pending`: non è un'approvazione. | `criticita.md`, esito «Compatibile nelle ipotesi attuali» |
| Verificato con fonte | Solo con dati `verified` e fonte (rilievo, scheda firmata). **Oggi nessun controllo è in questo stato.** | Esito «Superato» (assente in P02) |

## Tabella H01–H09, G01–G05

| ID | Stato | Evidenza iniziale | Intervento | Prima e dopo | Verifica | Residuo |
| --- | --- | --- | --- | --- | --- | --- |
| H01 Ingombri esterni isola e cassa | corretto ora | Render: top isola 410 × 1620 contro 390 × 1600; top cassa 1220 × 620 a z 1025, sporgente oltre x 0 e y 4750. | Ogni arredo è un insieme di componenti (zoccolo, corpo, top, marchio) contenuti nell'impronta dichiarata (`outer_envelope: true`); il top fa parte dell'altezza totale. Il render usa gli stessi componenti. | Isola 410 × 1620 → **390 × 1600 × 830**; cassa 1220 × 620 × 1025 → **1200 × 600 × 1000**, top 975–1000 dentro x 0–1200, y 4150–4750. | `test_T01_isola_outer_envelope`, `test_T02_cassa_outer_envelope`, `ENV-*` in `criticita.md`, `test_T09_render_uses_components` (oggetti Blender = componenti) | Prodotti reali di cassa e isola da scheda (cassa `pending`). |
| H02 Quote Z comuni (smart, LED, listelli) | corretto ora | Mensolina 2D 1050–1075 / 3D 1025–1050; cartellino 900–1010 / 790–900; LED 304/560 / 288/544; sommità listelli 3750 / 3700. | Riferimento Z esplicito (`z_ref: base`) per mensolina e cartellino; LED cassettiere come frazioni dell'altezza (assi 0,38 e 0,70 H); un solo parametro `top_gap_from_ceiling` per i listelli, rimosso `slat_top_gap` da `render.json`. Prospetti e render leggono gli stessi solidi. | Mensolina **1050–1075**, cartellino **900–1010**, LED **assi 304 e 560** (H 800), listelli **3750** ovunque. | `test_T03_smart_shelf_and_label_same_z` (rettangoli DXF = solidi), `test_T04_drawer_led_follow_height` (H 800 e H 900 sintetica), `test_T05_slat_top_single_parameter` (soffitto 4150 e 3800 sintetico) | Quote preliminari (ipotesi S4), da confermare in cantiere. |
| H03 L × P × H prodotto e posa | corretto ora | AB01 chiamava L × P × H i lati X × Y (C4 400 × 1500, scrivania 700 × 1600, isola 390 × 1600). | `product_dims()` dà L lungo il fronte, P profondità, H totale; AB01 separa prodotto, fronte/rotazione, ingombro X × Y e posizione, con stati distinti. | C4 **1500 × 400 × 800**, rotazione 90°, X × Y 400 × 1500; scrivania **1600 × 700 × 760**; isola **1600 × 390 × 830**. | `test_T06_product_dims_independent_of_rotation` (C4 ruotata: L/P/H invariati, X/Y scambiati) | Dimensioni di catalogo da ricontrollare su schede. |
| H04 Prospetti e quote dal modello | corretto ora | `ELEVATIONS` e costanti Q01 fissi nel generatore; la saletta aveva poligoni duplicati dei tramezzi. | `elevations` in `geometry.json` con muro ospite per ID (`FONDO`, `SALETTA:-x`, `SALETTA:-y`, `PARETE_DESTRA`); facce, estremi e sviluppo calcolati; saletta ricavata dai tramezzi (`bounded_by`); Q01 legge lati e muri dal modello. | Spostando W_SAL_O di −100 mm (prova sintetica): prima F02 perdeva tutti gli elementi; ora la faccia segue il tramezzo, i 17 componenti si spostano di 100 mm e Q01 riporta la nuova quota. | `test_T07_wall_move_updates_elevation_and_registers`, `test_T02_saletta_topology` | Nessuno nel software; misure dei muri da rilievo. |
| H05 Esposizione e specchio sulla parete cassa | corretto ora (composizione in ipotesi) | Mancavano esposizione sopra la cassa e colonna listelli/specchio sulla parete di fondo. | Proposta espositiva anche sopra la CASSA (4 mensole sfalsate e cubotto) e colonna **LS3** (listelli + specchio) fra cassa e C1; stessi componenti in F01, AB01 e render. Distanza fine mensole C1–telaio smart 150 mm (proposta). | F01 prima: cassa e C1 senza composizione → ora cassa + esposizione, LS3 x 1360–1680, C1 + esposizione. | F01, render `R01_ingresso_verso_cassa.png`, confronto qui sotto | Adattamento compositivo da approvare: dimensioni di mensole, cubotti e colonna sono proposte, non misure dal render. |
| H06 Pannelli smart, distanze e grafica | corretto ora (grafiche mancanti) | «Interasse 60» nei documenti; cornici +15 per lato fuori dall'ingombro dichiarato. | Schema `frame_outer_width 410`, `clear_gap 60`, `frame_border 15` (immagine 380), interasse calcolato 470; telai, immagini, mensoline e cartellini con testi S4 come componenti. Corretto anche il rapporto R01. | 4 × 410 + 3 × 60 = **1820** = fascia S2, margini 125/125; **interasse 470**; immagini 380 × 670 segnaposto. | `test_T09_smart_panels_gap_and_interaxis`, `test_T10_smart_images_declared_placeholders`, `test_T10_smart_elevation` | Immagini dei 4 pannelli e prodotti da fornire (`pending`); montanti neri della reference non modellati. |
| H07 Raccordo mensole/cubotti e D01 | corretto ora (dettaglio preliminare) | Cubotto C1 (2827–3177, z 1575–1925) sovrapposto alla mensola (1840–3190, z 1850–1875); D01 assente. | Cubotto appoggiato sulla mensola inferiore, mensola superiore **interrotta sul fianco** (giunto dichiarato); cubotto in 5 pezzi senza intersezioni; D01 a 1:10 disegnato dai componenti: sezione mensola+LED, nodo C1, sezione cassettiera con LED in fresata e vano driver, sezione colonna listelli. | Prima: sovrapposizione 350 × 250 × 25. Dopo: **0** sovrapposizioni non spiegate su 139 componenti (solo intarsi dichiarati). | `test_T11_no_unexplained_overlaps`, `OVL3D` in `criticita.md`, D01 | Staffe, carichi, ferramenta, schede LED/driver: aperti. |
| H08 Registro utenze E01 | corretto ora | La tabella E01 ometteva quantità e percorso; E05/E06 senza dettaglio di collegamento. | `E01_registro_utenze.md` con ID, servizio, tipo, quantità, X/Y e Z con stato e fonte, supporto, accesso, driver, percorso e dati mancanti; Z verificata mostrata come tale; E05/E06 con alternative A/B(/C) e decisione aperta, nessuna posa sotto arredo disegnata come definitiva. Nei prospetti solo tacca di posizione e «Z DA RILEVARE». | Prima: campi troncati → ora 11 utenze complete; E07–E09 senza coordinate fittizie. | `test_T12_electrical_register`, `test_T12_electrical_and_deliverables` | Z, potenze, circuiti, protezioni e scelta A/B/C: tecnico incaricato. |
| H09 Test, rigenerazione, consegna | corretto ora | Test basati su stringhe; nessun legame fra render e revisione. | Test geometrici R02 (T01–T26), `render_meta.json` con la revisione di ogni immagine, MANIFEST che dichiara il set incompleto se manca un render o la revisione non coincide; vista dall'alto come sezione (soffitto, architravi e binari nascosti solo nell'immagine). | Vedi «Risultati dei test» e «File consegnati». | `test_T23_render_manifest_detects_missing`, `test_T23_render_set_current_revision` | — |
| G01 Accostamento al muro e al lato | corretto ora | Cassa spostata a x 3000, y 0 restava «accostamento OK». | Ogni accostamento dichiara lato del mobile e supporto (muro per nome o mobile/tramezzo con lato); controlli di lato, parallelismo, verso, distanza e tratto di affaccio. | Sonda x 3000, y 0: prima OK → ora **CONFLITTO** (distanza 3000 da PARETE_SINISTRA). | `test_T13_cassa_on_wrong_wall`, `test_T14_side_and_segment` | Posto operatore della cassa da definire (verifica separata). |
| G02 Stato dalle dipendenze | corretto ora | P_SAL `verified` da sola portava a «SUPERATO» con ostacoli in ipotesi. | Ogni esito porta l'elenco delle dipendenze e lo stato più debole; «Superato» solo con tutte verificate. | Sonda P_SAL `verified`: prima SUPERATO → ora **Compatibile nelle ipotesi** con dipendenze elencate. | `test_T15_verified_door_with_assumed_obstacles`, `test_T16_missing_and_colliding` | — |
| G03 Porta, vano e muro ospite | corretto ora | P_ING a x 9000–9900 risultava compatibile (nessun ostacolo). | Controllo `HOST-` prima della collisione: muro/facciata ospite, cerniera su un estremo del vano, verso dell'apertura nel locale dichiarato. | Sonda P_ING x 9000: prima compatibile → ora **CONFLITTO** di collocazione; cerniera incoerente → CONFLITTO. | `test_T17_door_outside_shop`, `test_T18_hinge_inconsistent` | Larghezze utili e altezze delle porte da rilevare. |
| G04 Percorso distinto dalla collisione | corretto ora | FP05 1450 − 750 − 350 = 350 trattato solo come «non collisione»; criterio scelto dalle parole della descrizione. | Coppie funzionali a **scenari** (mobili chiusi, seduta, cassetti, simultanei) e controllo di **percorso** separato (`-PERCORSO`) con criterio esplicito; nessuna logica dal testo libero. | FP05: collisione compatibile 1450, percorso **residuo 350, non verificabile** (criterio mancante). FP02: percorso **230 < 900 conflitto**. | `test_T19_*`, `test_T20_description_does_not_change_outcome`, `test_T21_unknowns_stay_open`, `test_T22_baseline_conflicts_still_detected` | Criterio di passaggio e simultaneità da stabilire con la committenza. |
| G05 Scala–cassa 1000–1200 mm | decisione aperta | Scala y 1500–3900, cassa y 4150–4750: luce 250; fascia 850 contro 1600–1800 necessari. | Requisito `REQ_SCALA_CASSA` (committenza) misurato fra foro scala e ingombro completo della cassa (top compreso); quota in A01; analisi di fattibilità e varianti quotate. Scala non accorciata né spostata; differenza di 50 mm rispetto a P00 (3850) documentata. | Prima: nessun controllo → ora **CONFLITTO 250 mm, mancano 750–950 mm**. V1 (cassa sul fondo x 1850–3050, C1 x 0–1500): luce **1031 mm**, ma viola «cassa sul muro sinistro». | `test_T25_stair_cash_clearance` (250/999 insufficienti; 1000/1100/1200 solo criterio numerico), `test_T26_feasibility_and_provenance` | Scegliere: rilievo di fine scala e parapetto, banco meno profondo, oppure deroga V1. |

## Proposte quotate per gli spazi ancora critici

Dettaglio con confronto dei controlli in [`proposte_layout.md`](proposte_layout.md); pianta della variante principale in `A01_V1_proposta.pdf`. Il modello di base resta invariato.

| Variante | Cosa cambia | Effetto | Vincoli toccati |
| --- | --- | --- | --- |
| Muro sinistro (analisi) | — | Banco P 600/500/450: la scala dovrebbe finire entro y 3150/3250/3300 (oggi 3900). Verso la vetrina la cassa finirebbe dentro l'apertura della porta d'ingresso. | Nessuna soluzione nelle ipotesi P02 senza rilievo. |
| V1 | CASSA x 0 → 1850 (parete di fondo), C1 x 1840 → 0, LS3 x 1360 → 1515 | Luce scala–cassa 1031 mm (non verificabile finché non si rileva il parapetto); C1–cassa 350 mm. | **Deroga** a «cassa sul muro sinistro»: serve la tua approvazione. |
| V2 | C4 y 300 → 280 | Zona d'accesso P_SAL libera (900); C4–facciata 280 mm. | Nessuno; da confermare col serramento. |
| V3 | Scrivania lunga 1400 invece di 1600 | C3–scrivania 580 → 780; con cassetti 230 → 430, ancora < 900. | Prodotto da cambiare (scheda). |
| V4 | Percorso verso la saletta dal corridoio scrivania–C4 | Toglie il conflitto FP02-PERCORSO, ma il residuo FP05 con sedia e cassetti simultanei è 350 → conflitto. | Criterio d'uso da decidere. |

## Confronto F01 e vista cassa con la reference (H05)

Reference: `assets/approved/viste_approvate.png` (vista alta superiore). Confronto qualitativo, nessuna misura ricavata dalla prospettiva.

| Elemento della reference | F01 / render P02 | Esito |
| --- | --- | --- |
| Esposizione con mensole bianche e cubotto rovere sopra la cassa | 4 mensole sfalsate + 1 cubotto sopra CASSA (F01 sinistra, render) | presente; nella reference i cubotti sono due e c'è la scritta «lenti a contatto»: adattamento da confermare |
| Colonna listelli rovere con specchio fra cassa e cassettiera | LS3 x 1360–1680, specchio 250 × 1000 da quota 1300 | presente |
| Cassettiera noce con due linee LED sulla parete di fondo, esposizione sopra | C1 1500 × 400 × 800, LED assi 304/560, mensole e cubotto | presente |
| Cassa bianca con marchio sul frontale, fianco al muro sinistro | CASSA al muro sinistro, marchio ufficiale `assets/brand` | presente; **viola il requisito 1000–1200 mm** (G05) |
| Scala con ringhiera e isola bianca lungo la ringhiera | isola 390 × 1600 a 50 mm dall'asse ringhiera | presente |
| Parete smart in mattoni con 4 pannelli, mensoline e cartellini | F02 e render: 4 telai, mensoline e cartellini con i testi S4 | presente; immagini e montanti neri da fornire/definire |
| LED zoccolo cassa, binari con faretti | non modellati come componenti tecnici | solo estetica, nessuna potenza dedotta |

## File consegnati (rev. P02)

| File | Contenuto |
| --- | --- |
| `A01_pianta_arredi_preliminare.dxf/.pdf` | Pianta arredi 1:50 con ingombri d'uso e quota scala–cassa |
| `A01_V1_proposta.dxf/.pdf` | Variante V1 da approvare (cassa sul fondo) |
| `E01_punti_utenza_preliminari.dxf/.pdf` + `E01_registro_utenze.md` | Utenze e registro completo |
| `F01`–`F04_*.dxf/.pdf` | Prospetti 1:20 dalle facce del modello |
| `D01_dettagli_schema_preliminare.dxf/.pdf` | Dettagli schematici 1:10 dai componenti |
| `AB01_abaco_arredi.md`, `Q01_quote_aperte.md`, `criticita.md`, `proposte_layout.md`, `MANIFEST.md` | Registri |
| `render/R01_*.png` + `render/render_meta.json` | Quattro viste dalla revisione P02 |

Le sei tavole richieste sono A01, E01, F01, F02, F03, F04 (più D01 e la variante A01-V1).

## Risultati dei test e comandi

- Baseline `129e25f`: `pytest -q` → 19 passed; `python -m src.generate` → completato.
- P02: `pytest -q` → **54 passed, 0 failed, 0 skipped** (19 test P01 aggiornati + 33 casi R02 + 2 di riproducibilità; il test di scena Blender gira perché `bpy` è installato, in CI senza `bpy` risulta skipped).
- `python -m src.generate` → completato: 8 tavole DXF+PDF (sei richieste più D01 e A01-V1) e i registri elencati in `MANIFEST.md`.
- `python -m src.render` → 4 viste, revisione P02 registrata in `render_meta.json`.

## Misure da chiedere al geometra (in ordine di impatto)

1. **Fine della scala e parapetto/corrimano in testa alla scala** (y di fine foro, ingombro e spessore): decide G05.
2. Posizione e spessore della ringhiera lungo l'isola (luce netta isola–ringhiera, FP07).
3. Lati dell'involucro, diagonali e fuori squadra; quota del soffitto e ribassamenti (sommità listelli).
4. Tramezzi della saletta (W_SAL_O, W_SAL_S1/S2) e vano P_SAL: posizione, spessore, larghezza utile, altezza.
5. Porta d'ingresso P_ING: vano, luce netta, anta, cerniera e verso; serramenti vetrina (FP06).
6. Quote Z e posizioni effettive di prese, dati e alimentazioni (E01–E11), compresi E07–E09 senza posizione.

L'elenco completo, riga per riga con stato e fonte, è `Q01_quote_aperte.md`.

## Schede prodotto da acquisire

- Cassa (Amazon): L × P × H, top, zoccolo, lato operatore e vani; variante definitiva.
- Cassettiere Lumio 150 e varianti 120: dimensioni, zoccolo, fresata/profilo LED, estrazione cassetti.
- Scrivania Homary: dimensioni (1600 o 1400), cassettiera, passacavi.
- Isola Monfero: misure finali, apertura ante, passacavi per E05.
- Profili LED, driver (dimensioni e aerazione), staffe per mensole e carichi, fissaggio specchi.
- Immagini dei quattro pannelli smart e prodotti esposti.

## Decisioni chieste a Sherin

1. G05: rilievo prima (consigliato), banco meno profondo, oppure deroga V1 con cassa sul fondo.
2. C3–scrivania: scrivania da 1400 (V3), percorso dal corridoio (V4) o accettare il passaggio con cassetti chiusi.
3. C4: arretrarla di 20 mm (V2).
4. E05/E06: modalità di collegamento A/B/C.
