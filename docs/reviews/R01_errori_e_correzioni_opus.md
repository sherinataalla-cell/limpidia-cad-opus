# Limpidia - correzioni da eseguire in Opus

Data della revisione: 21 novembre 2026. Identificativo: REVIEW-R01.
Questo documento è una richiesta operativa di correzione del modello e degli elaborati preliminari.

## 1. Incarico e versione controllata

Repository: https://github.com/sherinataalla-cell/limpidia-cad-opus
PR controllata: https://github.com/sherinataalla-cell/limpidia-cad-opus/pull/1
Branch osservato: claude/project-thread-uc9o0p
Commit esaminato: 63373a5a028f69c4ec065fe68090572f28f3cb54
Base della PR al controllo: 7dd50e985d4130fba441412643ca406a2f5363e7

Correggi gli errori qui descritti, preservando le decisioni approvate e le eventuali modifiche più recenti della committenza. La correzione dell'orientamento potrebbe essere già in corso.

Il commit indicato identifica la versione analizzata: NON è una richiesta di ripristinarla. All'inizio registra il tuo HEAD effettivo, confrontalo con questa versione e classifica ogni punto come ancora presente, già corretto, superato da una decisione successiva oppure da verificare. Per un punto già risolto porta la prova e aggiungi soltanto il controllo mancante.

Questa patch aggiunge istruzioni, prove e riferimenti in nuove cartelle. Non modifica automaticamente geometria, generatore, render o tavole. L'implementazione richiesta a Opus comincia dopo la lettura.

La revisione ha letto il codice e riprodotto i calcoli geometrici. Ha ispezionato la planimetria precedente e il render approvato allegati. Non ha aperto i tre PNG prodotti dalla PR: le osservazioni sul renderer derivano dal codice che li genera. Non dichiarare come nostra una verifica grafica di quei PNG o un'esecuzione completa di pytest.

Una parte dei problemi è già nella geometria iniziale: attribuirli alla fonte corretta, senza presentarli tutti come introdotti da Opus.

## 2. Fonti e ordine da rispettare

1. Istruzioni più recenti della committenza e rilievi/documenti verificati eventualmente sopraggiunti.
2. Planimetria di riferimento e relativo sistema di orientamento, mantenendo preliminari le quote non rilevate.
3. Schede della variante effettiva degli arredi: dimensioni di prodotto separate da posizione nel locale.
4. Decisioni approvate in docs/decisioni.md.
5. Render approvato: materiali, composizione e carattere dell'arredo. Non è una fonte metrica.

Gli allegati sono in assets/review_R01/:

| Codice | File | Uso corretto |
| --- | --- | --- |
| S1 | planimetria_preliminare_2026-11-13.pdf | Pianta preliminare: fronte strada in basso, ingresso e scala a sinistra, saletta sul fondo a destra. |
| S2 | studio_cassa_smart_p12.png | Pagina 12 dello studio cassa: fianco saletta circa 2070 mm; sviluppo smart riservato 1820 mm; parete di fondo circa 3390 mm. |
| S3 | quote_modello_precedente_p30.png | Pagina 30 del modello precedente: quote preliminari, soffitto 4150 mm e superficie con foro scala incluso. |
| S4 | render_approvato_v6.jpeg | Immagine approvata con pavimento rovere sbiancato, pareti beige, noce, mensole e cubotti. |

S2 e S3 sono immagini delle pagine originali, non nuovi disegni. Il registro assets/review_R01/README.md documenta la provenienza. Le vecchie quantità e posizioni d'arredo nelle pagine storiche NON sostituiscono le decisioni più recenti sui quattro contenitori e sui prodotti scelti.

La presenza del file approvato assets/approved/viste_approvate.png è stata controllata sul commit analizzato: mancava. S4 rende disponibile il riferimento originale. Se una reference più recente è già presente, confrontale e conserva quella approvata più recente. Non rinominare un JPEG in PNG senza conversione, non sostituire in silenzio un'immagine già presente.

## 3. Vincoli d'arredo da conservare

