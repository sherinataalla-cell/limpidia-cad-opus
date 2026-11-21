"""Test del modello P01 e casi di accettazione T01-T12 della revisione R01
(docs/reviews/R01_regressioni.json). I fixture sintetici non sono misure del negozio."""
import copy
import json

import ezdxf
import pytest

from src.model import (load, areas, bounds, contains, gap, placement_status, weakest, smart_layout,
                       rect_cells, floor_poly, envelope_poly, room, ROOT)
from src import checks
from src.generate import generate


@pytest.fixture(scope='module')
def model():
    return load()


@pytest.fixture(scope='module')
def out():
    return generate()


def by_id(results):
    return {r['id']: r for r in results}


def furn(model, fid):
    return next(f for f in model['furniture'] if f['id'] == fid)


# --- base ---------------------------------------------------------------------

def test_ids_unique(model):
    ids = [x['id'] for x in model['furniture']] + [p['id'] for p in model['electrical_points']] + \
          [w['id'] for w in model['walls']] + [o['id'] for o in model['openings']]
    assert len(ids) == len(set(ids))
    assert {'C1', 'C2', 'C3', 'C4', 'CASSA', 'SCRIVANIA', 'ISOLA_SMART'} <= set(ids)


def test_units_and_status(model):
    assert model['units'] == 'mm'
    legal = set(model['status_legend'])
    for f in model['furniture']:
        assert f['status'] in legal and f['position_status'] in legal


def test_gap():
    assert gap((0, 0, 10, 10), (20, 0, 30, 10)) == (10, 'x')
    assert gap((0, 0, 10, 10), (5, 5, 15, 15))[1] == 'overlap'


# --- T01 orientamento -----------------------------------------------------------

def test_T01_orientation(model, out):
    ys = [v[1] for v in model['envelope']['vertices']]
    assert min(ys) == 0  # vetrina a Y minima = in basso in pianta
    assert all(e['x1'] <= 7500 for e in model['facade'])
    ing = next(o for o in model['openings'] if o['id'] == 'P_ING')
    stair = next(z for z in model['room_features'] if z['id'] == 'SCALE')
    assert ing['y'] == 0 and ing['x0'] < 2000          # ingresso a sinistra sulla vetrina
    assert stair['x'] == 0                               # scala a sinistra
    sal = envelope_poly(model).intersection(__import__('shapely.geometry', fromlist=['Polygon']).Polygon(room(model, 'SALETTA')['net']))
    cx, cy = sal.centroid.x, sal.centroid.y
    assert cx > 3750 and cy > 2375                       # saletta in fondo a destra
    cassa = furn(model, 'CASSA')
    assert cassa['x'] == 0 and cassa['y'] + cassa['depth'] == max(ys)  # cassa sul muro sinistro, verso il fondo
    # stesse coordinate nella pianta DXF
    msp = ezdxf.readfile(out / 'A01_pianta_arredi_preliminare.dxf').modelspace()
    texts = [t.dxf.text for t in msp.query('TEXT')]
    assert 'VIA ANDREA SOLARI - VETRINA' in texts


# --- T02 saletta ----------------------------------------------------------------

def test_T02_saletta_topology(model):
    sal = room(model, 'SALETTA')
    env = envelope_poly(model)
    from shapely.geometry import Polygon
    net, outer = Polygon(sal['net']), Polygon(sal['outer'])
    assert env.buffer(0.5).covers(outer)                 # niente fuori dall'involucro (rientro escluso)
    assert abs(net.area / 1e6 - 7.00) < 0.02             # S1/S3: 7,00 m² netti
    door = sum((o['x1'] - o['x0']) * 100 for o in model['openings'] if o['wall'] != 'facciata')
    walls = sum(w['width'] * w['depth'] for w in model['walls'])
    assert outer.difference(net).area == pytest.approx(walls + door, rel=0.001)  # tramezzi + vano porta
    w = next(w for w in model['walls'] if w['id'] == 'W_SAL_O')
    assert w['width'] == 100 and w['source']
    assert model['smart_wall']['face_x'] == w['x']
    assert model['smart_wall']['y1'] - model['smart_wall']['y0'] == 2070  # S2, ipotesi di riferimento
    assert model['smart_wall']['band']['status'] != 'verified'


# --- T03 contenimento in poligono concavo ----------------------------------------

CONCAVE = [[0, 0], [5500, 0], [5500, 450], [7500, 450], [7500, 4750], [0, 4750]]


