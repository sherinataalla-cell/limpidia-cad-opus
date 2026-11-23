"""Casi di accettazione R02 (docs/reviews/R02_regressioni.json, T01-T26).

I fixture sintetici (altezze, soffitti, pareti spostate, sonde) servono solo a verificare che il
codice segua il modello: non sono misure del negozio e non modificano config/geometry.json.
I casi visivi (T08, T10, T24) sono documentati nel rapporto outputs/revisione_correzioni_R02.md.
"""
import copy

import ezdxf
import pytest

from src import checks
from src.components import all_components, union_bounds, unexplained_overlaps
from src.model import load, bounds, product_dims, smart_layout, face_of
from src import generate as gen


@pytest.fixture(scope='module')
def model():
    return load()


def by_id(results):
    return {r['id']: r for r in results}


def comps_of(model, owner):
    return [c for c in all_components(model) if c['owner'] == owner]


def furn(model, fid):
    return next(f for f in model['furniture'] if f['id'] == fid)


def elev_spec(model, code):
    return next(e for e in model['elevations'] if e['code'] == code)


def dxf_rects(doc):
    """Rettangoli (u0, z0, u1, z1) delle polilinee chiuse del prospetto (model space 1:1 mm)."""
    out = set()
    for e in doc.modelspace().query('LWPOLYLINE'):
        pts = [(round(p[0]), round(p[1])) for p in e.get_points('xy')]
        if len(pts) == 4:
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            out.add((min(xs), min(ys), max(xs), max(ys)))
    return out


def dxf_hlines(doc):
    return {(round(min(l.dxf.start.x, l.dxf.end.x)), round(l.dxf.start.y), round(max(l.dxf.start.x, l.dxf.end.x)))
            for l in doc.modelspace().query('LINE') if abs(l.dxf.start.y - l.dxf.end.y) < 0.01}


# --- H01 ingombri esterni ---------------------------------------------------------------

def test_T01_isola_outer_envelope(model):
    f = furn(model, 'ISOLA_SMART')
    ub = union_bounds(comps_of(model, 'ISOLA_SMART'))
    x0, y0, x1, y1 = bounds(f)
    assert [round(v) for v in ub] == [x0, y0, 0, x1, y1, f['height']]   # niente +10 mm per lato
    assert x1 - x0 == 390 <= 400                                          # limite decisione
    m = copy.deepcopy(model)
    furn(m, 'ISOLA_SMART')['width'] = 420
    assert by_id(checks.decisions_check(m))['DEC-ISOLA-P']['outcome'] == 'CONFLITTO'


def test_T02_cassa_outer_envelope(model):
    ub = union_bounds(comps_of(model, 'CASSA'))
    assert [round(v) for v in ub] == [0, 4150, 0, 1200, 4750, 1000]
    assert ub[0] >= 0 and ub[4] <= 4750
    assert furn(model, 'CASSA')['status'] == 'pending'      # il prodotto reale resta da acquisire


# --- H02 stessa geometria in 2D e 3D ---------------------------------------------------------

def test_T03_smart_shelf_and_label_same_z(model):
    spec = elev_spec(model, 'F02')
    _, fr, items = gen.elevation_geometry(model, spec)
    rects = dxf_rects(gen.build_elevation(model, spec))
    for cid in ('SMART_ripiano_1', 'SMART_cartellino_1', 'SMART_telaio_1'):
        c = next(i for i in items if i['id'] == cid)
        u0, z0, u1, z1 = (round(v) for v in c['u'])
        assert (u0, z0, u1, z1) in rects                               # prospetto = solido 3D
        assert (z0, z1) == (round(c['box'][2]), round(c['box'][5]))
    sw = model['smart_wall']
    assert sw['shelf']['z_ref'] == 'base' and sw['label']['z_ref'] == 'base'
    shelf = next(i for i in items if i['id'] == 'SMART_ripiano_1')['box']
    assert (shelf[2], shelf[5]) == (sw['shelf']['z'], sw['shelf']['z'] + sw['shelf']['thickness'])


