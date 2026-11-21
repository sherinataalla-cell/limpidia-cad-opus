# R02 — Errori residui e correzioni richieste a Claude Opus

**Progetto:** Limpidia, via Andrea Solari 3, Milano

**Data:** 21 novembre 2026

**Repository:** `sherinataalla-cell/limpidia-cad-opus`

**Branch / PR:** `claude/project-thread-uc9o0p` / #1

**Commit di riferimento:** `129e25f5e45297869ed50ed01be6f99819933c50`

**Stato:** incarico di correzione, aggiornato con la richiesta della committenza di 100–120 cm netti fra scala e cassa; non è una nuova revisione esecutiva.

Questa versione aggiornata sostituisce la precedente patch R02. Se i tre file R02 sono già presenti, confronta e integra questa versione preservando le modifiche successive: non forzare una seconda aggiunta degli stessi file. Questa patch aggiunge le istruzioni e i criteri di accettazione nel repository. **Non corregge già i sorgenti CAD.** Il compito di Opus è implementare le correzioni, rigenerare gli elaborati e verificarne il risultato, non limitarsi a riscrivere questo documento.

## 1. Baseline e lavoro da preservare

La verifica è stata svolta sui sorgenti di `a6eb4a57ff0512389c4c3540116289488f816699` e sugli elaborati finali di `129e25f5e45297869ed50ed01be6f99819933c50`. Tra i due sono cambiati soltanto gli output. Prima di intervenire confronta il tuo HEAD con questa baseline: se un punto è già corretto, documenta la prova e conserva la correzione.

Sono già sistemati e **non vanno riaperti come errori**:

- l'orientamento con vetrina a Y=0, scala a sinistra e saletta sul fondo a destra;
- la saletta a L, il fianco smart di 2070 mm e la composizione esplicita di 1820 mm, con gli stati preliminari documentati;
- il contenimento poligonale dei mobili e il pavimento con foro scala;
- i cubotti aperti e i primi specchi/listelli;
- le sei tavole 2D e la presenza dei quattro render P01 aggiornati;
- titolo e descrizione della PR, ora aggiornati a P01, 19 test e quattro viste.

Il termine “interasse 60” rimasto nella documentazione e nella PR richiede invece la correzione lessicale di H06. Non descrivere la PR come ancora ferma alla P00.

Conserva i vincoli di `docs/decisioni.md`: quattro cassettiere noce; cassa bianca al muro sinistro; scrivania nell'angolo verso la vetrina, parallela alla parete espositiva e con accesso all'esposizione; isola Monfero parallela alla ringhiera con profondità esterna entro 400 mm. Mantieni beige, rovere sbiancato, mattoni marroni, mensole bianche e cubotti in rovere.

**Nuova indicazione della committenza:** tra scala e cassa è richiesto uno spazio libero nell’ordine di **1000–1200 mm**, con **1000 mm come minimo di progetto**. La cassa rimane sul muro sinistro; la sua attuale posizione longitudinale non è un vincolo da conservare se impedisce questa richiesta. Vedi R02-G05. Si tratta di una richiesta progettuale, non di una misura già rilevata né di una soglia normativa.

Le misure attuali di cassa, varianti delle cassettiere, altezze e numerose posizioni non sono ordini o quote di rilievo. Non promuovere `assumed`, `catalog` o `pending` a `verified` senza una fonte appropriata.

## 2. Fonti da leggere

1. `CLAUDE.md`, `docs/decisioni.md`, `config/geometry.json` e `config/render.json`.
2. `docs/reviews/R01_errori_e_correzioni_opus.md` per i vincoli e le correzioni precedenti.
3. `assets/approved/viste_approvate.png`, oppure `assets/review_R01/render_approvato_v6.jpeg`: riferimento estetico, non metrico. Le scelte di prodotto successive prevalgono.
4. `assets/review_R01/planimetria_preliminare_2026-11-13.pdf`, `studio_cassa_smart_p12.png` e `quote_modello_precedente_p30.png`, con la provenienza già registrata.
5. I sei PDF/DXF, i quattro PNG e i registri pubblicati in `outputs/`.

Le evidenze numeriche seguenti provengono dall'audit del codice e dagli elaborati della baseline, non da un nuovo rilievo. Le sonde sintetiche G01–G03 non rappresentano la posa attuale del negozio.

## 3. Priorità e natura degli interventi

“P0” significa da risolvere prima di considerare coordinati gli elaborati; non è una classificazione di rischio normativo.

