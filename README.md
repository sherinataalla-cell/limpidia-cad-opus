# Limpidia — CAD tecnico per Claude Opus

Repository di avvio per trasformare il concept approvato del negozio di via Andrea Solari 3 (Milano) in tavole **DXF editabili** e successivi PDF quotati per geometra, elettricista e falegname.

> **STATO: PRELIMINARE / NON ESECUTIVO.** Le quote dell'involucro e alcune posizioni sono ipotesi. Nessun disegno generato da questo repository autorizza taglio, perforazioni o lavori prima del rilievo, della verifica dei fornitori e della validazione dei tecnici incaricati.

## Avvio rapido

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.generate
pytest -q
```

I file generati sono in `outputs/`: una pianta architettonica preliminare e una tavola di coordinamento elettrico, entrambe DXF. Aprirle con LibreCAD, QCAD o AutoCAD. I file sorgente in `config/` sono l'unica fonte di coordinate e dimensioni.

## Claude Opus / Claude Code

Aprire questa cartella con Claude Code e chiedere:

> Leggi CLAUDE.md e .claude/skills/limpidia-cad/SKILL.md. Verifica il modello preliminare, genera e controlla le tavole DXF senza modificare decisioni approvate. Produci un registro di quote mancanti e collisioni; poi prepara una revisione R01 per il geometra, l'elettricista e il falegname. Non definire esecutiva alcuna tavola non validata.

## Sequenza di lavoro

1. Importare pianta autorizzata e rilievo metrico; distinguere geometria misurata, ipotizzata e approvata.
2. Definire assi, origini e perimetro, porta saletta, scala, ringhiera, serramenti, impianti esistenti.
3. Bloccare posizione dei quattro mobili contenitori, banco cassa, scrivania e isola smart.
4. Verificare spazi di servizio, cassetti aperti, sedute occupate e accesso saletta.
5. Generare pianta arredi, pianta elettrica, prospetti e sezioni con codici coordinati.
6. Acquisire schede tecniche, quote e carichi dei mobili reali; completare i dettagli su misura.
7. Rieseguire test, esportare DXF/PDF e richiedere validazione ai professionisti.

## Stato delle fonti

La vista approvata prevista in `assets/approved/` è il riferimento **estetico**, non una fonte metrica. Le coordinate di `config/geometry.json` sono ipotesi di lavoro. Vedi `docs/decisioni.md` e `docs/rilievo.md`.

**Immagine approvata:** se il file `assets/approved/viste_approvate.png` non è ancora presente, caricarlo prima di richiedere prospetti visivi; NON inventare nuove immagini. Le planimetrie DXF sono rigenerabili con `python -m src.generate`.