@pytest.mark.parametrize('h', [800, 900])
def test_T04_drawer_led_follow_height(model, h):
    m = copy.deepcopy(model)
    furn(m, 'C1')['height'] = h          # 900: altezza sintetica di prova
    led = m['display_proposal']['drawer_led']
    leds = sorted(c for c in [(round(c['box'][2]), round(c['box'][5])) for c in comps_of(m, 'C1') if c['kind'] == 'led'])
    exp = sorted((round(h * f - led['height'] / 2), round(h * f + led['height'] / 2)) for f in led['axes_fraction'])
    assert leds == exp
    lines = dxf_hlines(gen.build_elevation(m, elev_spec(m, 'F01')))
    for z0, z1 in exp:                                               # stesso asse nel prospetto
        assert any(abs(z - (z0 + z1) / 2) <= 1 for _, z, _ in lines)


@pytest.mark.parametrize('ceiling', [4150, 3800])
def test_T05_slat_top_single_parameter(model, ceiling):
    m = copy.deepcopy(model)
    m['ceiling']['height'] = ceiling     # 3800: fixture sintetico
    top = ceiling - m['display_proposal']['slat_mirror']['top_gap_from_ceiling']
    slats = [c for c in all_components(m) if c['kind'] == 'slat']
    assert slats and all(round(c['box'][5]) == top for c in slats)
    rects = dxf_rects(gen.build_elevation(m, elev_spec(m, 'F01')))
    assert any(r[3] == top for r in rects)
    src = (gen.ROOT / 'config' / 'render.json').read_text(encoding='utf-8')
    assert 'slat_top_gap' not in src                                 # nessun secondo parametro nel render


# --- H03 abaco -------------------------------------------------------------------------------

def test_T06_product_dims_independent_of_rotation(model):
    c4 = furn(model, 'C4')
    assert product_dims(c4)['L'] == 1500 and product_dims(c4)['P'] == 400
    assert product_dims(furn(model, 'SCRIVANIA'))['L'] == 1600 and product_dims(furn(model, 'SCRIVANIA'))['P'] == 700
    assert product_dims(furn(model, 'ISOLA_SMART'))['P'] == 390
    rot = dict(c4, front='-y', width=c4['depth'], depth=c4['width'])   # stessa cassettiera ruotata
    a, b = product_dims(c4), product_dims(rot)
    assert (a['L'], a['P'], a['H']) == (b['L'], b['P'], b['H']) and a['angle'] != b['angle']
    ab = gen.ab01(model)
    assert '1500 × 400 × 800' in ab and '1600 × 700' in ab and '400 × 1500' in ab   # prodotto e X×Y distinti


# --- H04 pareti per ID -------------------------------------------------------------------------

def test_T07_wall_move_updates_elevation_and_registers(model):
    m = copy.deepcopy(model)
    w = next(w for w in m['walls'] if w['id'] == 'W_SAL_O')
    w['x'] -= 100                                                   # variazione sintetica
    face = face_of(m, elev_spec(m, 'F02')['host'])
    assert face['fixed'] == w['x']
    _, _, items0 = gen.elevation_geometry(model, elev_spec(model, 'F02'))
    _, _, items1 = gen.elevation_geometry(m, elev_spec(m, 'F02'))
    assert len(items1) == len(items0) > 0                            # nessun elemento perso
    f0 = next(c for c in items0 if c['id'] == 'SMART_telaio_1')['box'][0]
    f1 = next(c for c in items1 if c['id'] == 'SMART_telaio_1')['box'][0]
    assert f1 == f0 - 100
    q, _ = gen.q01(m)
    assert f"x {w['x']}" in q
    src = (gen.ROOT / 'src' / 'generate.py').read_text(encoding='utf-8')
    assert 'ELEVATIONS = [' not in src                               # prospetti dal modello, non da tabelle fisse


# --- H06 parete smart ---------------------------------------------------------------------------

