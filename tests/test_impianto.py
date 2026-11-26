"""Coerenza dello schema elettrico (impianto/) con sé stesso e con il modello del negozio."""
import json

from impianto import schema
from src.model import load as load_model

D = schema.load()
MODEL = load_model()


def _ids(items):
    return [i['id'] for i in items]


def test_id_unici():
    tutti = _ids(D['quadri']) + _ids(D['circuiti']) + _ids(D['utenze'])
    doppi = sorted({i for i in tutti if tutti.count(i) > 1})
    assert not doppi, f'id ripetuti: {doppi}'


def test_stati_conosciuti():
    ammessi = set(D['stati'])
    for item in D['quadri'] + D['circuiti'] + D['utenze'] + [D['fornitura']]:
        assert item['stato'] in ammessi, f"{item.get('id', 'fornitura')}: stato {item['stato']!r}"


def test_circuiti_su_quadri_esistenti():
    quadri = set(_ids(D['quadri']))
    for c in D['circuiti']:
        assert c['quadro'] in quadri, f"{c['id']}: quadro {c['quadro']} inesistente"
        if c.get('alimenta'):
            assert c['alimenta'] in quadri, f"{c['id']}: alimenta {c['alimenta']} inesistente"


def test_utenze_su_circuiti_esistenti():
    circuiti = set(_ids(D['circuiti']))
    for u in D['utenze']:
        if u['circuito'] is None:
            assert u['tipo'] in ('dati', 'predisposizione'), f"{u['id']}: solo dati e predisposizioni stanno senza circuito"
        else:
            assert u['circuito'] in circuiti, f"{u['id']}: circuito {u['circuito']} inesistente"


def test_riferimenti_al_modello():
    punti = {p['id'] for p in MODEL['electrical_points']}
    for u in D['utenze']:
        if u['rif_modello']:
            assert u['rif_modello'] in punti, f"{u['id']}: {u['rif_modello']} non è in geometry.json"


def test_ogni_punto_del_modello_ha_un_circuito():
    # se il CAD aggiunge un punto utenza, lo schema elettrico deve dire su quale circuito va
    usati = {u['rif_modello'] for u in D['utenze'] if u['rif_modello']}
    mancanti = sorted({p['id'] for p in MODEL['electrical_points']} - usati)
    assert not mancanti, f'punti del modello senza utenza nello schema elettrico: {mancanti}'


def test_foto_presenti():
    citate = {s['foto'] for s in D['stato_di_fatto']} | set(D['fornitura'].get('foto', []))
    for q in D['quadri']:
        citate |= set(q.get('foto', []))
    mancanti = sorted(f for f in citate if not (schema.ROOT / 'impianto' / 'foto' / f'{f}.jpg').exists())
    assert not mancanti, f'foto mancanti: {mancanti}'


def test_schema_md_aggiornato():
    geometry = json.loads(schema.GEOMETRY.read_text(encoding='utf-8'))
    assert schema.OUT.read_text(encoding='utf-8') == schema.render(D, geometry), \
        'SCHEMA.md non coincide con impianto.json: python -m impianto.schema'
