"""Modello parametrico unico (unità: mm) e geometria comune a tavole, controlli e render.

Convenzione: origine nell'angolo vetrina sinistro, X verso destra, Y verso il
fondo, Z verso l'alto. La vetrina è il lato a Y minima. Tavole e render usano
queste coordinate senza ulteriori trasformazioni.
"""
import json
import math
from pathlib import Path

from shapely.geometry import Polygon, box as sbox, LineString, Point
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'config' / 'geometry.json'
OUT = ROOT / 'outputs'

STATUS_LABEL = {
    'verified': 'verificata',
    'catalog': 'da catalogo',
    'assumed': 'ipotesi',
    'pending': 'da definire',
}
# Affidabilità crescente: un dato derivato prende lo stato meno affidabile
_RANK = {'pending': 0, 'assumed': 1, 'catalog': 2, 'verified': 3}


def load(path=DATA):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def weakest(*statuses):
    """Stato meno affidabile fra quelli dati (per le quote derivate)."""
    st = [s for s in statuses if s]
    return min(st, key=lambda s: _RANK[s]) if st else 'pending'


def placement_status(item):
    """Stato di una grandezza che dipende da dimensione E posizione."""
    return weakest(item.get('status'), item.get('position_status', item.get('status')))


def bounds(item):
    """Rettangolo (xmin, ymin, xmax, ymax) di un oggetto x/y/width/depth."""
    return (item['x'], item['y'], item['x'] + item['width'], item['y'] + item['depth'])


def rect_poly(r):
    return sbox(*r)


def envelope_poly(model):
    return Polygon(model['envelope']['vertices'])


def stair_poly(model):
    s = next(z for z in model['room_features'] if z['id'] == 'SCALE')
    return rect_poly(bounds(s))


def _poly_coords(g):
    g = g.simplify(0)
    return [[round(x), round(y)] for x, y in list(g.exterior.coords)[:-1]]


def rooms(model):
    """Stanze con 'outer' e 'net' RICAVATI dai tramezzi indicati in 'bounded_by' (nessuna coordinata duplicata).

    bounded_by = {'x_wall': id, 'y_wall': id}: la stanza occupa la parte dell'involucro oltre il tramezzo
    parallelo a Y (lato +x) e oltre quello parallelo a X (lato +y). Senza bounded_by restano i poligoni dichiarati.
    """
    out = []
    env = envelope_poly(model)
    walls = {w['id']: w for w in model.get('walls', [])}
    for r in model.get('rooms', []):
        r = dict(r)
        bb = r.get('bounded_by')
        if bb:
            xw, yw = walls[bb['x_wall']], walls[bb['y_wall']]
            big = 10 ** 6
            outer = env.intersection(sbox(xw['x'], yw['y'], big, big))
            net = env.intersection(sbox(xw['x'] + xw['width'], yw['y'] + yw['depth'], big, big))
            r['outer'], r['net'] = _poly_coords(outer), _poly_coords(net)
        out.append(r)
    return out


def room(model, rid):
    return next(r for r in rooms(model) if r['id'] == rid)


def walls_poly(model):
    return unary_union([rect_poly(bounds(w)) for w in model.get('walls', [])])


def floor_poly(model):
    """Pavimento del negozio: involucro meno foro scala (la saletta resta pavimento)."""
    return envelope_poly(model).difference(stair_poly(model))


def shop_poly(model):
    """Zona vendita: pavimento meno l'impronta esterna della saletta (tramezzi compresi)."""
    out = floor_poly(model)
    for r in rooms(model):
        out = out.difference(Polygon(r['outer']))
    return out


def areas(model):
    """Superfici con definizione esplicita (m²)."""
    env = envelope_poly(model)
    st = stair_poly(model).intersection(env)
    sal = room(model, 'SALETTA')
    sal_out = Polygon(sal['outer'])
    sal_net = Polygon(sal['net'])
    walls = walls_poly(model).intersection(env)
    return {
        'involucro (poligono delle facce interne, foro scala incluso)': env.area / 1e6,
        'foro scala': st.area / 1e6,
        'tramezzi saletta (impronta)': walls.area / 1e6,
        'saletta netta (facce interne dei tramezzi)': sal_net.area / 1e6,
        'saletta lorda (con tramezzi)': sal_out.area / 1e6,
        'zona vendita calpestabile (involucro - foro scala - saletta lorda)': env.difference(st).difference(sal_out).area / 1e6,
    }


def contains(model, r, tol=0.5):
    """Vero se l'intera impronta r sta nel poligono dell'involucro (concavità comprese)."""
    return envelope_poly(model).buffer(tol).covers(rect_poly(r))