def test_T09_smart_panels_gap_and_interaxis(model):
    L = smart_layout(model)
    assert (L['frame'], L['clear_gap'], L['interaxis'], L['image']) == (410, 60, 470, 380)
    assert L['fits'] and L['matches_band']
    pts = [p for p in L['panels']]
    assert all(round(abs(a[0] - b[0])) == 470 for a, b in zip(pts, pts[1:]))
    assert all(round(abs(b[1] - a[0])) == 60 or round(abs(a[0] - b[1])) == 60 for a, b in zip(pts, pts[1:]))
    texts = ' '.join(t.dxf.text for t in gen.build_elevation(model, elev_spec(model, 'F02')).modelspace().query('TEXT'))
    assert 'distanza libera 60' in texts and 'interasse 470' in texts and 'interasse 60' not in texts


def test_T10_smart_images_declared_placeholders(model):
    assert model['smart_wall']['images']['status'] == 'pending'
    imgs = [c for c in all_components(model) if c['kind'] == 'image']
    assert len(imgs) == 4 and all(c['status'] == 'pending' for c in imgs)


# --- H07 raccordi -----------------------------------------------------------------------------------

def test_T11_no_unexplained_overlaps(model):
    cs = all_components(model)
    assert unexplained_overlaps(cs) == []
    cub = [c for c in cs if c['owner'] == 'ESP_C1' and c['kind'] == 'cubby']
    cx0 = min(c['box'][0] for c in cub)
    cz0, cz1 = min(c['box'][2] for c in cub), max(c['box'][5] for c in cub)
    for s in (c for c in cs if c['owner'] == 'ESP_C1' and c['kind'] == 'shelf'):
        if cz0 < s['box'][5] and s['box'][2] < cz1:                   # mensola all'altezza del cubotto
            assert s['box'][3] <= cx0 + 0.5                           # interrotta sul fianco


# --- H08 registro utenze ------------------------------------------------------------------------------

def test_T12_electrical_register(model):
    reg = gen.e01_register(model)
    assert 'Quantità' in reg and 'Percorso' in reg
    for p in model['electrical_points']:
        assert p['id'] in reg
        assert str(p.get('quantity')) in reg and p['route'][:30] in reg
    for pid in ('E07', 'E08', 'E09'):
        assert next(p for p in model['electrical_points'] if p['id'] == pid)['x'] is None
    m = copy.deepcopy(model)
    p = next(p for p in m['electrical_points'] if p['x'] is not None)
    p.update(z=1100, z_status='verified', z_source='rilievo sintetico')
    assert '1100 (verificata)' in gen.e01_register(m)


# --- G01 accostamenti ---------------------------------------------------------------------------------

def test_T13_cassa_on_wrong_wall(model):
    m = copy.deepcopy(model)
    furn(m, 'CASSA').update(x=3000, y=0)
    r = by_id(checks.adjacency(m))['ADJ_CASSA_SINISTRA']
    assert r['outcome'] == 'CONFLITTO' and 'PARETE_SINISTRA' in r['text'] and 'x0' in r['text']


def test_T14_side_and_segment(model):
    assert by_id(checks.adjacency(model))['ADJ_CASSA_SINISTRA']['outcome'] == 'OK'
    m = copy.deepcopy(model)
    next(a for a in m['adjacencies'] if a['id'] == 'ADJ_CASSA_SINISTRA')['side'] = 'x1'
    assert by_id(checks.adjacency(m))['ADJ_CASSA_SINISTRA']['outcome'] == 'CONFLITTO'
    m = copy.deepcopy(model)
    furn(m, 'C1')['front'] = '+y'                                     # fronte contro il muro
    assert by_id(checks.adjacency(m))['ADJ_C1_FONDO']['outcome'] == 'CONFLITTO'


# --- G02 qualità delle dipendenze -----------------------------------------------------------------------

def test_T15_verified_door_with_assumed_obstacles(model):
    m = copy.deepcopy(model)
    next(o for o in m['openings'] if o['id'] == 'P_SAL')['status'] = 'verified'
    r = by_id(checks.doors(m))['SWING-P_SAL']
    assert r['outcome'] != 'SUPERATO' and r.get('deps')