- Quattro cassettiere noce: C1 sul fondo di fronte alla vetrina; C2 e C3 sul fronte saletta; C4 sulla parete laterale parallela al lato lungo della scrivania.
- Le larghezze restano varianti da verificare: C1 1200/1500 mm; C2 e C3 candidate da 1200 mm; C4 candidata da 1500 mm. Non trasformare questa preferenza in ordine confermato.
- Cassa bianca con fianco a contatto con il muro sinistro. Il suo ingombro 1200 x 600 mm nel modello è un segnaposto; il lato operatore va definito.
- Scrivania nell'angolo verso la vetrina, parallela all'esposizione laterale; preservare accesso all'esposizione e spazio per le sedute.
- Isola Monfero, lato lungo parallelo alla ringhiera, ante verso la vendita, profondità entro 400 mm. Riferimento prodotto 1600 x 390 x 830 mm, da confermare sulla variante. La sua posa non è verificata.
- Pareti espositive beige sabbia opaco; pavimento rovere sbiancato; mattoni marrone scuro nella zona smart, finitura coerente nelle due viste.
- Mensole bianche sfalsate, cubotti aperti in rovere, specchi con listelli continui sopra e sotto, due linee LED nei frontali delle cassettiere.
- Quattro pannelli smart con immagini, titoli, ripiani prodotto e cartellini. Occhiali e confezioni a scala plausibile.
- Marchio ufficiale Limpidia sul frontale bianco della cassa; nessuna scritta/logo aggiunta sopra le mensole. Usare il file ufficiale, senza ridisegnare il marchio con un font approssimativo.

Le foto precedono alcune scelte di prodotto: per esempio il mobile Monfero scelto successivamente prevale sull'isola generica visibile nel render. Non ricopiare dimensioni, numero di moduli o orientamento della scrivania dalla prospettiva della foto.

## 4. Ordine di lavoro

- P0: correggere orientamento, involucro/saletta, aperture e contenimento; rendere valutabili gli ingombri.
- P1: correggere controlli e stato delle quote, riconciliare le altezze, rendere fedeli i componenti e coordinare E01.
- P2: completare gli elaborati mancanti sulla base corretta.

Procedi con il lavoro determinabile dai documenti. Le informazioni mancanti vanno nel registro delle quote aperte; non devono impedire le correzioni indipendenti. Se una scelta modifica una decisione approvata, prepara una proposta quotata separata e rendi esplicito il punto da decidere.

## 5. Registro degli errori e criteri di accettazione

### R01-01 / P0 - Orientamento e pianta specchiata

**Riscontro.** Il JSON definisce origine al fondo sinistro, X verso destra e Y verso la vetrina. src/generate.py passa quelle coordinate direttamente al CAD e colloca la vetrina a Y massimo; la vista standard mette quindi la vetrina in alto. S1 ha invece strada in basso, ingresso e scala a sinistra, saletta in alto a destra. Anche src/render.py trasferisce X/Y direttamente a Blender.

**Correzione.** Definisci e documenta un sistema di coordinate coerente e una sola trasformazione fra coordinate della pianta, CAD e scena 3D. Puoi normalizzare il modello oppure usare adattatori comuni. Trasforma insieme geometria, aperture, simboli, punti elettrici, quote, camere e target. Ricrea i testi leggibili. Una rotazione di 180 gradi o lo specchio del solo PNG non dimostrano la correzione e possono scambiare la destra con la sinistra.

**Accettazione.** Pianta ortogonale e vista dall'ingresso coerenti con quattro ancore: ingresso a sinistra, scala a sinistra, saletta sul fondo a destra, vetrina fissa a destra. A01, E01, prospetti e 3D mostrano gli stessi ID nelle stesse posizioni fisiche. Distanze e superfici restano invariate dopo una sola trasformazione. Se la correzione è già nel tuo HEAD, non applicarla una seconda volta.

**File:** config/geometry.json; src/generate.py, draw_base; src/render.py, box/build_scene/camere.

### R01-02 / P0 - Saletta e parete smart accorciate

**Riscontro numerico.** SALETTA è un rettangolo x=3450, y=450, larghezza=4050, profondità=1620 mm. Il fronte arriva a y=2070. Il fianco smart è quindi lungo 1620 mm. Il rientro di 450 mm dell'involucro riguarda soltanto la fascia x=5500..7500; applicarlo all'intera saletta lascia una striscia vuota sul retro sinistro.

S2 indica un fianco di circa 2070 mm e una fascia smart di 1820 mm, entrambi preliminari. La differenza fra 2070 e 1620 è 450 mm, circa il 21,7% del precedente fianco: non è soltanto un effetto prospettico.

**Correzione.** Modella la saletta come geometria articolata che segue il rientro, distinguendo facce esterne, spazio netto e spessori. Non allungare un rettangolo su tutta la larghezza: invaderebbe il rientro esterno. Non scalare l'intero negozio per far somigliare il render.

