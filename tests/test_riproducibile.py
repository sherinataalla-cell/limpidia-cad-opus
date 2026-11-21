"""Rigenerare la stessa revisione del modello deve dare file identici.

Senza questa proprietà ogni `python -m src.generate` cambia tutti i DXF e PDF
(data, GUID, /ID del PDF, retini) anche a disegno invariato, e il confronto
fra tavole committate e tavole rigenerate dalla CI non può funzionare.
"""
import hashlib

from src import generate as gen
from src.model import OUT


def _impronte():
    return {p.name: hashlib.md5(p.read_bytes()).hexdigest()
            for p in sorted(OUT.iterdir()) if p.suffix in {'.dxf', '.pdf', '.md'}}


def test_rigenerazione_identica():
    gen.generate()
    prima = _impronte()
    gen.generate()
    dopo = _impronte()
    diversi = sorted(k for k in prima if prima[k] != dopo.get(k))
    assert not diversi, f'file cambiati rigenerando lo stesso modello: {diversi}'


def test_data_dalla_revisione():
    model = gen.load()
    assert model.get('revision_date'), 'manca revision_date in geometry.json'
    assert gen.TODAY == model['revision_date']