| ID | Priorità | Intervento | Natura |
| --- | --- | --- | --- |
| H01 | P0 | Ingombri esterni di isola e cassa | Errore riprodotto nel codice 3D |
| H02 | P0 | Quote Z comuni per smart, LED e listelli | Divergenza riprodotta fra 2D e 3D |
| H03 | P1 | Dimensioni prodotto separate dalla posa | Ambiguità verificata in AB01 |
| H04 | P1 | Prospetti e quote derivati dal modello | Dipendenze fisse nel generatore |
| H05 | P1 | Esposizione e specchio sulla parete cassa | Differenza visiva rispetto alla reference |
| H06 | P1 | Pannelli smart, cornici, distanze e grafica | Errore lessicale e componenti da coordinare |
| H07 | P1 | Raccordi mensole/cubotti e D01 | Dettaglio costruttivo da sviluppare |
| H08 | P1 | Registro completo delle utenze E01 | Esportazione e dati aperti |
| G01 | P0 | Accostamento al muro e al lato corretti | Falso positivo riprodotto |
| G02 | P0 | Stato dei controlli derivato da tutte le dipendenze | Falso stato verificato riprodotto |
| G03 | P0 | Porta, vano e muro ospite coerenti | Falso positivo riprodotto |
| G04 | P0 | Percorso distinto dalla non collisione | Verifica funzionale incompleta |
| G05 | P0 | Spazio netto scala–cassa 1000–1200 mm | Nuovo vincolo della committenza |
| H09 | P1 | Test, rigenerazione e consegna coordinata | Protezione delle revisioni future |

Correggi subito i bug che non richiedono nuove decisioni. Per conflitti di layout e misure mancanti prepara alternative quotate e domande precise, mantenendo riconoscibile la soluzione approvata. Non bloccare le correzioni del software in attesa di dati che non sono necessari a eseguirle.

---

## R02-H01 — Ingombri esterni identici in modello, abaco, tavole e render

### Evidenza

`src/render.py:358–372` aggiunge parti fuori dalle dimensioni usate nelle tavole:

| Elemento | Modello tecnico | Scena generata |
| --- | --- | --- |
| Isola, profondità X | 390 mm, X900–1290 | piano X890–1300 = **410 mm** |
| Isola, lunghezza Y | 1600 mm, Y1500–3100 | piano Y1490–3110 = **1620 mm** |
| Cassa | 1200×600×1000 mm | piano 1220×620 mm, sommitàZ1025 |
| Cassa a muro | Xmin0, Ymax4750 | piano fino aX−10 eY4760, oltre le facce dei muri |

La profondità complessiva rappresentata per l'isola supera così il limite concordato di 400 mm. La cassa nel render invade i muri di 10 mm pur risultando contenuta nei controlli sul corpo base.

### Correzione richiesta

Definisci chiaramente se L/P/H del prodotto sono ingombri esterni totali. Modella corpo, top, zoccolo, frontali e sporgenze a partire da quelle dimensioni. Se una sporgenza è documentata, includila nel modello e nei controlli; se non è documentata, non aggiungerla fuori dall'ingombro come dettaglio grafico. Non cambiare l'ingombro dichiarato o la posizione dei mobili per nascondere l'incoerenza. La cassa rimane un prodotto da identificare e quotare: i1200×600×1000 attuali sono un segnaposto, non un ordine approvato.

**Accettazione:** ingombro esterno completo dell'isola non maggiore di 400 mm in profondità; pianta/abaco/render descrivono lo stesso mobile. Tutti i componenti della cassa stanno nell'ingombro dichiarato e non penetrano nei muri. Il test considera l'unione dei componenti, non soltanto il parallelepipedo principale. Eventuali dati di catalogo mancanti rimangono `pending` o ipotesi esplicite.

## R02-H02 — Unico riferimento per quote Z e dettagli espositivi

### Evidenza

| Componente | Prospetto | Render | Sorgenti |
| --- | --- | --- | --- |
| Cartellini smart, H110 | Z900–1010 | Z790–900 | `generate.py:530–532`; `render.py:339–341` |
| Ripiani smart, sp25 | Z1050–1075 | Z1025–1050 | `generate.py:528–529`; `render.py:336–338` |
| LED su cassettiere H800 | Z304 e560 | Z288 e544, bande alte12 | `generate.py:459–460`; `render.py:379–380` |
| Sommità listelli | H−400 =3750 | H−450 =3700 | `generate.py:494`; `render.py:411`; `render.json:166` |

### Correzione richiesta

Per ogni oggetto definisci il riferimento della quota: base, piano superiore oppure asse. Registra una sola geometria derivata con estremi X/Y/Z e usa quella per prospetto e scena. Non scegliere automaticamente una delle quote attuali come dato verificato: la scelta preliminare deve essere esplicita e riportata nel registro delle assunzioni. I parametri che descrivono elementi reali, come quota superiore dei listelli e posizione LED, non devono avere due versioni indipendenti fra generatore e renderer.

