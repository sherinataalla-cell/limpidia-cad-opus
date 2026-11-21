"""Lettura del modello parametrico unico e geometria di base (unità: mm)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'config' / 'geometry.json'
OUT = ROOT / 'outputs'

STATUS_LABEL = {
    'verified': 'verificata',
    'catalog': 'da catalogo',
    'assumed': 'ipotesi',
    'pending': 'da definire',
}


def load(path=DATA):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def bounds(item):
    """Rettangolo (xmin, ymin, xmax, ymax) di un mobile o di una zona."""
    return (item['x'], item['y'], item['x'] + item['width'], item['y'] + item['depth'])


def gap(a, b):
    """Distanza libera tra due rettangoli allineati agli assi.

    Restituisce (distanza, asse). Distanza negativa = sovrapposizione.
    Se i rettangoli non si fronteggiano su nessun asse, asse = 'diag'.
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
    s = 0
    for (x0, y0), (x1, y1) in zip(vertices, vertices[1:] + vertices[:1]):
        s += x0 * y1 - x1 * y0
    return abs(s) / 2


def point_in_rect(x, y, r, tol=0):
    return r[0] - tol <= x <= r[2] + tol and r[1] - tol <= y <= r[3] + tol


def envelope_edges(verts):
    return list(zip(verts, verts[1:] + verts[:1]))


def _signed_area(verts):
    return sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in envelope_edges(verts)) / 2


def outward(a, b, verts):
    """Normale esterna (unitaria, assi) del lato a→b del perimetro."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    nx, ny = (dy, -dx) if _signed_area(verts) > 0 else (-dy, dx)
    return (nx > 0) - (nx < 0), (ny > 0) - (ny < 0)


def _on_segment(p, a, b, tol=1):
    (px, py), (ax, ay), (bx, by) = p, a, b
    if ax == bx:
        return abs(px - ax) <= tol and min(ay, by) - tol <= py <= max(ay, by) + tol
    if ay == by:
        return abs(py - ay) <= tol and min(ax, bx) - tol <= px <= max(ax, bx) + tol
    return False


def on_envelope(a, b, verts):
    """Vero se il segmento a-b giace su un lato del perimetro."""
    mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    return any(_on_segment(mid, p, q) for p, q in envelope_edges(verts))


def back_side(r, verts, zones, tol=60):
    """Lato del mobile appoggiato a un muro o a una zona (x0, x1, y0, y1)."""
    x0, y0, x1, y1 = r
    cand = {'x0': ((x0, y0), (x0, y1)), 'x1': ((x1, y0), (x1, y1)),
            'y0': ((x0, y0), (x1, y0)), 'y1': ((x0, y1), (x1, y1))}
    lines = envelope_edges(verts)
    for z in zones:
        a0, b0, a1, b1 = bounds(z)
        lines += [((a0, b0), (a1, b0)), ((a0, b1), (a1, b1)), ((a0, b0), (a0, b1)), ((a1, b0), (a1, b1))]
    best, dist = None, None
    for side, (a, b) in cand.items():
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        for p, q in lines:
            if p[0] == q[0] and a[0] == b[0] and min(p[1], q[1]) <= mid[1] <= max(p[1], q[1]):
                d = abs(mid[0] - p[0])
            elif p[1] == q[1] and a[1] == b[1] and min(p[0], q[0]) <= mid[0] <= max(p[0], q[0]):
                d = abs(mid[1] - p[1])
            else:
                continue
            if d <= tol and (dist is None or d < dist):
                best, dist = side, d
    if best is None:  # nessun appoggio: retro sul lato lungo più vicino al perimetro
        best = 'y1' if (x1 - x0) >= (y1 - y0) else 'x1'
    return best