Riconcilia anche lo spigolo a x=3450 con il tratto di circa 3390 mm in S2 e la larghezza netta 4010 mm in S1/S3. Un controllo di coerenza del vecchio modello è: 7500 - 3390 - 100 = 4010 mm; 2070 - 100 = 1970 mm; 1970 - 450 = 1520 mm; 4010 x 1970 - 2000 x 450 = 6.999.700 mm², circa 7,00 m². È una ricostruzione delle ipotesi precedenti, NON un rilievo né un ordine di impostare quelle coordinate senza confronto.

**Accettazione.** Nessuna striscia spuria dietro il lato sinistro e nessuna invasione del rientro. Lunghezza del fianco, lunghezza effettivamente rivestita e fascia smart sono tre grandezze distinte. Confronto prima/dopo in mm con fonte e stato; area netta calcolata sulle facce interne. Ogni differenza residua da S1-S3 è spiegata.

**File:** config/geometry.json, SALETTA/envelope; src/model.py, bounds; src/generate.py, zone; src/render.py, saletta.

### R01-03 / P0 - Porta della saletta e ingresso mancanti

**Riscontro.** Il renderer chiude il fronte della saletta con una parete continua e la facciata con vetro e zoccolo continui. S1 mostra porta della saletta a destra, verso l'interno, vano preliminare 900 mm e passaggio previsto 850 mm; l'ingresso è sul fronte sinistro. Il modello non contiene aperture, cerniere e aree di apertura. Il messaggio “porta saletta non presente” in checks.py è incondizionato.

**Correzione.** Aggiungi oggetti porta/apertura con supporto murario, posizione, vano, luce utile, verso e fonte/stato. Modella solo i dati documentati, lasciando i restanti pending. Distingui la larghezza del vano dalla luce utile; non inventare distanze dalle spallette. Aggiorna il controllo in base agli oggetti realmente presenti.

**Accettazione.** Varchi visibili sia in A01/E01 sia in 3D, porte rappresentate nella verifica d'uso, nessuna cassettiera o mensola che attraversi il vano. Con porta correttamente inserita il warning “porta assente” sparisce; un'interferenza con l'anta viene invece segnalata.

**File:** config/geometry.json; src/checks.py; src/generate.py; src/render.py.

### R01-04 / P0 - Ingombri funzionali e accesso alla cassa

Le distanze sotto sono riprodotte sul commit analizzato. Sono distanze geometriche fra rettangoli ipotizzati: non sono tutte passaggi né dimostrano fruibilità.

| Relazione | Valore nel modello | Verifica richiesta |
| --- | ---: | --- |
| Cassa - zona scala | 300 mm | Lato operatore, accesso, apertura cassetti, prodotto reale. Non chiamarlo automaticamente “fronte cassa”. |
| C3 - scrivania | 580 mm | Sedute, accesso esposizione e percorso verso la saletta. |
| Cassa - C1 | 640 mm | Stabilire se spazio di servizio, passaggio o semplice intervallo laterale. |
| C4 - saletta | 880 mm | Porta, spallette, ante e uso della cassettiera. |
| Scrivania - C4 | 1450 mm | Sedute occupate/arretrate e cassetti aperti; oggi non appare nel report. |
| Scrivania - linea vetrina | 100 mm | Serramento, pulizia, sporgenze e reale uso del bordo. |
| Isola - asse ringhiera | 50 mm | Spessore e sporgenza reale del corrimano; 50 mm non è luce netta. |

Nel solo render il corrimano si estende 25 mm verso l'isola, riducendo quell'ultima distanza a 25 mm. Anche questa è un'ipotesi di rappresentazione.

**Correzione.** Registra orientamento dei frontali, zone di servizio, sedute, corse dei cassetti e delle ante, porte, ingombro della ringhiera. Le quantità mancanti restano da rilevare o sono espliciti scenari ipotetici. Mantieni i vincoli approvati; proponi alternative solo se serve, mostrando i risultati.

**Accettazione.** Una tavola degli ingombri d'uso distingue: controllo superato su dati documentati, conflitto, non verificabile per dato mancante. Un controllo non eseguito non deve apparire come superato. La soglia 900 mm del codice è soltanto un parametro di screening e non una dichiarazione di conformità.

### R01-05 / P0 - Contenimento nel poligono e pavimento 3D

**Bug riprodotto.** Un oggetto 100 x 100 mm a x=6000, y=100 si trova fuori dal poligono del negozio, nel rientro, ma checks.py non lo segnala perché usa il bounding box del locale. Il pavimento 3D è assemblato sul bounding box e copre anche il rientro 2000 x 450 mm.