def test_T16_missing_and_colliding(model):
    m = copy.deepcopy(model)
    m['furniture'].append({'id': 'PROBE_SWING', 'x': 6900, 'y': 3000, 'width': 200, 'depth': 200,
                           'status': 'assumed', 'front': '-y'})
    assert by_id(checks.doors(m))['SWING-P_SAL']['outcome'] == 'CONFLITTO'
    assert by_id(checks.functional_pairs(model))['FP07']['outcome'] == 'NON_VERIFICABILE'   # spessore ringhiera


# --- G03 porte -------------------------------------------------------------------------------------------

def test_T17_door_outside_shop(model):
    m = copy.deepcopy(model)
    next(o for o in m['openings'] if o['id'] == 'P_ING').update(x0=9000, x1=9900, hinge=[9000, 0])
    res = by_id(checks.doors(m))
    assert res['HOST-P_ING']['outcome'] == 'CONFLITTO'
    assert res.get('SWING-P_ING', {}).get('outcome') != 'COMPATIBILE_IPOTESI'


def test_T18_hinge_inconsistent(model):
    m = copy.deepcopy(model)
    op = next(o for o in m['openings'] if o['id'] == 'P_SAL')
    op['hinge'] = [op['x0'] - 500, op['hinge'][1]]
    assert by_id(checks.doors(m))['HOST-P_SAL']['outcome'] == 'CONFLITTO'


# --- G04 coppie funzionali ----------------------------------------------------------------------------------

def test_T19_fp05_collision_and_path_separate(model):
    res = by_id(checks.functional_pairs(model))
    assert round(res['FP05']['mm']) == 1450 and res['FP05']['outcome'] == 'COMPATIBILE_IPOTESI'
    assert round(res['FP05-PERCORSO']['mm']) == 350
    assert res['FP05-PERCORSO']['outcome'] == 'NON_VERIFICABILE'       # criterio di percorso non dichiarato


def test_T20_description_does_not_change_outcome(model):
    m = copy.deepcopy(model)
    for p in m['functional_pairs']:
        p['function'] = p['function'] + ' accesso passaggio percorso'   # campo descrittivo effettivo
    a = {k: (v['outcome'], v['mm']) for k, v in by_id(checks.functional_pairs(model)).items()}
    b = {k: (v['outcome'], v['mm']) for k, v in by_id(checks.functional_pairs(m)).items()}
    assert a == b


def test_T21_unknowns_stay_open(model):
    res = by_id(checks.run_all(model))
    assert res['USE-operator_zone']['outcome'] == 'NON_VERIFICABILE'
    assert res['USE-door_leaf_island']['outcome'] == 'NON_VERIFICABILE'
    assert model['use_assumptions']['railing_thickness']['value'] is None


def test_T22_baseline_conflicts_still_detected(model):
    res = by_id(checks.run_all(model))
    assert res['FP02-PERCORSO']['outcome'] == 'CONFLITTO' and round(res['FP02-PERCORSO']['mm']) == 230
    assert res['APPR-P_SAL']['outcome'] == 'CONFLITTO' and '220 × 20' in res['APPR-P_SAL']['text']
    assert res['SWING-P_SAL']['outcome'] != 'CONFLITTO'               # accesso distinto dall'anta


# --- H09 render ------------------------------------------------------------------------------------------------

def test_T23_render_manifest_detects_missing(model, tmp_path, monkeypatch):
    monkeypatch.setattr(gen, 'OUT', tmp_path)
    rows = gen.render_status(model)
    assert rows and not any(ok for _, _, ok, _ in rows)


def test_T23_render_set_current_revision(model):
    rows = gen.render_status(model)
    assert rows and all(ok for _, _, ok, _ in rows), 'set di render incompleto'          # consegna: non si salta
    assert all(rev == model['revision'] for *_, rev in rows), 'render di altra revisione o di modello/codice cambiati'


