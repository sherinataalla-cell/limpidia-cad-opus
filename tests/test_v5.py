"""Variante V5 (indicazioni utente 23/11/2026) e significato corretto dei controlli sulla scala.

Le sonde modificano copie in memoria del modello: config/geometry.json non cambia.
"""
import copy

import pytest

from src import checks
from src import generate as gen
from src.model import load, bounds, apply_overrides, use_bands, guards


@pytest.fixture(scope='module')
def model():
    return load()


@pytest.fixture(scope='module')
def v5(model):
    return apply_overrides(model, next(v for v in model['layout_proposals'] if v['id'] == 'V5'))


def by_id(results):
    return {r['id']: r for r in results}


def furn(m, fid):
    return next(f for f in m['furniture'] if f['id'] == fid)


def test_base_unchanged(model):
    assert furn(model, 'CASSA')['x'] == 0 and furn(model, 'C1')['x'] == 1840
    assert bounds(furn(model, 'SCRIVANIA')) == (4950, 100, 5650, 1700)


def test_v5_positions(v5):
    assert bounds(furn(v5, 'CASSA')) == (1850, 4150, 3050, 4750)
    assert bounds(furn(v5, 'C1')) == (0, 4350, 1500, 4750)
    assert bounds(furn(v5, 'SCRIVANIA')) == (4250, 750, 5850, 1450)
    ls3 = next(c for c in v5['display_proposal']['slat_columns'] if c['id'] == 'LS3')
    assert (ls3['x'], ls3['x'] + ls3['width']) == (1515, 1835)       # fra C1 e cassa, non sopra C1
    for fid, xy in (('C2', (3600, 2280)), ('C3', (4800, 2280)), ('C4', (7100, 300)), ('ISOLA_SMART', (900, 1500))):
        assert (furn(v5, fid)['x'], furn(v5, fid)['y']) == xy


def test_v5_desk_really_rotated(v5):
    """Sedute sui lati lunghi paralleli a VET_2, non uno scambio width/depth con fasce sui lati corti."""
    d = furn(v5, 'SCRIVANIA')
    bands = use_bands(d, 'chair_zone', 750)
    assert bands == [(4250, 0, 5850, 750), (4250, 1450, 5850, 2200)]
    from src.components import all_components
    top = next(c for c in all_components(v5) if c['id'] == 'SCRIVANIA_cassettiera')['box']
    assert top[4] - top[1] > top[3] - top[0]                          # contenitore sul lato corto


def test_v5_desk_distances(v5):
    res = by_id(checks.run_all(v5))
    assert round(res['FP05']['mm']) == 1250
    assert '900 mm' in res['FP05']['text']                           # con cassetti C4 aperti
    for fp in ('FP02', 'FP09'):
        r = res[fp]
        assert round(r['mm']) == 830 and 'residuo 480 mm' in r['text'] and 'residuo 80 mm' in r['text']
        assert r['outcome'] == 'CONFLITTO'                            # seduta + cassetti si sovrappongono
    txt = gen.proposals(load())
    assert '2550 / 2280' in txt and 'mancano 270 mm' in txt and '| -270 |' in txt


def test_v5_stair_semantics(v5, model):
    res = by_id(checks.run_all(v5))
    assert 'FP08-PERCORSO' not in res                                # il lato C1 non e' un accesso
    assert res['ACC-SCALE']['outcome'] == 'COMPATIBILE_IPOTESI'      # accesso dal lato vetrina
    assert round(res['PROT-C1-RINGHIERA_TESTATA']['mm']) == 100
    assert res['REQ-REQ_SCALA_CASSA']['outcome'] == 'NON_VERIFICABILE'
    assert round(res['REQ-REQ_SCALA_CASSA']['mm']) == 1031
    assert res['APPR-P_SAL']['outcome'] == 'CONFLITTO'               # la rotazione non risolve C4-porta saletta
    assert {g['id'] for g in guards(model)} == {'RINGHIERA', 'RINGHIERA_TESTATA'}
    t = next(g for g in guards(model) if g['id'] == 'RINGHIERA_TESTATA')
    assert t['status'] == 'assumed' and t['thickness'] is None and 'utente' in t['source']


def test_all_guards_checked_not_only_first_line(v5):
    """Una testata sintetica che invade l'area cassa deve dare conflitto anche se non e' la prima linea."""
    m = copy.deepcopy(v5)
    for g in m['room_features']:
        if g['type'] == 'line':
            g['thickness'] = 50
    t = next(g for g in m['room_features'] if g['id'] == 'RINGHIERA_TESTATA')
    t['end'] = [1500, 3900]                                           # sonda: testata prolungata verso la cassa
    r = by_id(checks.requirements(m))['REQ-REQ_SCALA_CASSA']
    assert r['outcome'] == 'CONFLITTO'


def test_stair_access_blocked_is_conflict(model):
    m = copy.deepcopy(model)
    furn(m, 'ISOLA_SMART')['x'] = 0
    furn(m, 'ISOLA_SMART')['y'] = 0                                    # sonda: mobile davanti all'imbocco
    assert by_id(checks.stair_access(m))['ACC-SCALE']['outcome'] == 'CONFLITTO'


def test_v5_electrical_realigned(v5):
    E = {e['id']: e for e in v5['electrical_points']}
    c = bounds(furn(v5, 'CASSA'))
    assert (E['E01']['x'], E['E01']['y']) == ((c[0] + c[2]) / 2, c[3])
    k = bounds(furn(v5, 'C1'))
    assert (E['E02']['x'], E['E02']['y']) == ((k[0] + k[2]) / 2, k[3])
    d = bounds(furn(v5, 'SCRIVANIA'))
    assert (E['E06']['x'], E['E06']['y']) == ((d[0] + d[2]) / 2, (d[1] + d[3]) / 2)
    for eid in ('E01', 'E02', 'E06'):
        assert E[eid]['z'] is None and E[eid]['z_status'] == 'pending' and 'V5' in E[eid]['xy_source']


def test_v5_sheets_and_no_component_clash(v5):
    res = checks.run_all(v5)
    assert not [r for r in res if r['id'].startswith(('OVL-', 'CMP-')) and r['outcome'] == 'CONFLITTO']
    assert gen.build_a01(v5, 'A01-V5') is not None and gen.build_e01(v5, 'E01-V5') is not None


def test_v5_render_set_current(model):
    """I render V5 devono esistere ed essere dell'impronta corrente (stessa pianta della tavola A01-V5)."""
    rows = gen.render_status(model, 'V5')
    assert rows and all(ok for _, _, ok, _ in rows), 'render V5 mancanti: python -m src.render --variante=V5'
    assert all(rev == model['revision'] + '-V5' for *_, rev in rows)
