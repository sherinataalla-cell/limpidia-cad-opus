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


def room(model, rid):
    return next(r for r in model.get('rooms', []) if r['id'] == rid)


def walls_poly(model):
    return unary_union([rect_poly(bounds(w)) for w in model.get('walls', [])])


def floor_poly(model):
    """Pavimento del negozio: involucro meno foro scala (la saletta resta pavimento)."""
    return envelope_poly(model).difference(stair_poly(model))


def shop_poly(model):
    """Zona vendita: pavimento meno l'impronta esterna della saletta (tramezzi compresi)."""
    out = floor_poly(model)
    for r in model.get('rooms', []):
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


def smart_layout(model):
    """Composizione della parete smart: posizioni lungo Y e controllo dello sviluppo."""
    sw = model['smart_wall']
    p = sw['panels']
    total = p['count'] * p['width'] + (p['count'] - 1) * p['gap']
    start = sw['y1'] - sw['margin_start'] - p['width']  # vista dalla scala: da sinistra (fondo) verso destra
    # Ordine da sinistra a destra guardando la parete (verso +X): sinistra = Y alta
    ys = []
    y = sw['y1'] - sw['margin_start']
    for _ in range(p['count']):
        ys.append((y - p['width'], y))
        y -= p['width'] + p['gap']
    available = sw['y1'] - sw['y0']
    return {'total': total, 'band': sw['band']['length'], 'available': available,
            'panels': ys, 'fits': sw['margin_start'] + total <= available,
            'matches_band': total == sw['band']['length'], 'start': start}


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
