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


def test_id_pdf_esadecimale_e_letterale():
    # PyMuPDF a volte scrive l'/ID come stringa letterale: deve diventare la stessa impronta
    corpo = b'%PDF-1.7\n1 0 obj<<>>endobj\nxref\ntrailer\n<</Size 2/Root 1 0 R'
    coda = b'>>\nstartxref\n9\n%%EOF\n'
    esa = corpo + b'/ID[<' + b'A' * 32 + b'><' + b'B' * 32 + b'>]' + coda
    lett = corpo + b'/ID[(n0\\021~]\\302\\214w?\\(cu6mdy)<' + b'C' * 32 + b'>]' + coda
    assert gen._stable_pdf_id(esa) == gen._stable_pdf_id(lett)


def test_caratteri_dal_repo():
    # i PDF devono usare i caratteri di assets/fonts, non quelli installati sul computer
    from ezdxf.fonts import fonts
    from src.model import ROOT
    for nome in ('OpenSans-Regular.ttf', 'OpenSansCondensed-Light.ttf'):
        voce = fonts.font_manager._font_cache.get(nome, '')
        assert voce is not None and (ROOT / 'assets' / 'fonts') in voce.file_path.resolve().parents, nome