def gap(a, b):
    """Distanza libera tra due rettangoli allineati agli assi: (distanza, asse).

    Distanza negativa = sovrapposizione. asse = 'diag' se non si fronteggiano.
    """
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    dx = max(bx0 - ax1, ax0 - bx1)
    dy = max(by0 - ay1, ay0 - by1)
    if dx < 0 and dy < 0:
        return max(dx, dy), 'overlap'
    if dx >= 0 and dy < 0:
        return dx, 'x'
    if dy >= 0 and dx < 0:
        return dy, 'y'
    return (dx ** 2 + dy ** 2) ** 0.5, 'diag'


def polygon_area(vertices):
    return Polygon(vertices).area


def point_in_rect(x, y, r, tol=0):
    return r[0] - tol <= x <= r[2] + tol and r[1] - tol <= y <= r[3] + tol


def front_band(item, depth):
    """Fascia di profondità `depth` davanti al frontale dichiarato del mobile."""
    x0, y0, x1, y1 = bounds(item)
    return {'-y': (x0, y0 - depth, x1, y0), '+y': (x0, y1, x1, y1 + depth),
            '-x': (x0 - depth, y0, x0, y1), '+x': (x1, y0, x1 + depth, y1)}[item['front']]


def use_bands(item, key, value, use=None):
    """Fasce d'uso di un mobile (stessa regola per tavole e controlli).

    Sedute (`chair_zone`): sui due lati lunghi del piano, qualunque sia l'orientamento.
    Persona ai cassetti (`drawer_user_zone`): oltre la corsa dei cassetti.
    Altri usi: davanti al frontale dichiarato.
    """
    x0, y0, x1, y1 = bounds(item)
    seats = item.get('seats') or []
    if key.startswith('seat_'):
        # sedute dichiarate per lato (V5b): solo sui lati dove c'e' una seduta con quel dato
        sides = [st['side'] for st in seats if st.get('use') == key or key == 'seat_move']
        side_box = {'-y': (x0, y0 - value, x1, y0), '+y': (x0, y1, x1, y1 + value),
                    '-x': (x0 - value, y0, x0, y1), '+x': (x1, y0, x1 + value, y1)}
        return [side_box[sd] for sd in sides]
    if key == 'chair_zone':
        if (y1 - y0) >= (x1 - x0):
            return [(x0 - value, y0, x0, y1), (x1, y0, x1 + value, y1)]
        return [(x0, y0 - value, x1, y0), (x0, y1, x1, y1 + value)]
    if key == 'drawer_user_zone':
        de = ((use or {}).get('drawer_extension') or {}).get('value') or 0
        return [front_band(item, de + value)]
    return [front_band(item, value)]


def guards(model, stair_id='SCALE'):
    """Tutte le protezioni (linee) di una scala: ringhiera longitudinale, testata, ecc."""
    return [z for z in model['room_features'] if z['type'] == 'line' and z.get('guards', stair_id) == stair_id]


def apply_overrides(model, ov):
    """Modello di una variante: copia della base con le sole modifiche dichiarate nella proposta."""
    import copy
    if ov.get('extends'):   # variante di una variante (es. V5b su V5): prima le modifiche del genitore
        parent = next(v for v in model['layout_proposals'] if v['id'] == ov['extends'])
        m = apply_overrides(model, parent)
        m['revision'] = model['revision']
    else:
        m = copy.deepcopy(model)
    for fid, fields in ov.get('furniture', {}).items():
        next(f for f in m['furniture'] if f['id'] == fid).update(fields)
    for cid, fields in ov.get('slat_columns', {}).items():
        next(c for c in m['display_proposal']['slat_columns'] if c['id'] == cid).update(fields)
    for pid, fields in ov.get('functional_pairs', {}).items():
        next(p for p in m['functional_pairs'] if p['id'] == pid).update(fields)
    for k, v in ov.get('display_proposal', {}).items():
        m['display_proposal'][k] = v
    for aid, a in ov.get('adjacencies', {}).items():   # None = accostamento non piu' valido nella variante
        m['adjacencies'] = [x for x in m['adjacencies'] if x['id'] != aid]
        if a is not None:
            m['adjacencies'].append(a)
    for eid, fields in ov.get('electrical_points', {}).items():
        next(e for e in m['electrical_points'] if e['id'] == eid).update(fields)
    m['revision'] = model['revision'] + '-' + ov['id']
    return m


