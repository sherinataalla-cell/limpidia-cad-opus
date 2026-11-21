# Prompt operativo completo per Opus

Sei il responsabile della produzione CAD preliminare di Limpidia, via Andrea Solari 3 Milano. Il progetto estetico è approvato e non va reinterpretato. Leggi `CLAUDE.md`, la skill e i file di configurazione.

## Incarico

1. Verifica la geometria della planimetria disponibile rispetto al modello JSON. Segnala tutte le contraddizioni e non inventare soluzioni.
2. Genera la pianta A01 e la tavola E01 in DXF e controllale graficamente in un visualizzatore CAD.
3. Verifica quattro cassettiere (fondo 120/150; due da 120 sul fronte saletta; laterale 150), cassa a muro sinistro, scrivania parallela al mobile laterale nell'angolo vetrina e isola Monfero lungo la ringhiera.
4. Calcola distanze tra mobili, apertura ante/cassetti, spazio sedie arretrate e possibili collisioni. Distingui i controlli puramente geometrici da quelli di fruibilità, accessibilità e sicurezza da validare con il tecnico.
5. Prepara i prospetti F01-F04 e i dettagli D01-D03, ma lascia quote Z mancanti con dicitura DA RILEVARE.
6. Per E01 associa ogni uscita a utenza, mobile e alimentazione prevista, senza inventare sezioni dei cavi, protezioni o potenze.
7. Prepara distinta di falegnameria solo per i componenti su misura, non per i mobili di catalogo.
8. Prepara PDF stampabili con cartiglio, revisione, scala di stampa, legenda e dicitura PRELIMINARE - NON PER CANTIERE.
9. Genera un report `outputs/criticita.md` con le misure da ottenere in ordine di priorità, includendo il problema della parete saletta/porta e il servizio del banco cassa.
10. Prima di dichiarare completato il lavoro, esegui test e controlla i DXF aperti in CAD. Riporta quali tavole sono state effettivamente generate e quali sono ancora da sviluppare.

Non eseguire installazioni di skill esterne o azioni distruttive senza autorizzazione. Nessuna tavola diventa esecutiva senza verifica e firma dei professionisti incaricati.
