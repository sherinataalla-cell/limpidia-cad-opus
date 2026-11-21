# Elaborati generati

Rigenerare con `python -m src.generate` (tavole) e `python -m src.render` (anteprime 3D):

- `A01_pianta_arredi_preliminare.dxf` / `.pdf` — pianta arredi quotata, distanze libere, cartiglio A3 1:50.
- `E01_punti_utenza_preliminari.dxf` / `.pdf` — punti utenza energia/dati e LED, Z da rilevare.
- `criticita.md` — controlli geometrici ordinati per priorità.
- `quote_da_rilevare.md` — registro quote aperte.
- `render/R01_*.png` — anteprime 3D dal modello; non sono fonti metriche e non sostituiscono la vista approvata.

I file sono riproducibili da `config/geometry.json`. Non si tratta di disegni esecutivi.