**Correzione.** Controlla l'intero footprint contro il poligono reale, considerando concavità, fori e spessori pertinenti. Per poligoni concavi non bastano centro o soli vertici dell'oggetto. Genera il pavimento dal medesimo involucro, escludendo il foro scala. Modella soffitto, ribassamenti ed eventuali aperture superiori secondo le fonti disponibili e il rilievo, senza dedurre un'apertura nel soffitto dalla sola presenza del foro nel pavimento.

**Accettazione.** Il caso di prova nel rientro fallisce il contenimento, un oggetto realmente interno passa, un oggetto che attraversa un bordo viene rilevato. Nessuna superficie di pavimento aggiunta fuori dal locale o sopra il foro scala.

**File:** src/checks.py, envelope_box/findings; src/model.py; src/render.py, pavimento_a/b/c e soffitto.

### R01-06 / P1 - Accostamenti e filtri che nascondono verifiche

**Bug riprodotto.** ACCOSTATO_MM=60 silenzia ogni distanza fino a 60 mm, anche senza un accostamento approvato. Due piccoli mobili a distanza 30 mm non generano il warning di passaggio stretto. VICINO_MM=1200 esclude invece la coppia funzionale scrivania-C4, distante 1450 mm.

**Correzione.** Descrivi gli accostamenti autorizzati per coppia e lato. Un cutoff può ridurre i controlli generici ma non deve eliminare le coppie funzionali dichiarate, i bordi del locale, porte o zone di servizio. Non trasformare ogni intervallo stretto in un passaggio obbligatorio: rendine esplicita la funzione.

**Accettazione.** Il caso da 30 mm non è dichiarato intenzionale senza una relazione esplicita; l'accostamento autorizzato C2-C3 è classificato correttamente; scrivania-C4 e scrivania-vetrina compaiono sempre fra le verifiche pertinenti. Nessuna sovrapposizione viene nascosta come accostamento.

**File:** src/checks.py, clearances/findings; src/generate.py, dims_clearances.

### R01-07 / P1 - Superfici e confronto improprio con 45 m²

**Riscontro.** Il poligono misura 34,725 m² e include il foro scala di 2,04 m². La zona rettangolare SALETTA misura 6,561 m² prima di una definizione coerente degli spessori. Il report chiama 34,7 “m² netti”; S3 specifica invece l'inclusione del foro scala. Il valore 45 è una costante nel codice, non una quota capace di correggere la geometria.

**Correzione.** Distingui superficie del poligono, foro scala, eventuali tramezzi e superficie effettivamente calpestabile. Riporta provenienza e criterio del dato 45 m² oppure indicali come da verificare. Non riscalare la pianta per raggiungerlo e non confrontare 6,561 m² di una zona con 7,00 m² netti come se fossero quantità omogenee.

**Accettazione.** Ogni area ha una definizione e i suoi addendi/sottrazioni. Il confronto con documenti commerciali resta una questione di fonti finché non viene riconciliato.

### R01-08 / P1 - Provenienza e stato di coordinate e quote

**Riscontro.** Le quote dei passaggi sono stampate con il solo suffisso “libero”, senza l'asterisco di non verifica. Un unico status=catalog sull'isola comprende anche x/y ipotizzati. quote_da_rilevare.md omette diverse quote dell'involucro, aperture, scala, saletta, altezze e spessori.

**Correzione.** Separa almeno stato e fonte di dimensioni, posizione, altezza e orientamento. Propaga alle distanze derivate lo stato delle grandezze da cui dipendono. Mantieni ID e dati metrici in un modello comune; i renderer non devono introdurre una seconda geometria tecnica. Amplia Q01 a tutte le quote mancanti.

**Accettazione.** Nessun numero derivato da coordinate assunte appare verificato. Una scheda di catalogo può confermare una dimensione ma non la posa nel negozio. Il registro consente l'inserimento futuro di dati verificati senza romperne i test.

**File:** config/geometry.json; config/render.json; src/generate.py, mark/dims_clearances/registro quote; tests/test_model.py.

### R01-09 / P1 - Altezze, soffitto e camere

**Riscontro.** config/render.json usa soffitto 3000 mm; S3 riporta 4150 mm preliminari. Il renderer usa cassettiere alte 800 mm e scrivania 760 mm come ipotesi visive. Le tre camere hanno focale 17 mm. Questi parametri influenzano la percezione, ma non spiegano da soli l'errore planimetrico della parete smart.