@pytest.mark.parametrize('rect,expected', [
    ((6000, 100, 6100, 200), False),   # sonda nel rientro: fuori
    ((1000, 1000, 1100, 1100), True),  # dentro
    ((0, 1000, 100, 1100), True),      # tocca il bordo
    ((5400, 300, 5600, 400), False),   # attraversa il bordo
])
def test_T03_concave_containment(rect, expected):
    m = {'envelope': {'vertices': CONCAVE}}
    assert contains(m, rect) is expected


def test_T03_containment_check_flags_probe(model):
    m = copy.deepcopy(model)
    m['envelope']['vertices'] = CONCAVE
    m['furniture'].append({'id': 'REVIEW_RECESS_PROBE', 'x': 6000, 'y': 100, 'width': 100, 'depth': 100,
                           'status': 'assumed', 'position_status': 'assumed', 'front': '-y'})
    assert by_id(checks.containment(m))['CONT-REVIEW_RECESS_PROBE']['outcome'] == 'CONFLITTO'


# --- T04 accostamenti non dichiarati -----------------------------------------------

def _probes(model, declared):
    m = copy.deepcopy(model)
    m['furniture'] = [
        {'id': 'PROBE_A', 'x': 1000, 'y': 3000, 'width': 100, 'depth': 100, 'status': 'assumed', 'front': '-y'},
        {'id': 'PROBE_B', 'x': 1130, 'y': 3000, 'width': 100, 'depth': 100, 'status': 'assumed', 'front': '-y'}]
    m['walls'], m['functional_pairs'] = [], []
    m['adjacencies'] = [{'a': 'PROBE_A', 'b': 'PROBE_B', 'relation': 'accostati'}] if declared else []
    return m


def test_T04_nonexplicit_adjacency(model):
    res = by_id(checks.proximity(_probes(model, False)))
    assert res['PRX-PROBE_A-PROBE_B']['outcome'] == 'AVVISO'
    assert 'non dichiarata' in res['PRX-PROBE_A-PROBE_B']['text']
    res_d = by_id(checks.proximity(_probes(model, True)))
    assert res_d['ADJ-PROBE_A-PROBE_B']['outcome'] == 'OK'
    m = _probes(model, True)
    m['furniture'][1]['x'] = 1050  # sovrapposizione: resta conflitto anche se dichiarato
    assert by_id(checks.proximity(m))['OVL-PROBE_A-PROBE_B']['outcome'] == 'CONFLITTO'


# --- T05 coppie funzionali -----------------------------------------------------------

def test_T05_functional_pairs(model):
    res = by_id(checks.functional_pairs(model))
    fp05 = next(p for p in model['functional_pairs'] if {p['a'], p['b']} == {'SCRIVANIA', 'C4'})
    fp06 = next(p for p in model['functional_pairs'] if {p['a'], p['b']} == {'SCRIVANIA', 'FACCIATA'})
    r5, r6 = res[fp05['id']], res[fp06['id']]
    assert round(r5['mm']) == 1450 and round(r6['mm']) == 100   # valutate a prescindere da soglie generiche
    assert r5['outcome'] == 'COMPATIBILE_IPOTESI'                # mai "superato" su ipotesi
    assert r6['outcome'] == 'NON_VERIFICABILE'                   # criterio mancante
    m = copy.deepcopy(model)
    m['use_assumptions']['chair_zone']['value'] = None
    assert by_id(checks.functional_pairs(m))[fp05['id']]['outcome'] == 'NON_VERIFICABILE'


# --- T06 stati della porta ----------------------------------------------------------

def test_T06_door_states(model):
    m = copy.deepcopy(model)
    m['openings'] = [o for o in m['openings'] if o['id'] != 'P_SAL']
    res = by_id(checks.doors(m))
    assert res['DOOR-SALETTA']['outcome'] == 'AVVISO'
    res = by_id(checks.doors(model))
    assert 'DOOR-SALETTA' not in res
    assert res['SWING-P_SAL']['outcome'] == 'COMPATIBILE_IPOTESI'
    m = copy.deepcopy(model)
    m['furniture'].append({'id': 'PROBE_SWING', 'x': 6900, 'y': 3000, 'width': 200, 'depth': 200,
                           'status': 'assumed', 'front': '-y'})
    assert by_id(checks.doors(m))['SWING-P_SAL']['outcome'] == 'CONFLITTO'
    op = next(o for o in model['openings'] if o['id'] == 'P_SAL')
    assert op['swing_quadrant'][1] > 0 and op['hinge'][0] > (op['x0'] + op['x1']) / 2  # verso l'interno, cerniera a destra


# --- T07 propagazione dello stato -----------------------------------------------------