**Accettazione:** i valori Z min/max e gli assi dei dettagli coincidono fra F01–F04, abaco e scena entro la tolleranza numerica dichiarata. Un test confronta la geometria effettivamente generata; non basta cercare una stringa Python. Quote senza fonte mantengono lo stato aperto.

## R02-H03 — L/P/H del prodotto separati da X/Y della posa

### Evidenza

`outputs/AB01_abaco_arredi.md:7–15` e `src/generate.py:668–671` chiamano «L×P×H» le dimensioni sui due assi del locale. Gli oggetti ruotati risultano C4=400×1500, scrivania=700×1600 e isola=390×1600, mentre i loro lati lunghi sono rispettivamente1500,1600,1600 mm.

### Correzione richiesta

Separa dimensioni del prodotto da rotazione e ingombro nel locale. In AB01 mostra almeno prodotto/variante, L/P/H di catalogo con fonti/stati, angolo o orientamento del mobile, ingombro X/Y e posizione. Non risolvere il problema ordinando meccanicamente i due lati dal maggiore al minore: il significato di larghezza e profondità deve provenire dall'orientamento del prodotto e del suo fronte.

**Accettazione:** C4, scrivania e isola mantengono il lato lungo corretto nella scheda prodotto e l'orientamento approvato in pianta. Una rotazione cambia l'ingombro X/Y ma non L/P/H del prodotto. Le altezze800/760 ecc. restano esplicitamente ipotizzate finché non sono confermate dalle schede scelte.

## R02-H04 — Prospetti derivati dalle pareti del modello

### Evidenza

`src/generate.py:406–415` contiene gli estremi delle quattro viste come numeri fissi: Y4750, X3390, Y2680, X7500, ecc. Coincidono oggi con il modello, ma un successivo rilievo che aggiorni il JSON può lasciare i prospetti sulla vecchia parete e far sparire elementi per il filtro `_on_wall`.

### Correzione richiesta

Definisci ciascun prospetto con ID di parete, faccia osservata e verso di lettura. Ricava estremi, sviluppo e posizione dalla geometria corrente; usa la stessa associazione per mobili, porte, rivestimenti, specchi e utenze. Gestisci esplicitamente eventuali viste composte da più tratti. Non cambiare i lati del negozio per correggere la proiezione.

Aggiorna anche il registro Q01: alcune dimensioni della saletta sono ripetute come costanti intorno a `generate.py:610`. Devono seguire gli stessi elementi geometrici, con la loro fonte e il loro stato.

**Accettazione:** in un fixture sintetico, spostare o allungare una parete aggiorna pianta, prospetto, quote, ubicazione dei dettagli e render in modo coerente. Il fixture non modifica le misure del negozio. Le etichette rimangono leggibili e l'orientamento del fronte corrisponde alla pianta.

## R02-H05 — Completare la composizione della parete cassa

### Evidenza visiva

Nella reference approvata v6 ci sono mensole e cubotti anche sopra/dietro la reception e una colonna con listelli e specchio sulla parete di fondo. In `R01_ingresso_verso_cassa.png` P01 la porzione sopra la cassa è quasi vuota, mentre le mensole sono associate solamente a C1. I due specchi/listelli introdotti sono presso il fronte saletta eC4.

### Correzione richiesta

Sviluppa F01 e il modello espositivo per includere anche la parte sopra la cassa, riprendendo l'effetto approvato: mensole bianche sfalsate, cubotti aperti in rovere, continuità del legno attorno allo specchio e luce sulle montature. Mantieni cassa bianca a contatto col muro sinistro, quattro cassettiere, palette e prodotti selezionati successivamente. Non copiare dalla prospettiva dimensioni o quantità non compatibili col locale; presenta come proposta qualsiasi adattamento compositivo necessario e riportane le quote da validare. Non spostare la cassa o ridurre passaggi per far posto alla composizione.

**Accettazione:** F01, abaco dei pezzi su misura e render mostrano gli stessi elementi anche nella zona sopra cassa. Consegna confronto annotato con la reference che distingua componenti ripristinati, adattamenti proposti e dettagli ancora mancanti. Nessun nuovo logo sopra le mensole; sul banco usa l'asset ufficiale senza ridisegnarlo.

## R02-H06 — Pannelli smart: lessico delle distanze, ingombro e grafica

### Evidenza

