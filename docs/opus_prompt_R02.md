# Incarico per Claude Opus — correzioni R02 Limpidia

Applica le correzioni richieste in `docs/reviews/R02_errori_e_correzioni_opus.md` e implementa i casi pertinenti descritti in `docs/reviews/R02_regressioni.json`.

La baseline verificata è `129e25f5e45297869ed50ed01be6f99819933c50` della PR #1, branch `claude/project-thread-uc9o0p`. Prima di intervenire confronta il tuo HEAD e conserva il lavoro successivo. Questa versione sostituisce la precedente R02; se i file sono già stati importati, integra le differenze senza sovrascrivere il lavoro successivo. La patch aggiunge l'incarico e i criteri di accettazione; le correzioni ai sorgenti e agli elaborati devono essere svolte da te.

Parti da ingombri esterni coerenti di isola/cassa e quote comuni 2D/3D. Correggi poi abaco, dipendenze dei prospetti e controlli di muri/porte/percorsi. Ripristina l'esposizione approvata sulla parete cassa, completa il coordinamento della parete smart, il raccordo mensola/cubotto e il registro utenze.

Nuovo vincolo della committenza: fra scala e cassa servono **100–120 cm netti**, con minimo di progetto 100 cm. Mantieni la cassa sul muro sinistro e verifica il passaggio fra ingombri completi, compresi top e corrimano. Nel modello attuale i 25 cm non soddisfano la richiesta: riconcilia le quote della scala e del locale e adegua o proponi una posa quotata; non accorciare la scala per far tornare la misura. Vedi R02-G05.

Conserva orientamento, saletta a L, cassa sul muro sinistro, quattro cassettiere, scrivania in zona d'angolo con accesso all'esposizione e isola parallela alla ringhiera entro 400 mm di profondità esterna. Non ricavare quote dalla prospettiva dei render e non sostituire misure mancanti con dati inventati.

I quattro render P01 e la descrizione della PR sono già aggiornati: non segnalarli come ancora mancanti o obsoleti. Correggi soltanto ciò che persiste; nel lessico smart 60 mm è lo spazio fra pannelli, non l'interasse.

Completa autonomamente le correzioni verificabili. Per i conflitti di disposizione ancora aperti prepara alternative quotate; mantieni riconoscibile la configurazione corrente e le decisioni necessarie. L'assenza di alcune misure non blocca la correzione dei bug indipendenti.

Esegui i test, rigenera le sei tavole e le quattro viste della revisione corrente, controlla i file effettivamente prodotti e aggiorna il manifesto. Restituisci `outputs/revisione_correzioni_R02.md` con intervento, prova, prima/dopo e residuo per tutti i quattordici ID H01–H09 e G01–G05.

Segui il flusso branch/PR previsto dal progetto; nessun merge automatico. Non limitarti a modificare la documentazione della review.
