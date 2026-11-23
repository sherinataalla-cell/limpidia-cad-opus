# Decisioni approvate e punti aperti

## Approvati

- Pareti esposizione: beige sabbia, lieve effetto minerale opaco.
- Pavimento: effetto rovere sbiancato chiaro.
- Parete smart: mattoni marrone scuro, stessa finitura visibile dal lato consulenza.
- Mensole: bianche, sfalsate, cubi rovere naturale, luce mirata sulle montature.
- Cassettiere: **quattro**, finitura noce scuro, due linee LED; una sul fondo di fronte alla vetrina, due sul fronte saletta, una sulla parete laterale parallela alla scrivania.
- Scrivania: legno noce, nell'angolo verso la vetrina, parallela all'esposizione laterale, senza bloccare accesso e prova montature.
- Cassa: bianca, fianco a contatto con muro sinistro. Marchio Limpidia ufficiale sul frontale; nessun logo sopra le mensole.
- Isola smart: Monfero cachemire, lato lungo parallelo e accostato alla ringhiera; profondità entro 40 cm; ante verso la vendita.
- Zona smart: quattro pannelli dimostrativi e luce prodotto; mantenere grafica e cartellini.

## Requisiti della committenza (R02, 21/11/2026)

- Luce netta fra scala e cassa: **100–120 cm, minimo 100 cm**, misurata fra il limite fisico più sporgente di scala/parapetto/corrimano e l'ingombro completo della cassa (top compreso). Requisito di progetto, non misura rilevata né soglia normativa. Nel modello: `requirements.REQ_SCALA_CASSA`.
- Con la cassa sul muro sinistro e la scala fino a y 3900 (ipotesi P02) la luce è 250 mm: il requisito **non è soddisfatto**. Non si sposta né si accorcia la scala; le alternative quotate sono in `outputs/proposte_layout.md` (V1 = deroga al vincolo «cassa sul muro sinistro», da approvare).

## Indicazioni dell'utente del 23/11/2026 (P04)

Queste indicazioni correggono l'interpretazione della scala e aprono una nuova proposta. Non sostituiscono la configurazione P03, che resta la base di confronto.

- **Scala:** accesso e discesa dal lato vetrina. Sul lato verso C1 c'è una protezione (ringhiera), non un accesso. Nel modello: `SCALE.access_side = -y` e linea `RINGHIERA_TESTATA` sul bordo del foro a y 3900, **ipotesi topologica** con fonte utente: tracciato, estremità, spessore e sporgenze da rilevare. Il vecchio controllo «percorso C1–scala» (FP08-PERCORSO) è stato tolto; restano la vicinanza dei cassetti alle protezioni (PROT-) e l'accesso dal lato vetrina (ACC-SCALE).
- **Requisito scala–cassa 1000–1200 mm:** non revocato. Resta obiettivo di progetto, da verificare sulle protezioni reali e sull'uso del luogo.
- **Proposta V5 (da approvare):** cassa sulla parte destra della parete di fondo, vicino alla parete Smart; C1 e la sua esposizione sulla parte sinistra; scrivania 1600 × 700 con il lato lungo parallelo a VET_2. Il vincolo «cassa al muro sinistro» descrive la configurazione P03 e non impedisce di studiare V5, ma V5 non è una scelta definitiva.

- **Proposta V5b (23/11/2026, da approvare):** come V5, con la scrivania a x 3950–5550, y 600–1300 (più vicina alla vetrina e verso la ringhiera; alternativa y 550). Cassetti normalmente chiusi e aperti brevemente; nessun passaggio simultaneo richiesto nella fascia dei cassetti aperti. Sedute rappresentate con la sedia reale per ruolo e lato (dato mancante): la fascia fissa da 750 mm è storica, non una prescrizione. Operatore lato vetrina e cliente lato interno sono ipotesi della prova.

## Preferenze dimensionali da verificare

- Cassettiere sul fronte saletta: due da 120 cm sono ipotesi preferita, NON ordine confermato.
- Fondo: 120 o 150 cm da decidere in base a cassa e accesso operatore.
- Laterale: 150 cm proposti, subordinati a passaggio e sedia operatore.
- Cassa Amazon: modello e quote della variante da verificare; placeholder 1200 × 600 mm NON confermato.
- Scrivania Homary: 1600 × 700 mm come riferimento di catalogo da ricontrollare.
- Isola Monfero: 1600 × 390 × 830 mm da confermare su scheda e variante finale.

## Attenzione

I render cambiano a volte prospettiva e proporzioni; non usarli per risolvere collisioni. Le vecchie piante R01–R03 erano ipotesi e non sono documentazione esecutiva.