def test_T23_render_fingerprint_detects_change(model, tmp_path, monkeypatch):
    import json
    (tmp_path / 'render').mkdir()
    for name, f, _, _ in gen.render_status(model):
        (tmp_path / 'render' / f.name).write_bytes(b'png')
    meta = {f.name: {'revision': model['revision'], 'fingerprint': 'impronta-vecchia'} for _, f, _, _ in gen.render_status(model)}
    (tmp_path / 'render' / 'render_meta.json').write_text(json.dumps(meta), encoding='utf-8')
    monkeypatch.setattr(gen, 'OUT', tmp_path)
    assert not any(rev == model['revision'] for *_, rev in gen.render_status(model))


def test_T09_render_uses_components():
    bpy = pytest.importorskip('bpy')
    import json
    from src.render import build_scene, RENDER_CFG
    m = load()
    build_scene(bpy, m, json.loads(RENDER_CFG.read_text(encoding='utf-8')))
    for c in all_components(m):
        if c['kind'] == 'logo':
            continue
        o = bpy.data.objects[c['id']]
        box = c['box']
        for i in range(3):                                  # ingombro completo: tre dimensioni e tre centri
            assert o.dimensions[i] * 1000 == pytest.approx(box[i + 3] - box[i], abs=0.5), (c['id'], i)
            assert o.location[i] * 1000 == pytest.approx((box[i] + box[i + 3]) / 2, abs=0.5), (c['id'], i)


# --- G05 scala–cassa ---------------------------------------------------------------------------------------------

@pytest.mark.parametrize('g,ok', [(250, False), (999, False), (1000, True), (1100, True), (1200, True)])
def test_T25_stair_cash_clearance(model, g, ok):
    m = copy.deepcopy(model)
    stair = next(z for z in m['room_features'] if z['id'] == 'SCALE')
    y_end = stair['y'] + stair['depth']
    furn(m, 'CASSA')['y'] = y_end + g                 # sonda: solo la luce, non una posizione proposta
    r = by_id(checks.requirements(m))['REQ-REQ_SCALA_CASSA']
    assert round(r['mm']) == g
    if not ok:
        assert r['outcome'] == 'CONFLITTO'
    else:
        assert r['outcome'] == 'NON_VERIFICABILE'     # parapetto/corrimano non rilevati
        for rail in [z for z in m['room_features'] if z['type'] == 'line']:
            rail['thickness'] = 0                     # fixture: limite fisico noto per TUTTE le protezioni
        assert by_id(checks.requirements(m))['REQ-REQ_SCALA_CASSA']['outcome'] == 'COMPATIBILE_IPOTESI'


def test_T25_measured_on_full_envelope(model):
    r = by_id(checks.requirements(model))['REQ-REQ_SCALA_CASSA']
    assert r['outcome'] == 'CONFLITTO' and round(r['mm']) == 250
    assert '850' in r['text'] and '1600' in r['text'] and '750' in r['text'] and '950' in r['text']


def test_T26_feasibility_and_provenance(model):
    stair = next(z for z in model['room_features'] if z['id'] == 'SCALE')
    assert stair['y'] + stair['depth'] == 3900                        # scala non accorciata
    txt = gen.proposals(model)
    for s in ('850', '1600 / 1800', 'manca 750', 'V1'):
        assert s in txt
    v1 = next(v for v in model['layout_proposals'] if v['id'] == 'V1')
    m = gen.apply_overrides(model, v1)
    r = by_id(checks.requirements(m))['REQ-REQ_SCALA_CASSA']
    assert r['mm'] >= 1000 and r['outcome'] != 'CONFLITTO'
    assert by_id(checks.adjacency(m))['ADJ_CASSA_SINISTRA']['outcome'] == 'CONFLITTO'   # deroga visibile
    assert furn(model, 'CASSA')['x'] == 0                             # base invariata



# --- Audit P02 (22/11/2026): difetti riprodotti -------------------------------------------------

def _v1(model):
    return gen.apply_overrides(model, next(v for v in model['layout_proposals'] if v['id'] == 'V1'))


