"""Genera impianto/SCHEMA.md da impianto/impianto.json.

uso:  python -m impianto.schema           (riscrive SCHEMA.md)
      python -m impianto.schema --check   (esce con 1 se SCHEMA.md non è aggiornato)

L'uscita dipende solo dai due file di dati: stessa revisione, stesso testo.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'impianto' / 'impianto.json'
GEOMETRY = ROOT / 'config' / 'geometry.json'
OUT = ROOT / 'impianto' / 'SCHEMA.md'

STATO = {'esistente': 'esistente', 'rilevato': 'rilevato', 'progetto': 'progetto',
         'futuro': 'futuro', 'da_decidere': 'da decidere'}


def load():
    return json.loads(DATA.read_text(encoding='utf-8'))


def _cell(s):
    return str(s if s is not None else '—').replace('|', '\\|').replace('\n', ' ')


def _nid(s):
    return s.replace('-', '_')


def render(d, geometry=None):
    geo = {p['id']: p for p in (geometry or {}).get('electrical_points', [])}
    circ = {c['id']: c for c in d['circuiti']}
    by_circ = {}
    for u in d['utenze']:
        by_circ.setdefault(u['circuito'], []).append(u)

    out = ['# Schema elettrico — Limpidia', '',
           f"Revisione {d['revisione']} del {d['data']}. File generato da `impianto/impianto.json` con "
           "`python -m impianto.schema`: non si modifica a mano. PRELIMINARE - NON PER CANTIERE: taglie, sezioni e "
           "tipi delle protezioni li decide il progetto dell'impresa.", '']

    f = d['fornitura']
    out += ['## Fornitura', '',
            f"- Contatore: {f['contatore']} ({STATO[f['stato']]}).",
            f"- Posizione: {f['posizione']}.",
            f"- Potenza del contratto: {str(f['potenza_contratto_kw']) + ' kW' if f['potenza_contratto_kw'] else 'da leggere in bolletta'}.",
            f"- A valle del contatore: {f['protezione_a_valle']}.", '']

    out += ['## Albero dei quadri', '', '```mermaid', 'flowchart LR', '  CONT["Contatore"]']
    for q in d['quadri']:
        out.append(f"  {_nid(q['id'])}[\"{q['id']} · {q['nome']}\"]")
    for q in d['quadri']:
        if q['alimentato_da'].startswith('contatore'):
            out.append(f"  CONT --> {_nid(q['id'])}")
    for c in d['circuiti']:
        out.append(f"  {_nid(c['id'])}[\"{c['id']} · {c['nome']}\"]")
        out.append(f"  {_nid(c['quadro'])} --> {_nid(c['id'])}")
        if c.get('alimenta'):
            out.append(f"  {_nid(c['id'])} --> {_nid(c['alimenta'])}")
    out += ['```', '']

    out += ['## Quadri', '', '| Quadro | Piano | Posizione | Alimentato da | Dotazioni | Stato |', '| --- | --- | --- | --- | --- | --- |']
    for q in d['quadri']:
        out.append(f"| {q['id']} {_cell(q['nome'])} | {q['piano']} | {_cell(q['posizione'])} | {_cell(q['alimentato_da'])} | "
                   f"{_cell('; '.join(q['dotazioni']) or '—')} | {STATO[q['stato']]} |")
    out.append('')

    out += ['## Circuiti e utenze', '']
    for c in d['circuiti']:
        out += [f"### {c['id']} — {c['nome']}", '',
                f"Quadro {c['quadro']}, {c['gruppo'].lower()}, stato: {STATO[c['stato']]}."
                + (f" Alimenta {c['alimenta']}." if c.get('alimenta') else '')
                + (f" {c['note']}." if c.get('note') else ''), '']
        rows = by_circ.get(c['id'], [])
        if rows:
            out += ['| Utenza | Piano | Tipo | Punti | Punto nel modello | Stato | Note |', '| --- | --- | --- | --- | --- | --- | --- |']
            for u in rows:
                ref = u['rif_modello']
                where = f"{ref} ({geo[ref]['support']})" if ref and ref in geo else (ref or '—')
                out.append(f"| {u['id']} {_cell(u['nome'])} | {u['piano']} | {u['tipo']} | {_cell(u['punti'])} | {_cell(where)} | "
                           f"{STATO[u['stato']]} | {_cell(u.get('note'))} |")
            out.append('')

    free = by_circ.get(None, [])
    if free:
        out += ['## Rete dati e predisposizioni senza circuito', '',
                '| Utenza | Piano | Tipo | Punti | Stato | Note |', '| --- | --- | --- | --- | --- | --- |']
        for u in free:
            out.append(f"| {u['id']} {_cell(u['nome'])} | {u['piano']} | {u['tipo']} | {_cell(u['punti'])} | {STATO[u['stato']]} | {_cell(u.get('note'))} |")
        out.append('')

    out += ['## Stato di fatto', '', '| Foto | Piano | Cosa c\'è | Destino |', '| --- | --- | --- | --- |']
    for s in d['stato_di_fatto']:
        out.append(f"| [{s['foto']}](foto/{s['foto']}.jpg) | {s['piano']} | {_cell(s['cosa'])} | {_cell(s['destino'])} |")
    out.append('')
    return '\n'.join(out)


def main(argv):
    geometry = json.loads(GEOMETRY.read_text(encoding='utf-8'))
    text = render(load(), geometry)
    if '--check' in argv:
        ok = OUT.exists() and OUT.read_text(encoding='utf-8') == text
        print('SCHEMA.md aggiornato' if ok else 'SCHEMA.md da rigenerare: python -m impianto.schema')
        return 0 if ok else 1
    OUT.write_text(text, encoding='utf-8')
    print(f'scritto {OUT.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