La composizione attuale usa4pannelli da 410 mm e spazi da 60 mm. **60 mm è la distanza libera fra i pannelli, non l'interasse. L'interasse è470 mm.** Il termine «interasse60» nel rapporto va corretto senza cambiare la geometria. Nel renderer ogni cornice si estende inoltre di 15 mm oltre il pannello per lato (`render.py:332`): definire se i410 mm descrivono l'immagine o il telaio esterno. I PNG P01 mostrano pannelli grigi con titoli e targhette bianche senza testo, privi delle immagini/prodotti della reference.

### Correzione richiesta

Usa nomi distinti per larghezza immagine, larghezza esterna telaio, distanza libera e interasse. Controlla lo sviluppo della composizione sull'ingombro completo, comprese cornici, ripiani e distanze dai bordi. Le quantità4×410+3×60=1820 descrivono oggi i pannelli; non attribuirle automaticamente ai telai completi se questi sono più larghi. Mantieni espliciti fonte/stato della fascia 1820 e della parete 2070.

Ripristina immagini, cartellini e appoggi prodotto della composizione approvata usando gli asset disponibili; se gli asset non sono disponibili, lascia segnaposto dichiarati e segnala cosa serve. Non sostituire il contenuto della reference con grafica arbitraria né rimpicciolire automaticamente gli elementi per farli entrare.

**Accettazione:** stesso sviluppo e stessi ingombri in F02, abaco e render; distanza60 e interasse470 correttamente etichettati quando i pannelli rimangono410. Test di ingombro esterno delle cornici. Render con composizione effettiva o segnaposto esplicitamente indicati, senza dichiarare conclusa la fedeltà grafica quando mancano immagini e cartellini.

## R02-H07 — Nodo di falegnameria mensole/cubotti e sviluppo D01

### Evidenza

Il cubottoC1 occupa X2827–3177,Y4490–4750,Z1575–1925; la mensola successiva X1840–3190,Y4500–4750,Z1850–1875. I solidi si sovrappongono nei fianchi e nel fondo del cubotto. La composizione può essere intenzionale a incastro: non è motivo per spostare automaticamente gli elementi.

### Correzione richiesta

Definisci il nodo costruttivo: mensola interrotta, fianchi sagomati, componenti condivisi o altra soluzione del falegname. Predisponi D01 con sezioni, codici dei componenti, modalità del raccordo, canalizzazione dei cavi e accesso ai driver. Quando mancano schede LED, carichi, supporti o fissaggi, emetti soltanto lo schema preliminare utile e un elenco preciso delle informazioni necessarie; non inventare una ferramenta o dichiarare esecutivo il dettaglio.

**Accettazione:** non restano solidi sovrapposti senza spiegazione costruttiva. Le parti rappresentate nei prospetti corrispondono alla distinta; i raccordi intenzionali sono documentati. Fissaggi/carichi/profili reali non disponibili restano `pending`. Il manifesto dichiara se D01 è schema preliminare, incompleto o ancora non emesso, indicando le cause concrete.

## R02-H08 — E01: consegnare l'intero registro delle utenze

### Stato attuale

Il modello contiene ora undici utenze e separa X/Y/Z, supporto, proprietario, accesso, alimentatore e percorso. È un miglioramento da preservare. E07–E09 senza posizione e le Z mancanti sono correttamente aperte. Tuttavia l'elenco stampato inE01 (`generate.py:384–396`) omette `quantity` e `route`; varie descrizioni restano «da definire». E05/E06 sotto arredo non hanno ancora il dettaglio fisico del collegamento.

### Correzione richiesta

Esporta un registro utenze completo e leggibile associato aE01, con gli stessi ID del JSON e almeno servizio/mobile, quantità e stato, X/Y/Z con fonte/stato, supporto, accesso manutenzione, driver, percorso previsto/stato e dati ancora necessari. Integra nei prospetti le quote effettivamente note; non scrivere sempre «Z da rilevare» se in una revisione futura un dato è stato verificato. PerE05/E06 descrivi le alternative di collegamento e il punto da decidere, senza disegnare una posa nascosta non autorizzata come definitiva.

**Accettazione:** ogni punto in pianta/prospetto è rintracciabile nel registro; nessun campo presente nel modello ma necessario al professionista va perso per troncamento o mancata esportazione. Dati mancanti restano `pending`. Non derivare potenze installate dalle luci di Blender; nessuna sezione, protezione, circuito o fissaggio inventato. E01 rimane preliminare finché allacci e quote non sono verificati.

## R02-G01 — Accostamento al muro specifico e al lato giusto del mobile