**Correzione.** Riconcilia altezza del soffitto e ribassamenti locali, senza sostituire automaticamente 3000 con 4150 come se quest'ultimo fosse un rilievo. Verifica le altezze dei mobili sulle varianti effettive. Parametri puramente visivi devono rimanere tali; le quote documentate vanno nella fonte parametrica comune.

**Accettazione.** Una tabella elenca valore precedente, nuovo valore, fonte e stato. Fornisci pianta e prospetto ortogonali per valutare la geometria, oltre alle viste prospettiche. Camere e target sono coerenti con l'orientamento corretto.

### R01-10 / P1 - Arredi, mensole, cubotti, specchi e marchio

**Riscontro nel codice.** Cassa e isola sono blocchi pieni; i cubotti sono cubi pieni da 180 mm. Le mensole sono tre livelli ripetuti. Non risultano oggetti dedicati a specchi, listelli continui o marchio della cassa. La semplificazione è ammessa per un ingombro iniziale, ma non soddisfa il confronto con l'arredo approvato.

**Correzione.** Usa S4 per la composizione e le schede prodotto per i mobili reali. Modella cubotti aperti, ripiani bianchi sfalsati, specchi e listelli sopra/sotto, frontali e due linee LED. Rendi riconoscibili il Monfero e la scrivania scelta, senza risolvere collisioni cambiandone la misura. Usa l'asset ufficiale del logo se disponibile; se manca, registralo come asset da acquisire, senza dichiarare fedele un'approssimazione.

**Accettazione.** Confronto per elementi fra S4 e i nuovi prospetti. Le misure dei pezzi su misura sono proposte esplicite, non “rilevate” dall'immagine. Le schede della variante selezionata vengono archiviate. Gli arredi di catalogo sono distinti dai componenti per il falegname.

### R01-11 / P1 - Pannelli smart rimpiccioliti automaticamente

**Riscontro.** src/render.py calcola w=span/4-80; con span=1620 ottiene quattro pannelli 325 x 422,5 mm. Sono lastre emissive, senza i contenuti, i ripiani e i cartellini approvati.

**Correzione.** Definisci nel modello una composizione smart esplicita: quattro pannelli, margini, interassi, altezza, mensoline, illuminazione prodotto e cartellini. Prima correggi il muro. Se la composizione non entra, segnala il conflitto senza ridimensionarla automaticamente per farlo sparire. Usa 1820 mm di S2 solo come precedente fascia di progetto da riconciliare.

**Accettazione.** Prospetto ortogonale della parete smart con quote e stati; sviluppo totale uguale alla somma di margini, pannelli e interassi. Stessa geometria nelle due viste del negozio. La luce di scena non viene trasferita come potenza elettrica di progetto.

### R01-12 / P1 - E01 incompleta come consegna per l'elettricista

**Riscontro.** Il modello ha otto punti funzionali: E01, E02, E03A/B/C, E04, E05 ed E06, tutti con Z=null. Non sono il conteggio definitivo di prese, circuiti o alimentatori. E05 e E06 cadono all'interno dell'ingombro di isola e scrivania; ciò richiede un dettaglio di collegamento e accesso, non dimostra da solo un errore.

**Correzione.** Per ciascun punto coordina: utenza, mobile/parete associati, X/Y/Z con stato, tipo di supporto, energia/dati/LED, quantità note o pending, modalità di accesso, alimentatore e percorso previsto o da definire. Verifica separatamente luci esposizione, quattro elementi smart, cassettiere, cassa/POS/rete, isola, consulenza, scala e saletta. Non trasportare nel progetto i watt artistici delle luci Blender.

**Accettazione.** Tabella utenze e tavola E01 con gli stessi ID della pianta; dettagli di accessibilità per E05/E06; dati mancanti visibili. Sezioni, protezioni e dimensionamento elettrico devono provenire dal professionista e dai dati reali, non da numeri inventati.

### R01-13 / P2 - Elaborati richiesti ancora mancanti

**Riscontro.** Il generatore produce A01, E01 e due report. CLAUDE.md richiede anche F01-F04, D01, AB01 e Q01. Non presentarli come già consegnati perché il repository ne contiene la richiesta.

**Consegna richiesta dopo la correzione della base.**