def back_side(item):
    """Lato del retro, opposto al frontale dichiarato."""
    return {'-y': 'y1', '+y': 'y0', '-x': 'x1', '+x': 'x0'}[item['front']]


def door_sweep(op, segments=24):
    """Settore circolare percorso dall'anta (poligono)."""
    hx, hy = op['hinge']
    sx, sy = op['swing_quadrant']
    r = op['leaf']
    pts = [(hx, hy)]
    for k in range(segments + 1):
        t = math.pi / 2 * k / segments
        pts.append((hx + sx * r * math.cos(t), hy + sy * r * math.sin(t)))
    return Polygon(pts)


def door_closed_leaf(op):
    """Segmento dell'anta chiusa (a filo del vano)."""
    hx, hy = op['hinge']
    sx, _ = op['swing_quadrant']
    return (hx, hy), (hx + sx * op['leaf'], hy)


def door_open_leaf(op):
    hx, hy = op['hinge']
    _, sy = op['swing_quadrant']
    return (hx, hy), (hx, hy + sy * op['leaf'])


def smart_wall_geom(model):
    """Faccia della parete smart ricavata dal tramezzo e dal rivestimento (nessuna coordinata duplicata)."""
    sw = model['smart_wall']
    w = next(w for w in model['walls'] if w['id'] == sw['wall'])
    return {'face_x': w['x'], 'cladding_face': w['x'] - sw['cladding']['thickness'],
            'y0': w['y'], 'y1': w['y'] + w['depth']}


def smart_layout(model):
    """Composizione della parete smart sui telai esterni.

    frame_outer_width = larghezza esterna del telaio; clear_gap = distanza libera fra
    telai; interasse = frame_outer_width + clear_gap; immagine = telaio - 2 x bordo.
    """
    sw = model['smart_wall']
    g = smart_wall_geom(model)
    p = sw['panels']
    w, gapc = p['frame_outer_width'], p['clear_gap']
    total = p['count'] * w + (p['count'] - 1) * gapc
    ys = []
    y = g['y1'] - sw['margin_start']   # da sinistra (fondo, Y alta) verso destra guardando la parete
    for _ in range(p['count']):
        ys.append((y - w, y))
        y -= w + gapc
    available = g['y1'] - g['y0']
    return {'total': total, 'band': sw['band']['length'], 'available': available, 'panels': ys,
            'fits': sw['margin_start'] + total <= available, 'matches_band': total == sw['band']['length'],
            'interaxis': w + gapc, 'clear_gap': gapc, 'frame': w, 'image': w - 2 * p['frame_border'],
            'margin_end': available - sw['margin_start'] - total}


def product_dims(item):
    """L/P/H del prodotto dal fronte dichiarato: L lungo il fronte, P perpendicolare.

    La rotazione cambia l'ingombro X/Y, non L/P/H. Angolo: fronte -y = 0°, -x = 90°,
    +y = 180°, +x = 270° (rotazione antioraria vista dall'alto).
    """
    along_x = item['front'] in ('-y', '+y')
    L, P = (item['width'], item['depth']) if along_x else (item['depth'], item['width'])
    angle = {'-y': 0, '-x': 90, '+y': 180, '+x': 270}[item['front']]
    return {'L': L, 'P': P, 'H': item.get('height'), 'angle': angle}


def _clip_pieces(model, a, b, n):
    """Tratti del segmento a-b (spostato di 1 mm lungo n) che si affacciano sulla zona vendita."""
    from shapely.geometry import LineString
    off = LineString([(a[0] + n[0], a[1] + n[1]), (b[0] + n[0], b[1] + n[1])])
    inter = off.intersection(shop_poly(model))
    return [g for g in _geoms(inter) if g.length > 1]


def _face(fid, a, b, n, pieces):
    axis = 'x' if a[1] == b[1] else 'y'
    fixed = a[1] if axis == 'x' else a[0]
    coords = [c[0] if axis == 'x' else c[1] for g in pieces for c in g.coords]
    lo, hi = (min(coords), max(coords)) if coords else sorted((a[0], b[0]) if axis == 'x' else (a[1], b[1]))
    return {'id': fid, 'axis': axis, 'fixed': fixed, 'lo': lo, 'hi': hi, 'n': n, 'pieces': len(pieces)}