**Errore già riprodotto.** In `src/checks.py`, `proximity`, il controllo degli accostamenti a `ENVELOPE` usa la distanza dal bordo completo. La descrizione «fianco a contatto con il muro sinistro» è soltanto testo. In una copia del modello, spostando la cassa a `x=3000, y=0`, il risultato continua a essere `ADJ-CASSA-ENV = OK`, con la stessa descrizione del muro sinistro. La cassa reale della P01 è invece correttamente posizionata a sinistra: il bug riguarda il controllo, non prova che quella posa sia sbagliata.

**Intervento richiesto.** Identificare in modo strutturato il segmento/faccia del muro di destinazione e il lato del mobile da accostare. Verificare almeno distanza dal muro corretto, parallelismo, tratto effettivo di affaccio e assenza di invasione. Le tolleranze devono appartenere alla relazione dichiarata; una distanza piccola da un altro muro non soddisfa il vincolo. Applicare lo stesso principio a C1/fondo, C4/parete laterale e agli accostamenti verso tramezzi o ringhiera, senza cambiare il layout solo per far passare il test.

**Accettazione.** La posa corrente della cassa è riconosciuta come coerente con il vincolo geometrico; la sonda sul fronte non lo è. Il risultato nomina il muro e il lato realmente controllati. Un contatto con il muro giusto ma con lato/orientamento incompatibile non viene promosso automaticamente a `OK`. La relazione resta distinta dalla verifica del posto operatore e dalla qualità delle quote.

## R02-G02 — Propagazione dello stato nei controlli delle porte

**Errore già riprodotto.** In `src/checks.py`, `doors`, il risultato `SWING-P_SAL` diventa `SUPERATO` quando si cambia in `verified` il solo stato di P_SAL, lasciando gli ostacoli circostanti e le loro posizioni `assumed`. La scelta dell'esito usa lo stato della porta e non quello del contesto necessario alla verifica.

**Intervento richiesto.** Rendere esplicite le dipendenze del controllo: geometria e posa della porta, muro ospite, ostacoli pertinenti, ingombri d'uso e eventuali criteri di accesso. Propagare lo stato meno affidabile delle dipendenze realmente utilizzate. Un dato necessario mancante deve produrre un esito non verificabile; un controllo eseguito su ipotesi deve restare qualificato come tale. Un'interferenza rilevata nello scenario corrente resta visibile, anche se basata su ipotesi.

**Accettazione.** Porta verificata più ostacoli ipotizzati non dà `SUPERATO`. Solo un caso sintetico con tutti i dati e criteri necessari verificati può ottenere quello stato, limitatamente al controllo geometrico dichiarato. Il report conserva separati apertura dell'anta, accesso al vano, qualità dei dati e validazione professionale: il superamento di uno non certifica gli altri.

## R02-G03 — Coerenza fra porta, apertura e muro ospite

**Errore già riprodotto.** In una copia del modello, impostando P_ING con `x0=9000`, `x1=9900` e `hinge=[9000,0]`, `doors()` dichiara ancora `COMPATIBILE_IPOTESI`, «nessuna interferenza». Il varco è fuori dall'involucro largo 7500 mm. La sola assenza di collisioni non verifica che esista un'apertura nel muro corretto. Le porte della P01 non sono state rilevate fuori dal locale: questa è una prova di un caso non gestito dal controllo.

**Intervento richiesto.** Validare prima l'associazione al muro/facciata, il tratto occupato dal vano, le coordinate della cerniera, la coerenza fra coordinate e `opening_width`, e l'orientamento dell'anta. Distinguere vano nominale, telaio, luce utile e larghezza dell'anta: non imporre che siano identici. Verificare poi l'apertura rispetto ai lati ammessi e agli ostacoli. Per una porta esterna non imporre indiscriminatamente che tutta l'anta aperta resti nel poligono interno: il lato di apertura deve essere documentato e valutato nel contesto interno/esterno corretto.

**Accettazione.** La sonda fuori locale produce un errore di collocazione/ospite, non un esito compatibile. Una porta su muro diverso, una cerniera incoerente o una larghezza nominale incompatibile con il vano producono esiti distinti e spiegabili. I casi corretti di P_SAL e P_ING mantengono il verso modellato; i dati ancora mancanti restano dichiarati. Gli avvisi non scompaiono solo perché il controllo delle collisioni non ha trovato ostacoli.

## R02-G04 — Circolazione esplicita, separata dalla semplice non sovrapposizione

