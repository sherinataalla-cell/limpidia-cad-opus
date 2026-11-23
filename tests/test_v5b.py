"""Variante V5b (indicazioni utente 23/11/2026): scrivania verso vetrina e ringhiera, cassetti ad apertura breve.

Le sonde modificano copie in memoria: config/geometry.json non cambia.
"""
import copy

import pytest

from src import checks
from src import generate as gen
from src.model import load, bounds, apply_overrides, use_bands


@pytest.fixture(scope='module')
def model():
    return load()


def variant(model, vid):
    return apply_overrides(model, next(v for v in model['layout_proposals'] if v['id'] == vid))


@pytest.fixture(scope='module')
def v5b(model):
    return variant(model, 'V5b')


def by_id(results):
    return {r['id']: r for r in results}


def furn(m, fid):
    return next(f for f in m['furniture'] if f['id'] == fid)


def test_v5b_extends_v5(model, v5b):
    v5 = variant(model, 'V5')
    for fid in ('CASSA', 'C1', 'C2', 'C3', 'C4', 'ISOLA_SMART'):
        assert bounds(furn(v5b, fid)) == bounds(furn(v5, fid))
    assert bounds(furn(v5b, 'SCRIVANIA')) == (3950, 600, 5550, 1300)
    assert bounds(furn(v5, 'SCRIVANIA')) == (4250, 750, 5850, 1450)       # V5 resta di confronto
    assert v5b['revision'] == model['revision'] + '-V5b'


def test_v5b_y_chain(v5b):
    d = bounds(furn(v5b, 'SCRIVANIA'))
    c2 = bounds(furn(v5b, 'C2'))
    assert (d[1], d[3] - d[1], c2[1] - d[3], c2[3] - c2[1]) == (600, 700, 980, 400)
    assert c2[3] == 2680                                                   # facciata-muro saletta, non netta


def test_v5b_no_fixed_750_and_seats_declared(v5b):
    d = furn(v5b, 'SCRIVANIA')
    assert {s['role']: s['side'] for s in d['seats']} == {'operatore': '-y', 'cliente': '+y'}
    assert all(s['status'] == 'assumed' for s in d['seats'])
    for k in ('seat_operator', 'seat_client', 'seat_move'):
        assert v5b['use_assumptions'][k]['value'] is None               # sedia reale: dato mancante, non 750
    for fp in ('FP02', 'FP09', 'FP05'):
        for sc in next(p for p in v5b['functional_pairs'] if p['id'] == fp)['scenarios']:
            assert 'chair_zone' not in sc['uses']


def test_v5b_distances_and_outcomes(v5b):
    res = by_id(checks.run_all(v5b))
    for fp in ('FP02', 'FP09'):
        assert round(res[fp]['mm']) == 980 and 'residuo 630 mm' in res[fp]['text']
        assert res[fp]['outcome'] == 'NON_VERIFICABILE'                    # sedute reali mancanti, non conflitto
    assert res['FP02-PERCORSO']['outcome'] == 'NON_VERIFICABILE'          # percorso ordinario A, sedute da rilevare
    assert res['FP05-PERCORSO']['outcome'] == 'COMPATIBILE_IPOTESI' and round(res['FP05-PERCORSO']['mm']) == 1550
    assert 'residuo 1200 mm' in res['FP05']['text']
    assert round(res['FP06']['mm']) == 600
    assert res['APPR-P_SAL']['outcome'] == 'CONFLITTO'                    # non risolto dalla scrivania
    assert not [r for r in res.values() if r['id'].startswith('OVL-')]


def _with_seats(m, op, cl):
    m = copy.deepcopy(m)
    m['use_assumptions']['seat_operator'].update(value=op, status='assumed')
    m['use_assumptions']['seat_client'].update(value=cl, status='assumed')
    m['use_assumptions']['seat_move'].update(value=cl, status='assumed')
    return m


def test_alternative_actions_are_not_conflict(v5b):
    """Sonda: con una seduta cliente di 700 la fascia si sovrappone ai cassetti aperti (630): azioni alternative -> AVVISO."""
    m = _with_seats(v5b, 500, 700)
    r = by_id(checks.run_all(m))['FP02']
    assert r['outcome'] == 'AVVISO' and 'azioni alternative' in r['text']


def test_physical_collision_still_conflict(v5b):
    """Sonda: una seduta ordinaria che arriva oltre i fronti chiusi e' una collisione reale."""
    m = _with_seats(v5b, 500, 1000)
    r = by_id(checks.run_all(m))['FP02']
    assert r['outcome'] == 'CONFLITTO'


def test_c1_rarity_not_proof(v5b):
    r = by_id(checks.run_all(v5b))['PROT-C1-RINGHIERA_TESTATA']
    assert r['outcome'] == 'NON_VERIFICABILE' and round(r['mm']) == 100


def test_v5b_e06_and_sheets(v5b, model):
    e06 = next(e for e in v5b['electrical_points'] if e['id'] == 'E06')
    assert (e06['x'], e06['y']) == (4750, 950) and e06['z'] is None
    assert '1550' in e06['support'] and '1950' in e06['support']
    txt = gen.proposals(model)
    assert '600 + 700 + 980 + 400 = 2680' in txt and '550 + 700 + 1030 + 400 = 2680' in txt
    assert '| 680 |' in txt
    assert gen.build_a01(v5b, 'A01-V5b') is not None


def test_seat_bands_follow_declared_sides(v5b):
    d = furn(v5b, 'SCRIVANIA')
    assert use_bands(d, 'seat_client', 600) == [(3950, 1300, 5550, 1900)]
    assert use_bands(d, 'seat_operator', 400) == [(3950, 200, 5550, 600)]


def test_v5b_render_set_current(model):
    rows = gen.render_status(model, 'V5b')
    assert rows and all(ok for _, _, ok, _ in rows), 'render V5b mancanti: python -m src.render --variante=V5b'
    assert all(rev == model['revision'] + '-V5b' for *_, rev in rows)