| Elaborato | Contenuto minimo |
| --- | --- |
| A01 | Pianta coordinata, aperture, arredi, distanze geometriche e ingombri d'uso. |
| E01 | Predisposizioni e abaco utenze coordinati, dati mancanti dichiarati. |
| F01-F04 | Prospetti fondo/cassa, smart, fronte saletta e laterale consulenza; mapping dei codici documentato. |
| D01 e dettagli necessari | Mensole/cubotti/specchi, profili LED, accesso driver, passaggi cavi; fissaggi da validare. |
| AB01 | Prodotti reali, varianti, dimensioni, finiture, fonte, stato e posa; distinta separata dei pezzi su misura. |
| Q01 | Registro completo delle quote aperte, conflitti e decisioni da prendere. |

**Accettazione.** Manifesto dei file realmente generati con revisione e stato. Modello DXF 1:1 in mm, impaginazione e scala di stampa dichiarate; tutte le tavole preliminari sono marcate PRELIMINARE - NON PER CANTIERE. Non inserire vecchi render nella cartella della nuova revisione senza identificarli.

### R01-14 / P1 - Test e verifica finale

**Riscontro.** I test attuali impongono tutte le Z a null e l'involucro sempre assumed, e cercano la presenza delle parole “saletta” e “cassa” nel report. Queste verifiche possono fallire quando un problema viene risolto correttamente e non proteggono dagli errori principali.

**Correzione.** Usa fixture dedicate per gli stati incompleti e verificati. Implementa i casi in R01_regressioni.json con il nuovo schema. Conserva le verifiche su unità, ID e leggibilità dei file, aggiungendo controlli geometrici concreti.

**Accettazione.**

1. Nessuna regressione di orientamento su pianta, prospetti, E01 e camere.
2. Saletta coerente col rientro e aree calcolate sulle entità appropriate.
3. Caso nel rientro rilevato; oggetti interni validi accettati.
4. Accostamenti solo espliciti; coppie funzionali controllate.
5. Porta mancante/porta presente/porta interferente producono esiti diversi e corretti.
6. Quote derivate con stato non più affidabile delle proprie fonti.
7. Dati validati futuri, incluse Z, accettati senza obbligo di null.
8. Confronto tra A01/E01/render sul medesimo modello e verifica grafica dei file finali realmente aperti.

Esegui pytest -q e python -m src.generate; genera i nuovi render quando la base è corretta. Registra comandi, esiti e limiti. Verifica almeno una quota nota sulla stampa A3 al 100%, senza “adatta alla pagina”, e rendi leggibili cartigli, testi, quote e simboli. Un test di creazione del PDF non sostituisce la sua ispezione.

## 6. Flusso Git senza perdere le correzioni in corso

Leggi prima le istruzioni attuali del repository. Non usare reset --hard, checkout della vecchia baseline o force push per applicare questa revisione.

1. Registra branch, HEAD e modifiche locali presenti.
2. Leggi l'ultimo stato della PR e confrontalo con la baseline dell'audit.
3. Lavora sulla PR attiva se è quella su cui stai già operando, oppure crea un branch di correzione che includa il suo HEAD. Evita di ripartire dal solo main se perderesti il lavoro della PR.
4. La patch aggiunge file in percorsi nuovi. Se uno di essi esiste già, confronta il contenuto e integra; non sovrascriverlo alla cieca.
5. Mantieni separabili correzioni del modello, controlli e rigenerazione degli elaborati.
6. Aggiorna o apri la PR necessaria e lascia il merge alla committenza. Nessun push diretto su main.

Le regole permanenti del repository restano applicabili. Questo incarico autorizza la preparazione delle correzioni su branch; non cambia le decisioni estetiche né autorizza il rilascio esecutivo dei disegni.

## 7. Rapporto che Opus deve restituire

Crea outputs/revisione_correzioni.md usando la prossima revisione libera. Per ciascun ID R01-01..R01-14 riporta:

| ID | Stato iniziale sul tuo HEAD | Intervento o motivo di esclusione | Valore prima/dopo e fonte | Prova o test | Dato residuo |
| --- | --- | --- | --- | --- | --- |
| R01-xx | ancora presente / già corretto / superato / da verificare | Descrizione concreta | Solo se pertinente | File, vista o risultato | Quota/documento da acquisire |

Allega una pianta corretta leggibile, il prospetto smart e le due viste principali aggiornate, oltre ai file tecnici realmente prodotti. Distingui “corretto nel modello”, “compatibile nelle ipotesi attuali” e “verificato con fonte”, senza usare questi stati come sinonimi.

Priorità di chiusura: prima rendere affidabile il confronto geometrico, poi completare gli elaborati e la fedeltà dell'arredo. Non fermarti alla sola specchiatura o a un nuovo render.