**Lacuna verificata.** FP05 scrivania–C4 misura 1450 mm. Con la fascia sedia assunta di 750 mm e la corsa cassetti assunta di 350 mm restano 350 mm. Le due fasce non si sovrappongono: l'esito corrente è corretto soltanto per quel controllo geometrico. Non verifica né certifica 350 mm come percorso o come accesso all'esposizione durante l'uso simultaneo. Inoltre `functional_pairs()` decide se applicare lo screening del passaggio cercando «percorso», «passaggio» o «accesso» nella descrizione libera: una modifica editoriale può cambiare l'esito.

**Intervento richiesto.** Separare in campi strutturati il tipo di controllo, lo scenario d'uso e il criterio applicabile. Mantenere descrizione e logica indipendenti. Per FP05 restituire almeno: distanza statica, ingombri attivati, assenza/presenza di collisione, spazio residuo e stato della valutazione del percorso/accesso all'esposizione. Valutare esplicitamente gli scenari pertinenti, ad esempio mobili chiusi, seduta occupata e cassetti aperti, senza sommare scenari che siano dichiarati alternativi. Se non è ancora stabilito quali usi debbano essere simultanei o quale criterio adottare, la relativa valutazione resta non verificabile.

**Accettazione.** Il valore residuo di 350 mm compare nel report corrente con le sue ipotesi. «Nessuna sovrapposizione» non diventa un giudizio complessivo di fruibilità. Se si applica lo screening di progetto di 900 mm già presente, il confronto è dichiarato come tale; non viene presentato come requisito normativo verificato. Cambiare le parole della descrizione senza cambiare i campi funzionali non modifica l'esito. Una soglia o uno scenario mancante produce un risultato aperto, non un'approvazione implicita.

## R02-G05 — Spazio netto fra scala e cassa: 100–120 cm

**Fonte:** ultima indicazione della committenza: «tra la scala e la cassa dovrebbe esserci un metro barra un metro e venti». Questa richiesta integra e prevale sul precedente trattamento del distacco cassa–scala come semplice valore aperto di 250 mm.

### Criterio da inserire nel modello

- Registrare un requisito di progetto: **luce netta richiesta nell'ordine di 1000–1200 mm**, minimo richiesto **1000 mm**; 1200 mm è l'estremo superiore dell'obiettivo indicativo, non un divieto di lasciare più spazio.
- Conservare il fianco della cassa sul muro sinistro. Valutare la sua posizione lungo quel muro rispetto al nuovo requisito, senza congelare la coordinata attuale y=4150.
- Quotare in A01 il passaggio effettivo fra il limite fisico più sporgente di scala/parapetto/corrimano e il bordo esterno della cassa, compreso il top. Identificare i due riferimenti di misura; non misurare dall'asse della ringhiera.
- Separare questa luce a banco chiuso dagli ingombri di cassetti/ante, dal posto operatore e dalle altre verifiche durante l'uso. Il nuovo requisito non determina da solo l'ergonomia della postazione.
- Conservare fonte e qualità delle geometrie. Un requisito della committenza è un dato di progetto; non rende verificate le coordinate del locale.

### Riscontro nel modello P01

| Grandezza | Valore del modello |
| --- | ---: |
| Scala lungo Y | 1500–3900 mm |
| Cassa lungo Y, profondità 600 mm | 4150–4750 mm |
| Parete di fondo | Y = 4750 mm |
| Distacco schematico attuale | 4150 − 3900 = **250 mm** |
| Fascia totale fra fine scala e fondo | 4750 − 3900 = **850 mm** |
| Fascia necessaria con quel banco e 1000–1200 mm liberi | **1600–1800 mm** |
| Differenza rispetto alla fascia attuale | **750–950 mm** |

Con queste coordinate e quel banco, la configurazione sul fondo non può soddisfare la nuova richiesta: non basta spostare di poco il mobile o cambiare la quota scritta. È un'incompatibilità delle ipotesi della P01, non la prova che lo spazio reale del negozio sia insufficiente.

### Correzione richiesta e accettazione

1. Inserire il requisito in forma strutturata e aggiornare `docs/decisioni.md`, Q01, pianta e controllo del distacco scala–cassa. Mantenere distinto il dato “richiesto” dal dato “rilevato/calcolato”.
2. Verificare sulle fonti disponibili la fine effettiva della scala, il fondo del locale, le sporgenze del parapetto e le dimensioni della variante di cassa. Non spostare o accorciare una scala reale e non dilatare il perimetro per ottenere il numero.
3. Adeguare il layout al vincolo lungo il muro sinistro quando i dati lo consentono, riportando le modifiche prima/dopo. Se le coordinate della P01 sono confermate e il vincolo non è soddisfacibile con il prodotto scelto, preparare alternative quotate e indicare la scelta necessaria. Non dichiarare già ottenuto il passaggio.
4. Nel fixture P01, i 250 mm devono risultare **insufficienti rispetto al nuovo minimo richiesto**, con stato delle misure ipotizzato. L'assenza dei dati del posto operatore non deve nascondere questo confronto; gli altri controlli incompleti restano aperti separatamente.
5. Nella soluzione proposta, mostrare una quota netta esplicita fra gli ingombri completi. Verificare almeno 1000 mm e indicare il valore ottenuto rispetto all'obiettivo 1000–1200 mm; se gli ingombri reali non sono noti, riportare lo stato non verificabile anziché un “OK” definitivo.
6. Conservare cassa a sinistra, quattro cassettiere e gli altri vincoli approvati. L'eventuale variazione della posizione longitudinale della cassa per rispettare questo nuovo spazio fa parte della richiesta; eventuali altre modifiche al concept devono essere presentate come proposte.

