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