def test_T07_quality_propagation(model):
    isola = furn(model, 'ISOLA_SMART')
    assert isola['status'] == 'catalog' and placement_status(isola) == 'assumed'
    assert weakest('verified', 'assumed') == 'assumed'
    for r in checks.functional_pairs(model):
        assert r['outcome'] != 'SUPERATO'
    m = copy.deepcopy(model)
    p = m['electrical_points'][0]
    p.update(z=1100, z_status='verified', z_source='rilievo test')
    ids = by_id(checks.electrical(m))
    assert 'EL-Z-' + p['id'] not in ids   # una Z verificata futura è un input valido


# --- T08 superfici --------------------------------------------------------------------

def test_T08_area_semantics(model):
    a = areas(model)
    assert a['involucro (poligono delle facce interne, foro scala incluso)'] == pytest.approx(34.725, abs=0.001)
    assert a['foro scala'] == pytest.approx(2.04, abs=0.001)
    assert a['saletta netta (facce interne dei tramezzi)'] == pytest.approx(7.00, abs=0.02)
    res = by_id(checks.area_checks(model))
    assert res['AREA-PT_DICHIARATO']['outcome'] == 'NON_VERIFICABILE'   # 45 m² non riscalati


# --- T09 geometria della scena ----------------------------------------------------------

def test_T09_render_mesh_bounds(model):
    poly = floor_poly(model)
    cells = rect_cells(poly)
    assert sum((c - a) * (d - b) for a, b, c, d in cells) == pytest.approx(poly.area, rel=1e-6)
    env = envelope_poly(model)
    from shapely.geometry import box
    assert all(env.buffer(0.5).covers(box(*c)) for c in cells)
    assert not [r for r in checks.containment(model) if r['id'].startswith('CONT-')]
    cfg = json.loads((ROOT / 'config' / 'render.json').read_text(encoding='utf-8'))
    assert 'ceiling_height' not in cfg and 'heights' not in cfg  # soffitto e altezze solo dal modello
    assert 'visual_assumptions' in cfg


# --- T10 parete smart --------------------------------------------------------------------

def test_T10_smart_elevation(model, out):
    L = smart_layout(model)
    sw = model['smart_wall']
    assert len(L['panels']) == sw['panels']['count'] == 4
    assert L['fits'] and L['matches_band']
    assert all(round(b - a) == sw['panels']['width'] for a, b in L['panels'])
    assert len(sw['panel_titles']) == 4
    doc = ezdxf.readfile(out / 'F02_prospetto_smart.dxf')
    meas = [round(d.get_measurement()) for d in doc.modelspace().query('DIMENSION')]
    assert meas.count(sw['panels']['width']) >= 4 and 1820 in meas and 2070 in meas


# --- T11 componenti approvati --------------------------------------------------------------

def test_T11_approved_components(model):
    dp = model['display_proposal']
    assert dp['status'] == 'assumed' and dp['stagger'] > 0 and dp['cubby']['board'] > 0
    assert dp['slat_mirror'] and len(dp['slat_columns']) == 2
    assert (ROOT / 'assets' / 'brand' / 'limpidia.png').exists()
    assert (ROOT / 'assets' / 'approved' / 'viste_approvate.png').exists()
    src = (ROOT / 'src' / 'render.py').read_text(encoding='utf-8')
    assert 'for zz in (h * 0.36, h * 0.68)' in src  # due linee LED sulle cassettiere
    assert 'LOGO' in src


# --- T12 utenze e consegne -------------------------------------------------------------------

def test_T12_electrical_and_deliverables(model, out):
    for p in model['electrical_points']:
        for k in ('service', 'support', 'owner', 'access', 'driver', 'route', 'z_status', 'xy_status'):
            assert p.get(k), f"{p['id']}: campo {k} vuoto"
        if p['z'] is None:
            assert p['z_status'] == 'pending'
    for pid in ('E05', 'E06'):
        p = next(e for e in model['electrical_points'] if e['id'] == pid)
        assert any(k in p['access'] for k in ('accesso', 'ispezion', 'passacavi', 'apertura'))
    e01 = [t.dxf.text for t in ezdxf.readfile(out / 'E01_punti_utenza_preliminari.dxf').modelspace().query('TEXT')]
    assert {p['id'] for p in model['electrical_points'] if p['x'] is not None} <= set(e01)
    manifest = (out / 'MANIFEST.md').read_text(encoding='utf-8')
    for f in ('A01_pianta_arredi_preliminare.pdf', 'E01_punti_utenza_preliminari.pdf', 'F02_prospetto_smart.pdf',
              'Q01_quote_aperte.md', 'AB01_abaco_arredi.md'):
        assert f in manifest and (out / f).stat().st_size > 0
    cfg = json.loads((ROOT / 'config' / 'render.json').read_text(encoding='utf-8'))
    assert 'potenz' in json.dumps(cfg, ensure_ascii=False).lower()  # luci render dichiarate non come potenze