## Decisioni di layout e dati da acquisire

I seguenti punti non si chiudono cambiando un messaggio del software. Conservare i conflitti e predisporre alternative quotate o domande puntuali sui dati mancanti. Nessuno spostamento deve essere introdotto come se fosse già approvato.

| Punto | Riscontro nella P01 | Azione richiesta | Condizione di chiusura |
| --- | --- | --- | --- |
| C3–scrivania | 580 mm statici; 230 mm residui con cassetto da 350 mm assunto. | Verificare corsa reale e percorso richiesto; preparare eventuali varianti quotate compatibili con scrivania nell'angolo e accesso all'esposizione. | Confronto degli scenari e scelta documentata; il conflitto resta fino a risoluzione dimostrata. |
| C4–accesso saletta | C4 entra per 220 × 20 mm nella fascia di accesso ipotizzata di 900 mm. | Confermare posizione del vano/spallette e criterio di accesso; illustrare alternative senza fissare automaticamente uno spostamento di 20 mm. | Apertura, ingombri d'uso e accesso coerenti nella pianta, nel prospetto e nel report. |
| Cassa | 250 mm dalla scala nella P01, inferiori ai nuovi 1000–1200 mm richiesti; 640 mm da C1; banco 1200 × 600 mm ancora segnaposto. | Applicare G05: verificare scala, fondo, sporgenze e prodotto; adeguare o proporre la posa lungo il muro sinistro e definire lato operatore/accesso. | Luce netta almeno 1000 mm nella soluzione valutata, confrontata con l’obiettivo 1000–1200 mm; fonti, stato e funzionamento documentati. |
| Isola–ringhiera | 50 mm dall'asse; spessore/sporgenze del corrimano mancanti. | Distinguere asse e ingombro fisico; completare inoltre la verifica delle ante Monfero, oggi pending e non richiesta da una coppia funzionale. | Luce netta e apertura ante valutate su dati documentati o espliciti scenari, con limiti residui visibili. |
| Scrivania–vetrina | 100 mm dalla linea della facciata. | Verificare serramento reale, sporgenze, pulizia e utilizzo del bordo. | Criterio e geometria pertinenti registrati; nessun esito positivo generato dalla sola distanza. |

Lo spostamento di 50 mm della scala nella P01 va descritto nel registro delle differenze: dalla semplice trasformazione della P00 si otterrebbe `y=1450..3850`, mentre il modello usa `1500..3900` con fonte S1 per posizione. Da qui la variazione cassa–scala da 300 a 250 mm. Non annullarlo automaticamente; verificare e documentare la scelta della fonte. La frase «mobili non spostati» non spiega da sola questa variazione di un elemento fisso.

## R02-H09 — Verifica e consegna coordinata

Riesegui i controlli necessari, genera tutti gli elaborati interessati e verifica anche gli output visuali. Mantieni i risultati già conseguiti: quattro viste aggiornate, orientamento corretto e stati delle quote. Una nuova revisione non è un motivo per cambiare nomi dei file senza aggiornare manifesto e rimandi.

### Criteri comuni di accettazione

- Un solo modello per dimensioni, sporgenze, fronti, collocazione, quote Z e geometria dei componenti; impostazioni artistiche tenute distinguibili dai dati tecnici.
- Test di coerenza tra impronte/solidi, prospetti, abaco e utenze, inclusi arredi ruotati e modifiche sintetiche delle pareti. I test che cercano stringhe nel sorgente non sostituiscono questi confronti.
- Manifesto con file realmente prodotti, revisione, comandi eseguiti e dati aperti; report punto per punto con prima/dopo, prova e residuo.
- Quattro render della revisione corrente, compresa una vista di controllo dall'alto leggibile: usare una sezione o nascondere gli elementi alti che coprono i varchi; non eliminare dal modello porte o architravi per migliorare l'immagine.
- Nessuna quota `assumed` o `pending` promossa a `verified` senza fonte; nessuna misura ricavata dal render estetico.
- Documentare ogni modifica a cassa, scrivania, isola o cassettiere. Per la cassa, G05 richiede di valutare la posa lungo il muro sinistro per ottenere 1000–1200 mm netti dalla scala; non mantenere una posizione incompatibile soltanto perché era nel modello precedente. Gli altri vincoli restano validi e i conflitti non risolti rimangono espliciti.
- Stato `PRELIMINARE - NON PER CANTIERE` preservato. Distinguere sempre «corretto nel codice», «compatibile nelle ipotesi» e «verificato con fonte».


