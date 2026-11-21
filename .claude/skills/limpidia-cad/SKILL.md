---
name: limpidia-cad
description: Progetta e verifica tavole CAD coordinate per il negozio Limpidia a partire dal modello parametrico; non rilascia disegni esecutivi senza rilievo e validazione.
---

# Workflow

1. Leggi `CLAUDE.md`, `docs/decisioni.md`, `docs/rilievo.md`, `config/geometry.json`.
2. Controlla unità mm, origini, assi, status di ogni quota e conflitti tra le fonti.
3. Esegui `python -m src.generate` e `pytest -q`.
4. Prepara lista interferenze: passaggi, sedie estratte, cassetti aperti, porta saletta, ringhiera, operatore cassa.
5. Produci revisioni coordinate di A01/E01 e successivamente prospetti F01–F04, sezioni D01, abaco AB01.
6. Per ogni elemento elettrico: codice, utenza, posizione X/Y, Z da verificare, accessibilità, alimentatore, potenza da scheda prodotto.
7. Emetti report differenze rispetto alla revisione precedente; non sovrascrivere file validati senza autorizzazione.
8. Chiedi conferma prima di cambiare posizione di cassa, isola, scrivania, numero di cassettiere, palette o finiture.

## Strumenti

- `ezdxf` per DXF; LibreCAD/QCAD/AutoCAD per ispezione.
- FreeCAD come possibile fase successiva per modelli e distinte di falegnameria.
- Skill open source esterne solo dopo verifica di codice, licenza, compatibilità e manutenzione. Non eseguire automaticamente repository terzi.

## Blocco sicurezza

I render non forniscono quote affidabili. Le misure e i carichi elettrici devono provenire da rilievo, schede tecniche e verifica professionale. Contrassegnare ogni output preliminare.
