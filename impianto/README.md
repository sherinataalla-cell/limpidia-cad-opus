# Impianto elettrico

Lo schema elettrico del negozio: com'è oggi, cosa si rifà e cosa si predispone per dopo. Serve per la consegna all'elettricista e, finiti i lavori, come mappa per i piccoli interventi futuri (telecamere, casse, monitor) senza ricostruire tutto.

> **PRELIMINARE - NON PER CANTIERE.** Taglie, sezioni, tipi delle protezioni, quote e percorsi li decide il progetto dell'impresa. Qui si registrano solo scelte e dati verificabili.

## File

| File | Cosa contiene |
| --- | --- |
| `impianto.json` | Fonte unica: fornitura, quadri, circuiti, utenze, predisposizioni future, stato di fatto con le foto |
| `SCHEMA.md` | Vista leggibile generata da `impianto.json`: albero dei quadri, circuiti con le loro utenze, stato di fatto. Non si modifica a mano |
| `schema.py` | Il generatore di `SCHEMA.md` |
| `foto/F01–F17.jpg` | Foto dello stato di fatto del 26/11/2026, ridotte e senza dati di posizione |

## Legame con il modello del negozio

Le posizioni dei punti non si scrivono qui: stanno in `config/geometry.json` (`electrical_points`, E01–E09). Ogni utenza che corrisponde a un punto del modello lo cita in `rif_modello`. Il test `tests/test_impianto.py` controlla che:

- ogni circuito stia su un quadro esistente e ogni utenza su un circuito esistente;
- ogni `rif_modello` esista nel modello;
- **ogni punto del modello abbia un'utenza nello schema elettrico**: se il CAD aggiunge un punto, il test lo segnala finché qui non si dice su quale circuito va;
- le foto citate ci siano e `SCHEMA.md` sia aggiornato.

## Stati

`esistente` (c'è e si tiene) · `rilevato` (letto dalle foto, da misurare) · `progetto` (nel rifacimento) · `futuro` (si predispone ora, si installa dopo) · `da_decidere` (dipende da una decisione aperta).

## Aggiungere qualcosa

1. Branch dedicato, come per il resto del repo.
2. Aggiungi o modifica la voce in `impianto.json`. Per un'installazione futura: `"stato": "futuro"`, `"tipo": "predisposizione"`, e nei punti cosa va predisposto (tubo vuoto, scatola, presa, dati).
3. `python -m impianto.schema` e `pytest -q`.
4. Pull request.

## Fuori dal repo

La consegna all'elettricista (scopo, divisione dei lavori, decisioni aperte, stima) è un documento condiviso a parte: questo repo ne tiene i dati.