## 4. Sequenza operativa e gestione Git

1. Leggi `docs/opus_prompt_R02.md` e questo documento. Controlla lo stato del branch, le modifiche locali e l'eventuale avanzamento successivo alla baseline. Non fare reset, checkout forzati o ripristini della P00.
2. Come previsto dal progetto, esegui e registra `pytest -q` e `python -m src.generate` sulla base di partenza. Non affermare che un comando è riuscito se non lo hai eseguito.
3. Correggi H01–H04 e G01–G05 con geometrie condivise, il nuovo requisito scala–cassa e regressioni mirate. Il file `R02_regressioni.json` è una specifica di casi da implementare, non un test già eseguito.
4. Completa H05–H08 e le proposte per i conflitti di layout. Per le quote non disponibili mantieni stato e fonte; produci comunque gli schemi preliminari utili.
5. Usa la prossima revisione libera del progetto per gli elaborati modificati; “R02” qui identifica l'incarico di review, non impone il codice della revisione del modello.
6. Rigenera tutte le tavole e i quattro render interessati. Se un ambiente non consente un'uscita, dichiara esattamente quale manca e non presentare il set come completo.
7. Controlla gli output pubblicabili, non soltanto i file sorgenti. Aggiorna manifesto, registri e rapporto con i risultati reali.
8. Prosegui sul branch della PR attiva o su un branch derivato dal suo HEAD aggiornato. Evita push diretti su `main`, force push e merge automatici; conserva le regole già presenti nel progetto.

## 5. Rapporto di chiusura richiesto

Scrivi `outputs/revisione_correzioni_R02.md` con una riga per **R02-H01…H09 e R02-G01…G05**:

| Campo | Contenuto richiesto |
| --- | --- |
| Stato | Già corretto / corretto ora / parziale / decisione aperta / dato mancante |
| Evidenza iniziale | File e comportamento o elaborato interessato |
| Intervento | File effettivamente modificati |
| Prima e dopo | Quote, geometrie o esiti confrontabili |
| Verifica | Test o controllo visivo realmente eseguito, con risultato |
| Residuo | Decisione, fonte o misura ancora necessaria |

Per le alternative di arredo mostra coordinate variate, motivo, distanze prima/dopo e impatto sugli altri vincoli. Non sostituire la soluzione corrente con una proposta non approvata.

Allega inoltre:

- elenco esatto di PDF/DXF/PNG/registri generati e loro revisione;
- risultati dei test, distinguendo passati, falliti e saltati;
- confronto di F01 e del render cassa con la reference, per rendere verificabile H05;
- elenco delle misure che il geometra deve rilevare e delle schede prodotto necessarie a elettricista e falegname;
- distinzione esplicita fra correzione del software, compatibilità nelle ipotesi e verifica con fonte.

Non chiudere un errore perché è cambiato soltanto il testo del report. Non usare un test “verde” come certificazione dell'arredo o dell'impianto.

## 6. Verifica già disponibile sulla baseline

L'ultima CI della baseline, [run 44921697307](https://github.com/sherinataalla-cell/limpidia-cad-opus/actions/runs/44921697307), riporta 19 test superati e generazione 2D riuscita. La verifica indipendente ha riprodotto la generazione delle sei tavole; localmente sono passati 18 test con uno escluso per indisponibilità dell'immagine approvata nel trasferimento, mentre il test completo è passato in CI.

I quattro PNG P01 sono stati aperti e confrontati con la reference. Le tre sonde G01–G03 e le divergenze geometriche H01/H02 sono state riprodotte nella review. **I nuovi casi del JSON R02 non sono stati ancora implementati né eseguiti.** La loro presenza nella patch non risolve gli errori.

Snapshot sorgenti e output: [commit 129e25f](https://github.com/sherinataalla-cell/limpidia-cad-opus/tree/129e25f5e45297869ed50ed01be6f99819933c50). Prima di applicare una correzione a un HEAD più recente controlla che l'anomalia persista.