def faces(model):
    """Facce di parete con ID: lati dell'involucro (nome) e facce esterne delle stanze verso il negozio.

    n = normale verso chi guarda (verso il negozio). Estremi = tratti realmente affacciati
    sulla zona vendita, ricavati dalla geometria corrente.
    """
    out = {}
    verts = model['envelope']['vertices']
    names = model['envelope'].get('edge_names') or [f'E{i}' for i in range(len(verts))]
    for name, (a, b) in zip(names, envelope_edges(verts)):
        ox, oy = outward(a, b, verts)
        n = (-ox, -oy)
        out[name] = _face(name, a, b, n, _clip_pieces(model, a, b, n))
    for r in rooms(model):
        rv = r['outer']
        for a, b in envelope_edges(rv):
            n = outward(a, b, rv)
            pieces = _clip_pieces(model, a, b, n)
            if not pieces:
                continue
            d = {(1, 0): '+x', (-1, 0): '-x', (0, 1): '+y', (0, -1): '-y'}[n]
            fid = f"{r['id']}:{d}"
            out[fid] = _face(fid, a, b, n, pieces)
    return out


def face_of(model, spec):
    """Faccia indicata da {'envelope': nome} oppure {'room': id, 'dir': '-x'}."""
    fs = faces(model)
    return fs[spec['envelope']] if 'envelope' in spec else fs[f"{spec['room']}:{spec['dir']}"]


def view_frame(face):
    """Riferimento del prospetto: vettore 'destra' di chi guarda la faccia e origine a sinistra."""
    nx, ny = face['n']
    rx, ry = -ny, nx  # chi guarda verso -n ha la destra in (-ny, nx)
    if face['axis'] == 'x':
        ends = [(face['lo'], face['fixed']), (face['hi'], face['fixed'])]
    else:
        ends = [(face['fixed'], face['lo']), (face['fixed'], face['hi'])]
    u0 = min(x * rx + y * ry for x, y in ends)
    return {'right': (rx, ry), 'u0': u0, 'L': face['hi'] - face['lo']}


def to_u(frame, x, y):
    rx, ry = frame['right']
    return x * rx + y * ry - frame['u0']


def host_face(model, item, tol=30):
    """Faccia su cui appoggia il retro di un oggetto (o None)."""
    x0, y0, x1, y1 = bounds(item)
    back = back_side(item)
    val = {'x0': x0, 'x1': x1, 'y0': y0, 'y1': y1}[back]
    n_need = {'y1': (0, -1), 'y0': (0, 1), 'x1': (-1, 0), 'x0': (1, 0)}[back]
    along = (x0, x1) if back.startswith('y') else (y0, y1)
    for f in faces(model).values():
        if f['n'] != n_need or abs(f['fixed'] - val) > tol:
            continue
        if min(along[1], f['hi']) - max(along[0], f['lo']) > 1:
            return f['id']
    return None


# --- Geometria dell'involucro per i render ------------------------------------

def envelope_edges(verts):
    return list(zip(verts, verts[1:] + verts[:1]))


def _signed_area(verts):
    return sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in envelope_edges(verts)) / 2


def outward(a, b, verts):
    """Normale esterna (unitaria, assi) del lato a→b del perimetro."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    nx, ny = (dy, -dx) if _signed_area(verts) > 0 else (-dy, dx)
    return (nx > 0) - (nx < 0), (ny > 0) - (ny < 0)


def rect_cells(poly):
    """Scompone un poligono ortogonale (anche con fori) in rettangoli."""
    xs = sorted({round(x) for g in _geoms(poly) for x, _ in g.exterior.coords} |
                {round(x) for g in _geoms(poly) for i in g.interiors for x, _ in i.coords})
    ys = sorted({round(y) for g in _geoms(poly) for _, y in g.exterior.coords} |
                {round(y) for g in _geoms(poly) for i in g.interiors for _, y in i.coords})
    cells = []
    for x0, x1 in zip(xs, xs[1:]):
        for y0, y1 in zip(ys, ys[1:]):
            if poly.contains(Point((x0 + x1) / 2, (y0 + y1) / 2)):
                cells.append((x0, y0, x1, y1))
    return cells


def _geoms(poly):
    return list(poly.geoms) if hasattr(poly, 'geoms') else [poly]


def model_fingerprint():
    """Impronta di modello e codice geometrico: lega i render alla geometria che li ha prodotti.

    Cambia se cambiano geometry.json, render.json o il codice dei componenti e della scena,
    anche senza cambiare la revisione.
    """
    import hashlib
    h = hashlib.sha256()
    for rel in ('config/geometry.json', 'config/render.json', 'src/components.py', 'src/model.py', 'src/render.py'):
        h.update(rel.encode())
        h.update((ROOT / rel).read_bytes().replace(b'\r\n', b'\n'))
    return h.hexdigest()[:16]