@pytest.mark.parametrize('end_y,th,exp', [(3900, 50, 'COMPATIBILE_IPOTESI'), (4400, 50, 'CONFLITTO'), (3900, None, 'NON_VERIFICABILE')])
def test_A1_railing_position_and_extent(model, end_y, th, exp):
    m = _v1(model)
    for g in [z for z in m['room_features'] if z['type'] == 'line']:
        g['thickness'] = th                        # tutte le protezioni, non solo la prima linea
    rail = next(z for z in m['room_features'] if z['id'] == 'RINGHIERA')
    rail['end'] = [rail['end'][0], end_y]          # ringhiera sintetica: estensione verso la cassa
    r = by_id(checks.requirements(m))['REQ-REQ_SCALA_CASSA']
    assert r['outcome'] == exp
    if end_y == 4400:
        assert round(r['mm']) == 975                # dall'ingombro fisico, non foro meno mezzo spessore


def test_A2_v1_c1_stair_and_diagonal(model):
    res = by_id(checks.run_all(_v1(model)))
    assert round(res['FP08']['mm']) == 450
    # P04: il lato C1 non e' un accesso alla scala (indicazione utente 23/11): nessun percorso obbligatorio,
    # ma la vicinanza dei cassetti alle protezioni resta una criticita' d'uso non verificabile
    assert 'FP08-PERCORSO' not in res
    assert res['PROT-C1-RINGHIERA_TESTATA']['outcome'] == 'NON_VERIFICABILE'
    assert round(res['PROT-C1-RINGHIERA_TESTATA']['mm']) == 100
    assert res['REQ-REQ_SCALA_CASSA']['outcome'] == 'NON_VERIFICABILE'
    assert 'non la larghezza di un percorso' in res['REQ-REQ_SCALA_CASSA']['text']
    txt = gen.proposals(model)
    assert 'DIAGONALE' in txt and 'non è una soluzione chiusa' in txt and 'PROT-C1-RINGHIERA_TESTATA' in txt


def test_A3_access_zone_depends_on_neighbours(model):
    m = copy.deepcopy(model)
    op = next(o for o in m['openings'] if o['id'] == 'P_SAL')
    op['status'] = 'verified'
    for w in m['walls']:
        if w['id'].startswith('W_SAL_S'):
            w['status'] = 'verified'
    next(r for r in m['rooms'] if r['id'] == 'SALETTA')['status'] = 'verified'
    m['use_assumptions']['screening_passage']['status'] = 'verified'
    furn(m, 'C4')['y'] = 280                        # come V2: appena fuori dalla zona, posa ipotizzata
    r = by_id(checks.doors(m))['APPR-P_SAL']
    assert r['outcome'] == 'COMPATIBILE_IPOTESI' and 'C4' in r['text']


def test_A3_host_text_without_hinge(model):
    m = copy.deepcopy(model)
    next(o for o in m['openings'] if o['id'] == 'P_SAL')['hinge'] = None
    res = by_id(checks.doors(m))
    assert 'cerniera, anta e verso coerenti' not in res['HOST-P_SAL']['text']
    assert res['SWING-P_SAL']['outcome'] == 'NON_VERIFICABILE'


def test_A4_d01_plinth_from_component(model):
    doc = gen.build_d01(model)
    zoc = next(c for c in all_components(model) if c['owner'] == 'C1' and c['kind'] == 'plinth')['box']
    depth = round(zoc[4] - zoc[1])
    meas = [round(d.get_measurement()) for d in doc.modelspace().query('DIMENSION')]
    assert depth in meas                           # 370: stesso zoccolo di abaco e render
    m = copy.deepcopy(model)
    m['display_proposal']['shelf_levels'] = [1250, 1530, 1850, 2150]   # livelli sintetici
    meas2 = [round(d.get_measurement()) for d in gen.build_d01(m).modelspace().query('DIMENSION')]
    assert 320 in meas2                            # passo dal modello, non +300 fisso


def test_A5_electrical_sources(model):
    q, _ = gen.q01(model)
    e = gen.e01_register(model)
    assert 'Fonte X, Y' in e and 'Fonte Z' in e
    for pid in ('E07', 'E08', 'E09'):
        row = next(l for l in q.splitlines() if l.startswith(f'| {pid} | posizione'))
        assert 'S0' not in row and 'da documentare' in row
    assert 'da documentare' in next(l for l in q.splitlines() if l.startswith('| E01 | quota Z'))
