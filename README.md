# Limpidia — CAD tecnico per Claude Opus

Repository di avvio per trasformare il concept approvato del negozio di via Andrea Solari 3 (Milano) in tavole **DXF editabili** e successivi PDF quotati per geometra, elettricista e falegname.

> **STATO: PRELIMINARE / NON ESECUTIVO.** Le quote dell'involucro e alcune posizioni sono ipotesi. Nessun disegno generato da questo repository autorizza taglio, perforazioni o lavori prima del rilievo, della verifica dei fornitori e della validazione dei tecnici incaricati.

## Regola di lavoro: sempre branch e pull request

**Nessun push diretto su `main`.** Ogni modifica (modello, codice, tavole, documenti) si fa su un branch dedicato e arriva su `main` solo tramite pull request, approvata e unita da Sherin (`@sherinataalla-cell`). Vale per le persone, per Claude e per i workflow automatici.

1. Crea un branch dal `main` aggiornato (es. `rilievo-saletta`, `render-r02`).
2. Modifica, poi esegui `pytest -q` e `python -m src.generate` e committa anche gli elaborati rigenerati.
3. Apri la pull request descrivendo cosa cambia nelle misure e nelle tavole.
4. La CI rigenera le tavole sulla PR e le allega come artifact: controlla che coincidano con quelle committate.
5. Solo dopo la revisione si fa il merge.

Così modello, tavole e render restano sempre allineati e ogni cambio di misura è tracciato.

Per farlo rispettare anche da GitHub, la regola va attivata una volta nelle impostazioni del repository: *Settings → Rules → Rulesets → New branch ruleset* su `main`, con "Restrict deletions", "Block force pushes" e "Require a pull request before merging" (almeno 1 approvazione).

## Avvio rapido

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.generate        # tavole DXF + PDF, registro quote, criticità
pytest -q
pip install bpy pillow        # solo per i render (Blender come modulo Python)
python -m src.render          # anteprime 3D in outputs/render/ (--fast per una bozza)
```

I file generati sono in `outputs/`:

| File | Contenuto |
| --- | --- |
| `A01_pianta_arredi_preliminare.dxf/.pdf` | Pianta arredi quotata, distanze libere, legenda, cartiglio A3 1:50 |
| `E01_punti_utenza_preliminari.dxf/.pdf` | Punti utenza energia/dati e LED con elenco, Z da rilevare |
| `criticita.md` | Controlli geometrici: passaggi stretti, porta saletta, banco cassa, superficie |
| `quote_da_rilevare.md` | Registro quote aperte |
| `render/R01_*.png` | Anteprime 3D dal modello (non fonti metriche) |

I DXF si aprono con LibreCAD, QCAD o AutoCAD; nello spazio modello sono 1:1 in mm, il layout `A01`/`E01` è la tavola stampabile. I file sorgente in `config/` sono l'unica fonte di coordinate e dimensioni (`geometry.json`); `render.json` contiene solo altezze e finiture per l'anteprima 3D, non quote di progetto.

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
