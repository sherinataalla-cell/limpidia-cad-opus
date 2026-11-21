"""Genera gli elaborati preliminari coordinati dal modello parametrico unico.

Uscite in `outputs/` (vedi MANIFEST.md generato):
- A01 pianta arredi quotata con ingombri d'uso (DXF + PDF A3, 1:50)
- E01 punti utenza con abaco (DXF + PDF A3, 1:50)
- F01-F04 prospetti delle pareti attrezzate (DXF + PDF A3, 1:20)
- D01 schema preliminare dei dettagli (DXF + PDF A3, 1:5)
- AB01 abaco arredi e distinta componenti, Q01 registro quote aperte, E01 registro utenze,
  proposte di layout quotate, criticita.md, MANIFEST.md

Modello in mm 1:1 nello spazio modello; la scala è solo nell'impaginazione.
"""
import datetime as dt
import hashlib
import math
import os
import random
import sys

import ezdxf
from ezdxf.enums import TextEntityAlignment

import copy
import json

from shapely.ops import nearest_points
from shapely.geometry import box, LineString, Polygon

from .model import (load, bounds, OUT, ROOT, STATUS_LABEL, weakest, placement_status, front_band, door_open_leaf,
                    smart_layout, smart_wall_geom, areas, room, faces, face_of, view_frame, to_u, product_dims,
                    envelope_edges, outward, rooms)
from .checks import run_all, clearances, write_report, LABEL as OUTCOME_LABEL
from .components import all_components, union_bounds

SHEET = (420, 297)         # A3 orizzontale, mm
WARNING = 'PRELIMINARE - NON PER CANTIERE'


def _revision_date():
    """Data stampata su tavole e registri: quella della revisione del modello.

    Viene da `revision_date` in geometry.json, accanto a `revision`, così
    rigenerare lo stesso modello in un altro giorno produce file identici.
    Se il campo manca si usa la data di oggi, come prima.
    """
    try:
        d = json.loads((ROOT / 'config' / 'geometry.json').read_text(encoding='utf-8')).get('revision_date')
    except (OSError, ValueError):
        d = None
    return d or dt.date.today().isoformat()


TODAY = _revision_date()

# DXF riproducibili: senza questa opzione ezdxf scrive a ogni salvataggio data,
# ora e GUID nuovi nell'intestazione, e i file cambiano anche a disegno identico.
# Con l'opzione l'intestazione è fissa; la data di revisione resta nel cartiglio.
ezdxf.options.write_fixed_meta_data_for_testing = True

LAYERS = [
    ('WALLS', 7, 50), ('WALLS_NEW', 8, 35), ('FACADE', 7, 25), ('DOORS', 7, 25), ('STAIR', 8, 18),
    ('ROOMS', 8, 18), ('FURNITURE_ASSUMED', 30, 35), ('FURNITURE_PENDING', 1, 35), ('FURNITURE_CATALOG', 3, 35),
    ('FURNITURE_VERIFIED', 7, 35), ('FRONT', 7, 50), ('USE', 140, 13), ('ELECTRICAL', 5, 35),
    ('DIM_ENVELOPE', 7, 18), ('DIM_FURNITURE', 8, 18), ('DIM_CLEARANCE', 6, 18), ('TEXT', 7, 18),
    ('WARNING', 1, 35), ('SHEET', 7, 25), ('DISPLAY', 8, 18), ('BRICK', 32, 18),
]
FURN_LAYER = {'assumed': 'FURNITURE_ASSUMED', 'pending': 'FURNITURE_PENDING',
              'catalog': 'FURNITURE_CATALOG', 'verified': 'FURNITURE_VERIFIED'}


def mark(*statuses):
    """Asterisco su ogni quota che dipende da almeno un dato non verificato."""
    return '' if weakest(*statuses) == 'verified' else ' *'


class Sheet:
    """Documento DXF con stile di quota e testo per una scala di stampa."""

    def __init__(self, scale):
        self.S = scale
        self.TXT = 2.5 * scale
        d = ezdxf.new('R2010', setup=True)
        d.header['$INSUNITS'] = 4
        d.header['$LWDISPLAY'] = 1
        for name, color, lw in LAYERS:
            d.layers.add(name, color=color, lineweight=lw)
        ds = d.dimstyles.duplicate_entry('EZDXF', 'LIM')
        for k, v in dict(dimtxt=2.0 * scale, dimasz=1.4 * scale, dimexo=0.8 * scale, dimexe=0.8 * scale,
                         dimgap=0.5 * scale, dimdec=0, dimtsz=0, dimtad=1, dimlunit=2, dimlfac=1, dimtih=0,
                         dimtoh=0, dimjust=0, dimtmove=2, dimclrt=0).items():
            setattr(ds.dxf, k, v)
        ds.dxf.dimblk = 'ARCHTICK'
        self.doc = d
        self.m = d.modelspace()

    def rect(self, r, layer, **kw):
        x0, y0, x1, y1 = r
        return self.m.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True,
                                     dxfattribs={'layer': layer, **kw})

    def line(self, a, b, layer, **kw):
        return self.m.add_line(a, b, dxfattribs={'layer': layer, **kw})

    def text(self, s, x, y, layer='TEXT', h=None, align=TextEntityAlignment.LEFT, rot=0):
        t = self.m.add_text(s, height=h or self.TXT, dxfattribs={'layer': layer, 'style': 'OpenSans', 'rotation': rot})
        t.set_placement((x, y), align=align)
        return t

    def dim(self, p1, p2, base, layer, angle=0, suffix=''):
        d = self.m.add_linear_dim(base=base, p1=p1, p2=p2, angle=angle, dimstyle='LIM',
                                  text='<>' + suffix, dxfattribs={'layer': layer})
        d.render()

    def hatch(self, pts, layer, pattern='SOLID', color=8, scale=1.0):
        h = self.m.add_hatch(color=color, dxfattribs={'layer': layer})
        if pattern == 'SOLID':
            h.set_solid_fill(color=color)
        else:
            h.set_pattern_fill(pattern, scale=scale, color=color)
        h.paths.add_polyline_path(pts)
        return h

    def layout(self, name, title, legend, model, limits, vp_box, notes=(), extra=None):
        """Layout A3: viewport nella scala del foglio, colonna cartiglio a destra."""
        lay = self.doc.layouts.new(name)
        lay.page_setup(size=SHEET, margins=(0, 0, 0, 0), units='mm')
        W, H = SHEET
        lay.add_lwpolyline([(10, 10), (W - 10, 10), (W - 10, H - 10), (10, H - 10)], close=True,
                           dxfattribs={'layer': 'SHEET', 'lineweight': 50})
        col = W - 10 - 105
        lay.add_line((col, 10), (col, H - 10), dxfattribs={'layer': 'SHEET'})
        xmin, ymin, xmax, ymax = limits
        bx0, by0, bx1, by1 = vp_box
        vw, vh = bx1 - bx0, by1 - by0
        lay.add_viewport(center=((bx0 + bx1) / 2, (by0 + by1) / 2), size=(vw, vh),
                         view_center_point=((xmin + xmax) / 2, (ymin + ymax) / 2), view_height=vh * self.S)

        def t(s, x, y, h=2.5, layer='TEXT'):
            e = lay.add_text(s, height=h, dxfattribs={'layer': layer, 'style': 'OpenSans'})
            e.set_placement((x, y))

        x, y = col + 5, H - 20
        t('LIMPIDIA', x, y, 6)
        t('Via Andrea Solari 3, Milano', x, y - 7, 2.8)
        y -= 17
        t(name, x, y, 9)
        y -= 7
        for ln in title:
            t(ln, x, y, 3.0)
            y -= 4.8
        y -= 3
        t('LEGENDA', x, y, 2.8)
        y -= 5.5
        for color, txt in legend:
            lay.add_line((x, y + 1), (x + 8, y + 1), dxfattribs={'color': color, 'lineweight': 50})
            t(txt, x + 11, y, 2.2)
            y -= 4.4
        y -= 2
        for ln in ['* quota non verificata: ipotesi, catalogo o da definire.',
                   'Quote derivate: stato del dato meno affidabile.',
                   f"Fonte: config/geometry.json, rev. {model['revision']}. Unità mm.",
                   'Origine: angolo vetrina sinistro; vetrina in basso.'] + list(notes):
            t(ln, x, y, 2.0)
            y -= 3.8
        yb = 58
        lay.add_line((col, yb), (W - 10, yb), dxfattribs={'layer': 'SHEET'})
        yy = yb - 6.5
        for k, v in [('Scala', f'1:{self.S} su A3 al 100%'), ('Revisione', model['revision']), ('Data', TODAY),
                     ('Stato', 'PRELIMINARE'), ('Validazione', 'da tecnico incaricato')]:
            t(k, x, yy, 2.3)
            t(v, x + 27, yy, 2.6)
            yy -= 5.6
        t(WARNING, x, 15, 3.2, 'WARNING')
        if extra:
            extra(lay, t)
        return lay


# --- Pianta ---------------------------------------------------------------------

def draw_plan(sh, model, labels=True):
    S, TXT = sh.S, sh.TXT
    v = model['envelope']['vertices']
    xs = [p[0] for p in v]
    # Involucro senza il lato vetrina (disegnato per segmenti di facciata)
    edges = list(zip(v, v[1:] + v[:1]))
    for a, b in edges:
        if a[1] == b[1] == 0:
            continue
        sh.line(a, b, 'WALLS', lineweight=70)
    for seg in model.get('facade', []):
        x0, x1 = seg['x0'], seg['x1']
        if seg['type'] == 'pier':
            sh.rect((x0, -150, x1, 0), 'WALLS')
            sh.hatch([(x0, -150), (x1, -150), (x1, 0), (x0, 0)], 'WALLS', color=250)
        elif seg['type'] == 'glazing':
            sh.line((x0, -40), (x1, -40), 'FACADE')
            sh.line((x0, -110), (x1, -110), 'FACADE')
            if labels:
                sh.text(seg['id'], (x0 + x1) / 2, -350, 'TEXT', TXT * 0.8, TextEntityAlignment.TOP_CENTER)
    # Tramezzi
    for w in model.get('walls', []):
        x0, y0, x1, y1 = bounds(w)
        sh.rect((x0, y0, x1, y1), 'WALLS_NEW')
        sh.hatch([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 'WALLS_NEW', color=8)
    # Porte: anta aperta e arco di apertura
    for op in model.get('openings', []):
        a, b = door_open_leaf(op)
        sh.line(a, b, 'DOORS', lineweight=35)
        hx, hy = op['hinge']
        sx, sy = op['swing_quadrant']
        start = math.degrees(math.atan2(0, sx)) % 360
        end = math.degrees(math.atan2(sy, 0)) % 360
        s0, s1 = (start, end) if (sx * sy) > 0 else (end, start)
        sh.m.add_arc((hx, hy), op['leaf'], s0, s1, dxfattribs={'layer': 'DOORS', 'linetype': 'DASHED', 'ltscale': 8})
        if labels:
            sh.text(op['id'], (op['x0'] + op['x1']) / 2 + (0 if op['y'] == 0 else -2.5 * S),
                    op['y'] + 1.2 * S if op['y'] > 0 else -5.5 * S, 'DOORS', TXT * 0.8,
                    TextEntityAlignment.BOTTOM_CENTER if op['y'] > 0 else TextEntityAlignment.TOP_CENTER)
    # Scala
    for z in model['room_features']:
        if z['type'] == 'zone':
            x0, y0, x1, y1 = bounds(z)
            sh.rect((x0, y0, x1, y1), 'STAIR')
            y = y0
            while y < y1 - 1:
                sh.line((x0, y), (x1, y), 'STAIR')
                y += 200
            if labels:
                sh.text('SCALA', (x0 + x1) / 2, (y0 + y1) / 2, 'STAIR', TXT, TextEntityAlignment.MIDDLE_CENTER, rot=90)
        else:
            sh.line(z['start'], z['end'], 'WALLS', lineweight=50)
    # Saletta
    for r in rooms(model):
        c = Polygon(r['net']).centroid
        sal_area = Polygon(r['net']).area / 1e6
        if labels:
            sh.text(r['id'], c.x - 300, c.y, 'ROOMS', TXT * 1.1, TextEntityAlignment.MIDDLE_CENTER)
            sh.text(f'{sal_area:.2f} m² netti{mark(r["status"])}'.replace('.', ','), c.x - 300, c.y - 1.4 * TXT, 'ROOMS', TXT,
                    TextEntityAlignment.MIDDLE_CENTER)
    if labels:
        sh.text('VIA ANDREA SOLARI - VETRINA', (min(xs) + max(xs)) / 2, -11 * S, 'TEXT', TXT, TextEntityAlignment.TOP_CENTER)
        sh.text('PARETE DI FONDO', (min(xs) + max(xs)) / 2, max(p[1] for p in v) + 19 * S, 'TEXT', TXT * 0.9, TextEntityAlignment.BOTTOM_CENTER)


def draw_furniture(sh, model, labels=True, layer_override=None):
    for f in model['furniture']:
        r = bounds(f)
        layer = layer_override or FURN_LAYER[weakest(f['status'], f.get('position_status'))]
        sh.rect(r, layer)
        # frontale: linea spessa interna sul lato d'uso
        x0, y0, x1, y1 = r
        i = 40
        fr = {'-y': ((x0 + i, y0 + i), (x1 - i, y0 + i)), '+y': ((x0 + i, y1 - i), (x1 - i, y1 - i)),
              '-x': ((x0 + i, y0 + i), (x0 + i, y1 - i)), '+x': ((x1 - i, y0 + i), (x1 - i, y1 - i))}[f['front']]
        sh.line(*fr, 'FRONT')
        if labels:
            rot = 90 if f['depth'] > f['width'] * 1.5 else 0
            sh.text(f['id'], (x0 + x1) / 2, (y0 + y1) / 2, layer, sh.TXT * 0.9, TextEntityAlignment.MIDDLE_CENTER, rot)
    for c in model.get('display_proposal', {}).get('slat_columns', []):
        sh.rect(bounds(c), 'DISPLAY')


def draw_use(sh, model):
    """Fasce d'uso ipotizzate: cassetti, sedute, anta isola (tratteggio)."""
    use = model.get('use_assumptions', {})
    furn = {f['id']: f for f in model['furniture']}
    for key, u in use.items():
        if not isinstance(u, dict) or u.get('value') is None or 'applies_to' not in u:
            continue
        for fid in u['applies_to']:
            f = furn[fid]
            if key == 'chair_zone':
                x0, y0, x1, y1 = bounds(f)
                v = u['value']
                bands = [(x0 - v, y0, x0, y1), (x1, y0, x1 + v, y1)]
            else:
                bands = [front_band(f, u['value'])]
            for b in bands:
                sh.rect(b, 'USE', linetype='DASHED', ltscale=4)
    for fid, u in [(k, v) for k, v in use.items() if isinstance(v, dict) and v.get('status') == 'pending']:
        pass


def _edge_list(model):
    verts = model['envelope']['vertices']
    names = model['envelope'].get('edge_names') or [f'E{i}' for i in range(len(verts))]
    return [(n, a, b, outward(a, b, verts)) for n, (a, b) in zip(names, envelope_edges(verts))]


def dims_plan(sh, model):
    """Quote dell'involucro, della saletta, delle porte e della scala ricavate dalla geometria corrente."""
    S = sh.S
    v = model['envelope']['vertices']
    est = mark(model['envelope']['status'])
    xs = [p[0] for p in v]
    ys = [p[1] for p in v]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    sh.dim((x0, y1), (x1, y1), (0, y1 + 13 * S), 'DIM_ENVELOPE', 0, est)
    sh.dim((x0, y0), (x0, y1), (x0 - 13 * S, 0), 'DIM_ENVELOPE', 90, est)
    for name, a, b, (ox, oy) in _edge_list(model):
        if a[1] == b[1] == y0:
            continue
        if a[1] == b[1]:
            base = (0, a[1] + oy * 7 * S) if a[1] == y1 else (0, a[1] + oy * 3 * S)
            sh.dim(a, b, base, 'DIM_ENVELOPE', 0, est)
        else:
            base = (a[0] + ox * 7 * S, 0) if a[0] in (x0, x1) else (a[0] + ox * 3 * S, 0)
            if a[0] == x0:
                continue  # lato sinistro già quotato in totale
            sh.dim(a, b, base, 'DIM_ENVELOPE', 90, est)
    for s in model.get('facade', []):
        sh.dim((s['x0'], 0), (s['x1'], 0), (0, -6 * S), 'DIM_ENVELOPE', 0, mark(s['status']))
    # Stanze: posizione, larghezza e profondità nette per tratto, spessore dei tramezzi
    for r in rooms(model):
        st = mark(r['status'])
        net = Polygon(r['net'])
        nx0, ny0, nx1, ny1 = net.bounds
        ox0, oy0 = min(p[0] for p in r['outer']), min(p[1] for p in r['outer'])
        bx = sorted({p[0] for p in r['net']})
        tops = []
        for a, b in zip(bx, bx[1:]):
            xm = (a + b) / 2
            seg = LineString([(xm, ny0), (xm, ny1 + 1)]).intersection(net)
            tops.append((a, b, seg.bounds[3]))
        ymid = ny0 + 0.55 * (min(t[2] for t in tops) - ny0)
        sh.dim((nx0, ymid), (nx1, ymid), (0, ymid), 'DIM_FURNITURE', 0, st)
        for a, b, top in tops:
            xm = a + 0.6 * (b - a)
            sh.dim((xm, ny0), (xm, top), (xm, 0), 'DIM_FURNITURE', 90, st)
        sh.dim((x0, y1), (ox0, y1), (0, y1 + 2.5 * S), 'DIM_ENVELOPE', 0, st)
        sh.dim((x1, y0), (x1, oy0), (x1 + 3 * S, 0), 'DIM_ENVELOPE', 90, st)
        sh.dim((ox0, y0), (ox0, oy0), (ox0 - 2 * S, 0), 'DIM_ENVELOPE', 90, st)
    for w in model.get('walls', []):
        if w['width'] <= 200 and w['depth'] > w['width']:
            ym = w['y'] + w['depth'] * 0.3
            sh.dim((w['x'], ym), (w['x'] + w['width'], ym), (0, ym), 'DIM_FURNITURE', 0, mark(w['status']))
    for op in model.get('openings', []):
        if op['y'] > 0:
            sh.dim((op['x0'], op['y']), (op['x1'], op['y']), (0, op['y'] - 3 * S), 'DIM_ENVELOPE', 0, mark(op['status']))
    z = next(z for z in model['room_features'] if z['id'] == 'SCALE')
    zx0, zy0, zx1, zy1 = bounds(z)
    sh.dim((zx0, zy0), (zx0, zy1), (zx0 - 5 * S, 0), 'DIM_FURNITURE', 90, mark(z['status']))
    sh.dim((zx0, 0), (zx0, zy0), (zx0 - 5 * S, 0), 'DIM_FURNITURE', 90, mark(z['status']))


def dims_furniture(sh, model):
    S = sh.S
    for f in model['furniture']:
        x0, y0, x1, y1 = bounds(f)
        st = mark(f['status'])
        fr = f['front']
        yd = y0 - 2 * S if fr != '+y' else y1 + 2 * S
        xd = x0 - 2 * S if fr == '-x' else x1 + 2 * S
        sh.dim((x0, y0), (x1, y0), (0, yd), 'DIM_FURNITURE', 0, st)
        sh.dim((x0, y0), (x0, y1), (xd, 0), 'DIM_FURNITURE', 90, st)


def _req_pairs(model):
    return {frozenset((r['a'], r['b'])) for r in model.get('requirements', [])}


def dims_clearances(sh, model):
    skip = _req_pairs(model)
    for c in clearances(model):
        a, b = c['ra'], c['rb']
        if c['mm'] is None or c['mm'] <= 1 or frozenset((c['a'], c['b'])) in skip:
            continue
        if a[2] <= b[0] or b[2] <= a[0]:
            lo, hi = (a, b) if a[2] <= b[0] else (b, a)
            yy = (max(lo[1], hi[1]) + min(lo[3], hi[3])) / 2
            if max(lo[1], hi[1]) > min(lo[3], hi[3]):
                continue
            sh.dim((lo[2], yy), (hi[0], yy), (0, yy), 'DIM_CLEARANCE', 0, f" {c['id']}" + mark(c['status']))
        elif a[3] <= b[1] or b[3] <= a[1]:
            lo, hi = (a, b) if a[3] <= b[1] else (b, a)
            xx = (max(lo[0], hi[0]) + min(lo[2], hi[2])) / 2
            if max(lo[0], hi[0]) > min(lo[2], hi[2]):
                continue
            sh.dim((xx, lo[3]), (xx, hi[1]), (xx, 0), 'DIM_CLEARANCE', 90, f" {c['id']}" + mark(c['status']))


def dims_requirements(sh, model):
    """Quota della luce netta richiesta dalla committenza fra gli ingombri completi."""
    comps = all_components(model)
    for req in model.get('requirements', []):
        z = next(z for z in model['room_features'] if z['id'] == req['a'])
        za = bounds(z)
        ub = union_bounds([c for c in comps if c['owner'] == req['b']])
        b = (ub[0], ub[1], ub[3], ub[4])
        f = next(f for f in model['furniture'] if f['id'] == req['b'])
        st = mark(z['status'], placement_status(f))
        lab = st
        note = [f"{req['id']}: luce netta scala–cassa", f"richiesta {req['min']}–{req['target'][1]} mm (committenza)"]
        ox = min(za[2], b[2]) - max(za[0], b[0])   # sovrapposizione in X
        oy = min(za[3], b[3]) - max(za[1], b[1])   # sovrapposizione in Y
        if ox > 0 and za[3] <= b[1]:
            xx = (max(za[0], b[0]) + min(za[2], b[2])) / 2
            sh.dim((xx, za[3]), (xx, b[1]), (xx + 3 * sh.S, 0), 'DIM_CLEARANCE', 90, lab)
            pos = (max(za[2], b[2]) + 150, za[3] - 500)
        elif ox > 0 and b[3] <= za[1]:
            xx = (max(za[0], b[0]) + min(za[2], b[2])) / 2
            sh.dim((xx, b[3]), (xx, za[1]), (xx + 3 * sh.S, 0), 'DIM_CLEARANCE', 90, lab)
            pos = (max(za[2], b[2]) + 150, b[3] + 300)
        elif oy > 0:
            lo, hi = (za, b) if za[2] <= b[0] else (b, za)
            yy = (max(lo[1], hi[1]) + min(lo[3], hi[3])) / 2
            sh.dim((lo[2], yy), (hi[0], yy), (0, yy), 'DIM_CLEARANCE', 0, lab)
            pos = (hi[0], min(lo[1], hi[1]) - 250)
        else:
            # nessuna sovrapposizione: distanza diagonale fra gli spigoli più vicini
            p1, p2 = nearest_points(box(*za), box(*b))
            d = sh.m.add_aligned_dim(p1=(p1.x, p1.y), p2=(p2.x, p2.y), distance=-2 * sh.S, dimstyle='LIM',
                                     text='<>' + lab, dxfattribs={'layer': 'DIM_CLEARANCE'})
            d.render()
            pos = (min(p1.x, p2.x) + 150, min(p1.y, p2.y) - 450)
        for i, line in enumerate(note):
            sh.text(line, pos[0], pos[1] - i * 2.2 * sh.S, 'DIM_CLEARANCE', 1.6 * sh.S)


def plan_limits(model, pad_mm=2000):
    xs = [v[0] for v in model['envelope']['vertices']]
    ys = [v[1] for v in model['envelope']['vertices']]
    return min(xs) - pad_mm, min(ys) - pad_mm * 0.9, max(xs) + pad_mm * 0.7, max(ys) + pad_mm * 0.6


LEGEND_A01 = [(7, 'Muratura esistente (ipotesi)'), (8, 'Tramezzo proposto 10 cm'), (30, 'Mobile, misure ipotesi'),
              (3, 'Mobile da catalogo'), (1, 'Mobile da definire'), (140, "Ingombro d'uso ipotizzato"),
              (6, 'Distanza funzionale (FPxx) e luce richiesta')]
LEGEND_E01 = [(7, 'Muratura esistente (ipotesi)'), (8, 'Tramezzo proposto'), (30, 'Ingombro mobili'),
              (5, 'Punto utenza: X/Y ipotesi, Z da rilevare')]


def build_a01(model, code='A01', title=None, notes=None):
    sh = Sheet(50)
    draw_plan(sh, model)
    draw_furniture(sh, model)
    draw_use(sh, model)
    dims_plan(sh, model)
    dims_furniture(sh, model)
    dims_clearances(sh, model)
    dims_requirements(sh, model)
    res = [r for r in run_all(model) if (r['cat'] in ('requisiti', 'uso', 'porte', 'ingombri', 'decisioni') and r['outcome'] != 'OK')
           or (r['cat'] == 'accostamento' and r['outcome'] == 'CONFLITTO')]

    def table(lay, t):
        y = 112
        t("REQUISITI, INGOMBRI D'USO E VERIFICHE (dettaglio in outputs/criticita.md)", 15, y, 2.6)
        y -= 5
        for r in res:
            t(r['id'], 15, y, 1.7)
            t(OUTCOME_LABEL[r['outcome']], 52, y, 1.7)
            t(r['text'][:135], 104, y, 1.7)
            y -= 3.2
            if y < 14:
                break
    sh.layout(code, title or ['Pianta arredi quotata', "con ingombri d'uso", 'Piano terra'], LEGEND_A01, model,
              plan_limits(model), (12, 118, 302, 285),
              notes=notes or ["Fasce d'uso: ipotesi di screening,", 'non misure di prodotto.',
                              'Luce scala-cassa: richiesta committenza.'], extra=table)
    return sh.doc


def build_e01(model):
    sh = Sheet(50)
    draw_plan(sh, model, labels=True)
    draw_furniture(sh, model, labels=True, layer_override='FURNITURE_ASSUMED')
    dims_plan(sh, model)
    for p in model['electrical_points']:
        if p['x'] is None:
            continue
        r = 1.6 * sh.S
        sh.m.add_circle((p['x'], p['y']), r, dxfattribs={'layer': 'ELECTRICAL', 'lineweight': 35})
        sh.line((p['x'] - r, p['y']), (p['x'] + r, p['y']), 'ELECTRICAL')
        if 'dati' in p['kinds']:
            sh.line((p['x'], p['y'] - r), (p['x'], p['y'] + r), 'ELECTRICAL')
        if 'LED' in p['kinds']:
            sh.m.add_circle((p['x'], p['y']), r * 0.45, dxfattribs={'layer': 'ELECTRICAL'})
        sh.text(p['id'], p['x'] + 2.2 * sh.S, p['y'] + 1.2 * sh.S, 'ELECTRICAL', sh.TXT)

    def table(lay, t):
        y = 112
        t('ABACO UTENZE (stessi ID della pianta; registro completo in E01_registro_utenze.md; circuiti e protezioni a cura del tecnico)', 15, y, 2.2)
        y -= 4.5
        t('ID     Servizio / mobile                                      Tipo           X / Y (stato)        Z           Q.tà', 15, y, 1.8)
        y -= 3.6
        for p in model['electrical_points']:
            xy = f"{p['x'] if p['x'] is not None else '-'} / {p['y'] if p['y'] is not None else '-'} ({STATUS_LABEL[p['xy_status']]})"
            z = 'DA RILEVARE' if p['z'] is None else f"{p['z']} ({STATUS_LABEL[p['z_status']]})"
            t(f"{p['id']:<6} {p['service'][:54]:<54} {'/'.join(p['kinds']):<14} {xy:<20} {z:<11} {p['quantity']}", 15, y, 1.75)
            y -= 3.0
            t(f"         supporto: {p['support']}; accesso: {p['access']}; alimentatore: {p['driver']}; percorso: {p['route']}"[:200],
              15, y, 1.5)
            y -= 3.3
    sh.layout('E01', ['Punti utenza energia/dati', 'e alimentazioni LED', 'Piano terra'], LEGEND_E01, model,
              plan_limits(model), (12, 118, 302, 285),
              notes=['Simbolo: cerchio energia, croce dati,', 'cerchio interno alimentazione LED.',
                     'Le luci dei render non sono potenze.'], extra=table)
    return sh.doc


# --- Prospetti (dalla faccia di parete del modello) -------------------------------------------

KIND_STYLE = {'body': ('FURN', None), 'plinth': ('FURN', None), 'top': ('FURN', None), 'led': ('DISPLAY', 2),
              'shelf': ('DISPLAY', 8), 'cubby': ('DISPLAY', 40), 'slat': ('DISPLAY', 40), 'mirror': ('DISPLAY', 5),
              'frame': ('DISPLAY', 7), 'image': ('DISPLAY', 254), 'label': ('DISPLAY', 7), 'logo': ('TEXT', 1),
              'cladding': ('BRICK', 32)}


def elevation_geometry(model, spec):
    """Faccia, riferimento di vista e componenti proiettati (u0, z0, u1, z1) di un prospetto."""
    face = face_of(model, spec['host'])
    fr = view_frame(face)
    items = []
    for c in all_components(model):
        if c['host'] != face['id']:
            continue
        x0, y0, z0, x1, y1, z1 = c['box']
        us = sorted((to_u(fr, x0, y0), to_u(fr, x1, y1)))
        items.append(dict(c, u=(us[0], z0, us[1], z1)))
    return face, fr, items


def build_elevation(model, spec):
    sh = Sheet(20)
    S, TXT = sh.S, sh.TXT
    H = model['ceiling']['height']
    face, fr, items = elevation_geometry(model, spec)
    L = fr['L']
    sh.line((0, 0), (L, 0), 'WALLS', lineweight=70)
    sh.line((0, H), (L, H), 'WALLS', linetype='DASHED', ltscale=6)
    sh.line((0, 0), (0, H), 'WALLS', lineweight=50)
    sh.line((L, 0), (L, H), 'WALLS', lineweight=50)
    sh.text(f"soffitto {H}{mark(model['ceiling']['status'])} ({model['ceiling']['source']}, ribassamenti da rilevare)", 100, H + 60,
            'TEXT', TXT * 0.8)
    sh.dim((L, 0), (L, H), (L + 6 * S, 0), 'DIM_ENVELOPE', 90, mark(model['ceiling']['status']))
    sh.dim((0, 0), (L, 0), (0, -9 * S), 'DIM_ENVELOPE', 0, mark(model['envelope']['status']))
    furn = {f['id']: f for f in model['furniture']}
    order = ['cladding', 'image', 'frame', 'body', 'plinth', 'top', 'shelf', 'cubby', 'slat', 'mirror', 'label', 'led', 'logo']
    for c in sorted(items, key=lambda c: order.index(c['kind']) if c['kind'] in order else 99):
        u0, z0, u1, z1 = c['u']
        lay, color = KIND_STYLE.get(c['kind'], ('DISPLAY', 8))
        if lay == 'FURN':
            f = furn[c['owner']]
            lay = FURN_LAYER[weakest(f['status'], f.get('position_status'))]
        if c['kind'] == 'cladding':
            sh.hatch([(u0, z0), (u1, z0), (u1, z1), (u0, z1)], 'BRICK', 'BRICK', color=32, scale=12)
            continue
        if c['kind'] == 'image':
            sh.hatch([(u0, z0), (u1, z0), (u1, z1), (u0, z1)], 'DISPLAY', color=254)
            sh.text('IMMAGINE DA FORNIRE', (u0 + u1) / 2, (z0 + z1) / 2, 'TEXT', TXT * 0.5, TextEntityAlignment.MIDDLE_CENTER)
            continue
        kw = {'color': color} if color and lay in ('DISPLAY', 'TEXT') else {}
        if c['kind'] == 'led':
            sh.line((u0, (z0 + z1) / 2), (u1, (z0 + z1) / 2), 'DISPLAY', color=2, lineweight=35)
            continue
        sh.rect((u0, z0, u1, z1), lay, **kw)
        if c['kind'] == 'frame' and c.get('title'):
            sh.text(c['title'], (u0 + u1) / 2, z1 - 70, 'TEXT', TXT * 0.6, TextEntityAlignment.MIDDLE_CENTER)
        if c['kind'] == 'label' and c.get('text'):
            sh.text(c['text'][:28], (u0 + u1) / 2, (z0 + z1) / 2, 'TEXT', TXT * 0.32, TextEntityAlignment.MIDDLE_CENTER)
        if c['kind'] == 'logo':
            sh.text('marchio ufficiale (assets/brand)', (u0 + u1) / 2, (z0 + z1) / 2, 'TEXT', TXT * 0.6,
                    TextEntityAlignment.MIDDLE_CENTER)
    # quote per mobile: ingombro e altezza
    elec_u = []
    for pnt in model['electrical_points']:
        if pnt['x'] is None:
            continue
        along = pnt['x'] if face['axis'] == 'x' else pnt['y']
        other = pnt['y'] if face['axis'] == 'x' else pnt['x']
        if abs(other - face['fixed']) <= 30 and face['lo'] - 1 <= along <= face['hi'] + 1:
            elec_u.append(to_u(fr, pnt['x'], pnt['y']))
    owners = {}
    for c in items:
        owners.setdefault(c['owner'], []).append(c['u'])
    for own, us in owners.items():
        u0, u1 = min(u[0] for u in us), max(u[2] for u in us)
        z1 = max(u[3] for u in us)
        if own in furn:
            f = furn[own]
            lay = FURN_LAYER[weakest(f['status'], f.get('position_status'))]
            sh.text(own, (u0 + u1) / 2, z1 + 60, lay, TXT, TextEntityAlignment.BOTTOM_CENTER)
            sh.dim((u0, 0), (u1, 0), (0, -3 * S), 'DIM_FURNITURE', 0, mark(f['status']))
            # quota altezza a sinistra; a destra se a sinistra c'è un punto utenza
            busy = any(abs(eu - (u0 - 2 * S)) < 4 * S for eu in elec_u)
            hx = u1 + 4 * S if busy else u0 - 2 * S
            sh.dim((u1 if busy else u0, 0), (u1 if busy else u0, f['height']), (hx, 0), 'DIM_FURNITURE', 90,
                   mark(f['status'], f.get('height_status')))
        elif own.startswith('ESP_'):
            dp = model['display_proposal']
            zs = sorted({round(c['u'][1]) for c in items if c['owner'] == own and c['kind'] == 'shelf'})
            st = mark(dp['status'])
            sh.dim((u1, 0), (u1, zs[0]), (u1 + 2 * S, 0), 'DIM_FURNITURE', 90, st)
            for za, zb in zip(zs, zs[1:]):
                sh.dim((u1, za), (u1, zb), (u1 + 2 * S, 0), 'DIM_FURNITURE', 90, st)
        elif own.startswith('LS'):
            sm = model['display_proposal']['slat_mirror']
            col = next(c for c in model['display_proposal']['slat_columns'] if c['id'] == own)
            cb = bounds(col)
            u0, u1 = sorted((to_u(fr, cb[0], cb[1]), to_u(fr, cb[2], cb[3]))) if face['axis'] == 'x' else \
                sorted((to_u(fr, cb[0], cb[1]), to_u(fr, cb[0], cb[3])))
            sh.text(f"{own} listelli + specchio", u0 - 60, z1 - 150, 'DISPLAY', TXT * 0.7, TextEntityAlignment.BOTTOM_RIGHT)
            sh.dim((u0, 0), (u1, 0), (0, -3 * S), 'DIM_FURNITURE', 0, mark(model['display_proposal']['status']))
            sh.dim((u1, z1), (u1, H), (u1 + 2 * S, 0), 'DIM_FURNITURE', 90, f" (soffitto - {sm['top_gap_from_ceiling']})" + mark('assumed'))
    # Parete smart: catene di quote dai telai reali
    frames = sorted([c['u'] for c in items if c['owner'] == 'SMART' and c['kind'] == 'frame'])
    if frames:
        sw = model['smart_wall']
        p = sw['panels']
        L_ = smart_layout(model)
        zt = frames[0][3]
        pts = [0] + [v for f_ in frames for v in (f_[0], f_[2])] + [L]
        for a, b in zip(pts, pts[1:]):
            if b - a > 1:
                sh.dim((a, zt), (b, zt), (0, zt + 4 * S), 'DIM_FURNITURE', 0, mark(p['status']))
        sh.dim((frames[0][0], 0), (frames[-1][2], 0), (0, -3 * S), 'DIM_FURNITURE', 0,
               f" telai (fascia S2: {sw['band']['length']})" + mark(sw['band']['status']))
        sh.dim(((frames[0][0] + frames[0][2]) / 2, zt), ((frames[1][0] + frames[1][2]) / 2, zt), (0, zt + 8 * S),
               'DIM_FURNITURE', 0, ' interasse' + mark(p['status']))
        lab = next(c['u'] for c in items if c['kind'] == 'label')
        shl = next(c['u'] for c in items if c['owner'] == 'SMART' and c['kind'] == 'shelf')
        for za, zb in ((0, lab[1]), (lab[1], shl[1]), (shl[1], frames[0][1]), (frames[0][1], zt)):
            sh.dim((L, za), (L, zb), (L + 2 * S, 0), 'DIM_FURNITURE', 90, mark(p['status']))
        sh.text(f"telaio esterno {L_['frame']}, immagine {L_['image']}, distanza libera {L_['clear_gap']}, interasse {L_['interaxis']}",
                100, H - 450, 'TEXT', TXT * 0.8)
        sh.text(f"rivestimento mattoni sp. {sw['cladding']['thickness']}{mark(sw['cladding']['status'])}", 100, H - 250, 'TEXT', TXT * 0.8)
    # Porte sulla faccia
    for op in model.get('openings', []):
        if face['axis'] == 'x' and abs(op['y'] - face['fixed']) <= 1 and op['x0'] >= face['lo'] - 1 and op['x1'] <= face['hi'] + 1:
            u0, u1 = sorted((to_u(fr, op['x0'], op['y']), to_u(fr, op['x1'], op['y'])))
            for a, b in (((u0, 0), (u0, 2100)), ((u1, 0), (u1, 2100)), ((u0, 2100), (u1, 2100))):
                sh.line(a, b, 'DOORS', linetype='DASHED', ltscale=6)
            sh.text(f"{op['id']} vano {op['opening_width']}{mark(op['status'])}", (u0 + u1) / 2, 2260, 'DOORS', TXT * 0.75,
                    TextEntityAlignment.BOTTOM_CENTER)
            sh.text('altezza DA RILEVARE (simbolo)', (u0 + u1) / 2, 2160, 'DOORS', TXT * 0.75, TextEntityAlignment.BOTTOM_CENTER)
            sh.dim((u0, 0), (u1, 0), (0, -3 * S), 'DIM_FURNITURE', 0, mark(op['status']))
    # Utenze sulla faccia: Z nota disegnata alla quota, altrimenti "da rilevare"
    for pnt in model['electrical_points']:
        if pnt['x'] is None:
            continue
        along = pnt['x'] if face['axis'] == 'x' else pnt['y']
        other = pnt['y'] if face['axis'] == 'x' else pnt['x']
        if abs(other - face['fixed']) <= 30 and face['lo'] - 1 <= along <= face['hi'] + 1:
            u = to_u(fr, pnt['x'], pnt['y'])
            if pnt['z'] is not None:
                sh.m.add_circle((u, pnt['z']), 40, dxfattribs={'layer': 'ELECTRICAL'})
                sh.text(f"{pnt['id']} Z {pnt['z']}{mark(pnt['z_status'])}", u + 60, pnt['z'], 'ELECTRICAL', TXT * 0.75)
            else:
                # solo posizione lungo la parete: tacca a pavimento, nessuna quota Z disegnata
                sh.line((u, 0), (u, 250), 'ELECTRICAL')
                sh.line((u - 40, 250), (u, 300), 'ELECTRICAL')
                sh.line((u + 40, 250), (u, 300), 'ELECTRICAL')
                sh.text(f"{pnt['id']} Z DA RILEVARE", u + 40, 330, 'ELECTRICAL', TXT * 0.75, rot=90)
    sh.text(f"faccia {face['id']}: lato sinistro guardando la parete", 0, -14 * S, 'TEXT', TXT * 0.7)
    lim = (-12 * S, -18 * S, L + 14 * S, H + 6 * S)
    sh.layout(spec['code'], spec['title'] + [f"faccia {face['id']}"],
              [(7, 'Muratura / tramezzo'), (30, 'Mobile, misure ipotesi'), (8, 'Mensole, listelli (proposta)'),
               (2, 'Linee LED (asse)'), (5, 'Utenza'), (32, 'Rivestimento mattoni')], model, lim, (14, 14, 302, 285),
              notes=['Componenti dalla geometria comune', '(src/components.py): stessi solidi del 3D.',
                     'Altezze dei mobili: ipotesi da schede.', 'Mensole e listelli: proposta da S4.'])
    return sh.doc


def elevation_name(spec):
    return f"{spec['code']}_prospetto_{'_'.join(spec['title'][0].split()[2:]).lower()}"


# --- D01: schema preliminare dei dettagli --------------------------------------------------

def build_d01(model):
    """Dettagli schematici a 1:10, disegnati dagli stessi componenti del modello 3D (nessuna quota propria)."""
    sh = Sheet(10)
    TXT = sh.TXT
    dp = model['display_proposal']
    D, TH, cb, sl, led = dp['shelf_depth'], dp['shelf_thickness'], dp['cubby'], dp['shelf_led'], dp['drawer_led']
    sm = dp['slat_mirror']
    P = model['furniture_parts']['drawers']
    st = mark(dp['status'])
    comps = all_components(model)

    def title(x, y, s):
        sh.text(s, x, y, 'TEXT', TXT * 0.8)

    def note(x, y, s):
        sh.text(s, x, y, 'TEXT', TXT * 0.55)

    # D01.1 (in basso a destra) sezione mensola a parete con profilo LED sotto
    ox, oy = 2300, 500
    sh.line((ox, oy - 150), (ox, oy + 450), 'WALLS', lineweight=70)
    sh.rect((ox - D, oy + 150, ox, oy + 150 + TH), 'DISPLAY')
    sh.rect((ox - D + sl['inset'], oy + 150 - sl['height'], ox - sl['inset'], oy + 150), 'DISPLAY', color=2)
    sh.rect((ox - 40, oy + 60, ox, oy + 150), 'DISPLAY', linetype='DASHED', ltscale=1)
    sh.dim((ox - D, oy + 150 + TH), (ox, oy + 150 + TH), (0, oy + 150 + TH + 60), 'DIM_FURNITURE', 0, st)
    sh.dim((ox - D, oy + 150), (ox - D, oy + 150 + TH), (ox - D - 60, 0), 'DIM_FURNITURE', 90, st)
    note(ox - D - 150, oy - 20, f"LED sotto mensola: profilo h {sl['height']}, rientro {sl['inset']} (ipotesi)")
    note(ox - D - 150, oy - 70, 'sezione profilo da scheda (pending)')
    note(ox - D - 150, oy - 120, 'staffa/fissaggio: DA DEFINIRE (carico e tasselli)')
    title(ox - D - 150, oy - 260, 'D01.1 Sezione mensola, LED sotto mensola')
    # D01.2 (in alto a sinistra) nodo mensola / cubotto: vista frontale ricavata dai componenti di C1
    cub = [c for c in comps if c['owner'] == 'ESP_C1' and c['kind'] == 'cubby']
    if cub:
        cx0 = min(c['box'][0] for c in cub); cx1 = max(c['box'][3] for c in cub)
        cz0 = min(c['box'][2] for c in cub); cz1 = max(c['box'][5] for c in cub)
        wx0, wx1, wz0, wz1 = cx0 - 500, cx1 + 150, cz0 - 400, cz1 + 300
        ox, oy = 150 - wx0, 1650 - wz0
        near = [c for c in comps if c['owner'] == 'ESP_C1' and c['box'][3] > wx0 and c['box'][0] < wx1
                and c['box'][5] > wz0 and c['box'][2] < wz1]
        for c in near:
            x0, _, z0, x1, _, z1 = c['box']
            x0, x1 = max(x0, wx0), min(x1, wx1)
            if c['kind'] == 'led':
                sh.line((ox + x0, oy + (z0 + z1) / 2), (ox + x1, oy + (z0 + z1) / 2), 'DISPLAY', color=2, lineweight=35)
            else:
                sh.rect((ox + x0, oy + z0, ox + x1, oy + z1), 'DISPLAY', **({'color': 40} if c['kind'] == 'cubby' else {}))
        sh.line((ox + wx0, oy + wz0), (ox + wx0, oy + wz1), 'TEXT', linetype='DASHED', ltscale=2)
        sh.dim((ox + cx0, oy + cz1), (ox + cx1, oy + cz1), (0, oy + cz1 + 80), 'DIM_FURNITURE', 0, st)
        sh.dim((ox + cx1, oy + cz0), (ox + cx1, oy + cz1), (ox + cx1 + 80, 0), 'DIM_FURNITURE', 90, st)
        sup = [c for c in near if c['kind'] == 'shelf' and c['box'][2] < cz0 + 1 and c['box'][5] >= cz0 - 1]
        if sup:
            sh.dim((ox + cx0 - 200, oy + sup[0]['box'][2]), (ox + cx0 - 200, oy + sup[0]['box'][2] + 300),
                   (ox + cx0 - 260, 0), 'DIM_FURNITURE', 90, ' passo mensole' + st)
        note(150, 1650 - 120, f"cubotto aperto rovere {cb['size']} x {cb['size']}, prof. {cb['depth']}, pannelli {cb['board']}: "
             'appoggiato sulla mensola inferiore,')
        note(150, 1650 - 170, 'mensola superiore interrotta sul fianco del cubotto (giunto proposto, da validare)')
        note(150, 1650 - 220, 'passaggio cavi LED dal retro: da definire. Geometria = componenti ESP_C1 del modello')
        title(150, 1650 - 330, 'D01.2 Nodo mensola / cubotto C1 (vista frontale, dai componenti)')
    # D01.3 (in basso a sinistra) sezione cassettiera con LED in fresata e vano driver
    ox, oy = 250, 300
    h = next(f['height'] for f in model['furniture'] if f['id'] == 'C1')
    d = next(f['depth'] for f in model['furniture'] if f['id'] == 'C1')
    sh.rect((ox, oy + P['plinth_height'], ox + d, oy + h), 'FURNITURE_ASSUMED')
    sh.rect((ox + P['plinth_inset'], oy, ox + d - P['plinth_inset'], oy + P['plinth_height']), 'FURNITURE_ASSUMED')
    for i, fr_ in enumerate(led['axes_fraction']):
        zz = oy + h * fr_
        sh.rect((ox + d - led['groove_depth'], zz - led['height'] / 2, ox + d, zz + led['height'] / 2), 'DISPLAY', color=2)
        sh.dim((ox + d, oy), (ox + d, zz), (ox + d + 80 + 120 * i, 0), 'DIM_FURNITURE', 90, ' asse' + mark(led['status']))
    sh.rect((ox + 40, oy + P['plinth_height'] + 20, ox + 220, oy + P['plinth_height'] + 140), 'DISPLAY', linetype='DASHED', ltscale=1)
    sh.line((ox, oy - 40), (ox, oy + h + 40), 'WALLS', lineweight=70)
    sh.dim((ox, oy + h), (ox + d, oy + h), (0, oy + h + 60), 'DIM_FURNITURE', 0, mark('assumed'))
    note(ox + d + 400, oy + h - 40, f"LED in fresata {led['groove_depth']} mm, h {led['height']},")
    note(ox + d + 400, oy + h - 90, f"assi a {led['axes_fraction'][0]:.2f} e {led['axes_fraction'][1]:.2f} H (si adattano a H)")
    note(ox + d + 400, oy + h - 140, 'vano driver ispezionabile: posizione indicativa,')
    note(ox + d + 400, oy + h - 190, 'dimensioni e aerazione da scheda (pending)')
    note(ox + d + 400, oy + h - 240, 'passaggio cavi dal retro: da definire')
    title(ox - 150, oy - 230, f"D01.3 Sezione cassettiera C1 H {h} (ipotesi): LED in fresata")
    # D01.4 (in alto a destra) sezione orizzontale colonna listelli + specchio, dai componenti LS1
    lsc = [c for c in comps if c['owner'] == 'LS1']
    col = next(c for c in dp['slat_columns'] if c['id'] == 'LS1')
    bx0, by1 = col['x'], col['y'] + col['depth']
    ox, oy = 1850, 2150
    for c in lsc:
        x0, y0, _, x1, y1, _ = c['box']
        sh.rect((ox + x0 - bx0, oy + by1 - y1, ox + x1 - bx0, oy + by1 - y0), 'DISPLAY',
                color={'slat': 40, 'frame': 7, 'mirror': 5}.get(c['kind'], 8))
    W = col['width']
    sh.line((ox - 40, oy), (ox + W + 40, oy), 'WALLS', lineweight=70)
    sh.dim((ox, oy), (ox + W, oy), (0, oy - 60), 'DIM_FURNITURE', 0, st)
    dep = sm['slat_depth'] + sm['mirror_plate'] + sm['mirror_thickness']
    sh.dim((ox + W, oy), (ox + W, oy + dep), (ox + W + 60, 0), 'DIM_FURNITURE', 90, st)
    note(ox, oy + 120, f"listelli {sm['slat']} x {sm['slat_depth']}, distanza {sm['slat_gap']}, centrati nella colonna;")
    note(ox, oy + 170, f"specchio {sm['mirror_width']} x {sm['mirror_height']} su piastra: fissaggio DA DEFINIRE")
    title(ox, oy - 250, 'D01.4 Colonna listelli + specchio LS1 (sezione orizzontale)')
    lim = (0, 0, 2900, 2750)
    sh.layout('D01', ['Schema preliminare dettagli', 'mensole, cubotti, LED, listelli'],
              [(8, 'Mensole e listelli (proposta)'), (40, 'Rovere'), (2, 'Profili LED'), (5, 'Specchio')], model, lim,
              (14, 14, 302, 285),
              notes=['SCHEMA PRELIMINARE: non esecutivo.', 'Mancano schede LED, driver, carichi,',
                     'staffe e fissaggi: restano pending.', 'Geometria dai componenti comuni.'])
    return sh.doc


# --- Esportazione --------------------------------------------------------------------

def _pdf_string_end(data, i):
    """Fine (esclusa) della stringa PDF che inizia in i: esadecimale <...> o letterale (...)."""
    if data[i:i + 1] == b'<':
        return data.index(b'>', i) + 1
    depth, j = 0, i
    while j < len(data):
        c = data[j:j + 1]
        if c == b'\\':
            j += 2
            continue
        if c == b'(':
            depth += 1
        elif c == b')':
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    raise ValueError('stringa PDF non chiusa')


def _stable_pdf_id(data):
    """Sostituisce l'/ID casuale del PDF con un'impronta del contenuto.

    PyMuPDF scrive un /ID nuovo a ogni salvataggio, a volte come stringa esadecimale <...>
    e a volte come stringa letterale (...): si accettano entrambe le forme. L'/ID sta nel
    trailer, dopo la tabella xref, quindi cambiarne la lunghezza non sposta gli offset.
    """
    k = data.rfind(b'/ID[')
    if k < 0:
        return data
    s1 = k + 4
    e1 = _pdf_string_end(data, s1)
    e2 = _pdf_string_end(data, e1)
    if data[e2:e2 + 1] != b']':
        return data
    h = b'<' + hashlib.md5(data[:k] + data[e2 + 1:]).hexdigest().upper().encode() + b'>'
    return data[:s1] + h + h + data[e2:]


def export_pdf(doc, layout_name, path):
    from ezdxf.addons.drawing import Frontend, RenderContext, pymupdf, layout, config
    lay = doc.layouts.get(layout_name)
    # ezdxf sposta di pochissimo, a caso, le linee dei retini (mattoni) per evitare
    # artefatti: con un seme fisso lo spostamento è sempre lo stesso e il PDF anche.
    random.seed(0)
    backend = pymupdf.PyMuPdfBackend()
    cfg = config.Configuration(background_policy=config.BackgroundPolicy.WHITE,
                               color_policy=config.ColorPolicy.COLOR, lineweight_scaling=1.0)
    Frontend(RenderContext(doc), backend, config=cfg).draw_layout(lay, finalize=True)
    page = layout.Page(*SHEET, layout.Units.mm)
    path.write_bytes(_stable_pdf_id(backend.get_pdf_bytes(page, settings=layout.Settings(scale=1, fit_page=False))))
    return path


# --- Registri ----------------------------------------------------------------------

def _room_dims(r):
    net = Polygon(r['net'])
    nx0, ny0, nx1, ny1 = net.bounds
    bx = sorted({p[0] for p in r['net']})
    depths = []
    for a, b in zip(bx, bx[1:]):
        seg = LineString([((a + b) / 2, ny0), ((a + b) / 2, ny1 + 1)]).intersection(net)
        depths.append(round(seg.bounds[3] - ny0))
    return round(nx1 - nx0), depths, net.area / 1e6


def q01(model):
    """Registro di tutte le quote non verificate e dei dati mancanti."""
    rows = []

    def add(ref, what, value, status, source):
        if status != 'verified':
            rows.append((ref, what, value, STATUS_LABEL.get(status, status), source))
    e = model['envelope']
    for name, a, b, _ in _edge_list(model):
        add(name, f'lato {a} → {b}', f"{abs(b[0]-a[0]) + abs(b[1]-a[1])}", e['status'], e['source'])
    add('ENVELOPE', 'spessori dei muri esistenti, diagonali, fuori squadra', '-', 'pending', 'rilievo')
    add('SOFFITTO', 'quota interna del soffitto e ribassamenti', model['ceiling']['height'], model['ceiling']['status'], model['ceiling']['source'])
    for s in model.get('facade', []):
        add(s['id'], f"facciata {s['type']} x {s['x0']}–{s['x1']}", s['x1'] - s['x0'], s['status'], s['source'])
    for w in model.get('walls', []):
        add(w['id'], f"{w['desc']}: x {w['x']}, y {w['y']}, {w['width']} × {w['depth']}", '-', w['status'], w['source'])
    for op in model.get('openings', []):
        add(op['id'], f"{op['desc']}: vano {op['x0']}–{op['x1']}, luce {op['clear_width'] or 'da rilevare'}, verso", op['opening_width'], op['status'], op['source'])
        add(op['id'], 'altezza del vano, spallette, serramento', '-', 'pending', 'rilievo')
    for r in rooms(model):
        wn, deps, a = _room_dims(r)
        add(r['id'], 'dimensioni nette (dal poligono netto)', f"{wn} × {' / '.join(map(str, deps))}; {a:.2f} m²", r['status'], r['source'])
    for z in model['room_features']:
        add(z['id'], 'posizione e dimensioni' + (' (spessore e sporgenza corrimano)' if z['type'] == 'line' else ''), '-', z['status'], z['source'])
    add('SCALE', 'fine della scala lato fondo, parapetto in testa: confronto P00 (y 1450–3850) / S1 (y 1500–3900)', '3900', 'assumed',
        'S1 scelta in P01; da rilevare (determina la luce scala-cassa)')
    for f in model['furniture']:
        pdm = product_dims(f)
        add(f['id'], 'prodotto L × P (lungo il fronte × profondità)', f"{pdm['L']} × {pdm['P']}", f['status'], f['source'])
        add(f['id'], 'posizione nel locale', f"x {f['x']}, y {f['y']}, fronte {f['front']}", f['position_status'], f['source'])
        add(f['id'], 'altezza', f['height'], f['height_status'], 'scheda prodotto da archiviare')
    fp = model.get('furniture_parts', {})
    if fp:
        add('PARTI', 'zoccoli, top e pannelli dei mobili (spessori)', 'vedi furniture_parts', fp['status'], fp['source'])
    for k, u in model.get('use_assumptions', {}).items():
        if isinstance(u, dict) and 'status' in u:
            add('USO', f"{k}: {u.get('note', '')}", u.get('value') if u.get('value') is not None else '-', u['status'], u['source'])
    for req in model.get('requirements', []):
        rows.append((req['id'], f"requisito committenza: {req['measure']}", f"≥ {req['min']} (obiettivo {req['target'][0]}–{req['target'][1]})",
                     'requisito', req['source']))
    sw = model.get('smart_wall')
    if sw:
        L_ = smart_layout(model)
        p = sw['panels']
        add('SMART', 'fascia smart', sw['band']['length'], sw['band']['status'], sw['band']['source'])
        add('SMART', 'telaio esterno / immagine / distanza libera / interasse / altezza / base',
            f"{L_['frame']} / {L_['image']} / {L_['clear_gap']} / {L_['interaxis']} / {p['height']} / {p['bottom']}", p['status'], p['source'])
        add('SMART', 'rivestimento mattoni: spessore e fissaggio', sw['cladding']['thickness'], sw['cladding']['status'], sw['cladding']['source'])
        add('SMART', 'immagini dei pannelli', '-', sw['images']['status'], sw['images']['note'])
    dp = model.get('display_proposal')
    if dp:
        add('ESPOSIZIONE', 'livelli mensole (base), cubotti, listelli e specchi', str(dp['shelf_levels']), dp['status'], dp['source'])
        add('ESPOSIZIONE', 'sommità listelli', f"soffitto - {dp['slat_mirror']['top_gap_from_ceiling']}", dp['status'], dp['source'])
        add('ESPOSIZIONE', 'linee LED cassettiere (assi, frazione di H)', str(dp['drawer_led']['axes_fraction']), dp['drawer_led']['status'],
            dp['drawer_led']['source'])
    for p in model['electrical_points']:
        add(p['id'], f"posizione X/Y ({p['service']})", f"{p['x']}, {p['y']}", p['xy_status'], 'S0')
        add(p['id'], 'quota Z, quantità, supporto, alimentatore, percorso', p['z'] if p['z'] is not None else '-', p['z_status'], 'elettricista')
    for d in model.get('declared_areas', []):
        add(d['id'], f"superficie dichiarata: {d['definition']}", d['value_m2'], d['status'], d['source'])
    conflicts = [r for r in run_all(model) if r['outcome'] in ('CONFLITTO', 'NON_VERIFICABILE')]
    lines = ['# Q01 - Registro quote aperte, conflitti e decisioni', '',
             f"Revisione {model['revision']}, generato il {TODAY} da config/geometry.json. Ogni riga resta aperta finché il dato non è "
             "inserito con stato `verified` e fonte (rilievo, scheda firmata).", '',
             '| Rif. | Dato | Valore attuale | Stato | Fonte |', '| --- | --- | --- | --- | --- |']
    lines += [f'| {a} | {b} | {c} | {d} | {e} |' for a, b, c, d, e in rows]
    lines += ['', '## Conflitti e verifiche non eseguibili', '', '| ID | Esito | Dettaglio |', '| --- | --- | --- |']
    lines += [f"| {r['id']} | {OUTCOME_LABEL[r['outcome']]} | {r['text']} |" for r in conflicts]
    lines += ['', '## Decisioni da prendere (alternative quotate in proposte_layout.md)', '',
              '- Luce scala–cassa ≥ 1000 mm richiesta: con la scala fino a y 3900 e la cassa sul muro sinistro non è ottenibile; scegliere fra le alternative.',
              '- Lato operatore della cassa e prodotto reale (oggi segnaposto 1200 × 600).',
              '- C3–scrivania (percorso verso la saletta) e C4 nella zona di accesso alla saletta.',
              '- Lati di seduta della scrivania e simultaneità degli usi fra scrivania e C4.',
              '- Collegamento di E05 ed E06 (alternative nel registro utenze).',
              '- Immagini dei pannelli smart e prodotti esposti.',
              '- Verbale di rilievo: data, tecnico, foto e strumenti per ogni quota inserita come verificata.']
    return '\n'.join(lines) + '\n', len(rows)


LINKS = {'ISOLA_SMART': 'https://www.arredamento1.it/collezioni-di-mobili/collezione-di-mobili-monfero/madia-monfero.html',
         'C1': 'https://de.homary.com/lditem/lumio-59-led-6-drawer-dresser-with-charging-station-54469.html',
         'C2': 'Lumio (stessa famiglia, variante 120 da verificare)', 'C3': 'Lumio (stessa famiglia, variante 120 da verificare)',
         'C4': 'https://de.homary.com/lditem/lumio-59-led-6-drawer-dresser-with-charging-station-54469.html',
         'SCRIVANIA': 'https://de.homary.com/item/modern-63-rectangular-walnut-wood-desk-with-charging-station-storage-55649.html',
         'CASSA': 'https://amzn.eu/d/0awMXHm3'}
FINISH = {'CASSA': 'bianca, marchio ufficiale sul frontale', 'C1': 'noce scuro, due linee LED', 'C2': 'noce scuro, due linee LED',
          'C3': 'noce scuro, due linee LED', 'C4': 'noce scuro, due linee LED', 'SCRIVANIA': 'noce',
          'ISOLA_SMART': 'Monfero cachemire, ante verso la vendita'}


def ab01(model):
    lines = ['# AB01 - Abaco arredi', '', f"Revisione {model['revision']} ({TODAY}). L × P × H = dimensioni del PRODOTTO "
             '(L lungo il fronte, P profondità, H altezza totale): ingombri esterni con top e zoccolo compresi. '
             "La posa nel locale è data da fronte/rotazione, ingombro X × Y e posizione; la rotazione cambia X × Y, non L × P × H. "
             'Le schede della variante scelta vanno archiviate prima di portare una dimensione a `verified`.', '',
             '## Arredi di catalogo', '',
             '| ID | Prodotto / fonte | L × P × H prodotto (mm) | Stato dimensioni | Fronte, rotazione | Ingombro X × Y | Posizione X, Y | Stato posa | Finitura |',
             '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for f in model['furniture']:
        p = product_dims(f)
        lines.append(f"| {f['id']} | {LINKS.get(f['id'], '-')} | {p['L']} × {p['P']} × {p['H']} | "
                     f"{STATUS_LABEL[f['status']]} (H {STATUS_LABEL[f['height_status']]}) | {f['front']}, {p['angle']}° | "
                     f"{f['width']} × {f['depth']} | {f['x']}, {f['y']} | {STATUS_LABEL[f['position_status']]} | {FINISH.get(f['id'], '')} |")
    comps = all_components(model)
    dp = model.get('display_proposal', {})
    sw = model.get('smart_wall', {})
    L_ = smart_layout(model) if sw else None

    def n(kind, pref=''):
        return sum(1 for c in comps if c['kind'] == kind and c['owner'].startswith(pref))
    lines += ['', '## Componenti su misura (distinta per il falegname, proposta da validare)', '',
              '| Componente | Quantità | Misure proposte (mm) | Stato | Fonte |', '| --- | --- | --- | --- | --- |']
    lines.append(f"| Mensole bianche sfalsate (pezzi) | {n('shelf', 'ESP_')} su {len(dp.get('over', []))} pareti attrezzate ({', '.join(dp.get('over', []))}) | "
                 f"prof. {dp.get('shelf_depth')}, sp. {dp.get('shelf_thickness')}, base ai livelli {dp.get('shelf_levels')}, sfalsamento {dp.get('stagger')}; "
                 f"interrotte sui cubotti | ipotesi | S4, proposta |")
    c = dp['cubby']
    lines.append(f"| Cubotti aperti rovere | {n('cubby', 'ESP_') // 5} | {c['size']} × {c['size']} × prof. {c['depth']}, pannelli {c['board']} (5 pezzi) | ipotesi | S4, proposta |")
    s = dp['slat_mirror']
    lines.append(f"| Colonne listelli rovere + specchio | {len(dp.get('slat_columns', []))} ({', '.join(c_['id'] for c_ in dp['slat_columns'])}) | "
                 f"larghezza {s['width']}, listelli {s['slat']} × {s['slat_depth']} passo {s['slat'] + s['slat_gap']}, sommità soffitto - {s['top_gap_from_ceiling']}; "
                 f"specchio {s['mirror_width']} × {s['mirror_height']} da quota {s['mirror_bottom']}, sp. {s['mirror_thickness']} su piastra {s['mirror_plate']} | ipotesi | S4, proposta |")
    lines.append(f"| Profili LED (cassettiere, mensole, cubotti) | {n('led')} tratti | cassettiere: assi a {dp['drawer_led']['axes_fraction']} di H, fresata "
                 f"{dp['drawer_led']['groove_depth']}; mensole: sotto il piano | ipotesi | schede LED da acquisire |")
    if sw:
        p = sw['panels']
        lines.append(f"| Telai smart | {p['count']} | telaio esterno {L_['frame']} × {p['height']}, immagine {L_['image']} (bordo {p['frame_border']}), "
                     f"distanza libera {L_['clear_gap']}, interasse {L_['interaxis']}, base a {p['bottom']}, prof. {p['frame_depth']} | ipotesi | S4/S2, proposta |")
        lines.append(f"| Immagini dei pannelli | {p['count']} | {L_['image']} × {p['height'] - 2 * p['frame_border']} | da definire | asset da fornire |")
        lines.append(f"| Ripiani prodotto smart | {p['count']} | {sw['shelf']['width']} × {sw['shelf']['depth']} × {sw['shelf']['thickness']}, base a {sw['shelf']['z']} | ipotesi | S4, proposta |")
        lines.append(f"| Cartellini smart | {p['count']} | {sw['label']['width']} × {sw['label']['height']}, base a {sw['label']['z']}; testi S4 | ipotesi | S4, proposta |")
        g = smart_wall_geom(model)
        lines.append(f"| Rivestimento mattoni marrone scuro | 1 parete | {g['y1'] - g['y0']} × soffitto, sp. {sw['cladding']['thickness']} | ipotesi | decisioni |")
    lines += ['', '## Distinta componenti (geometria comune a prospetti e render)', '',
              'Stessi solidi usati da F01–F04 e dalla scena 3D. Coordinate in mm; z0–z1 = base e sommità.', '',
              '| Componente | Tipo | Parete | x0–x1 | y0–y1 | z0–z1 | Stato | Raccordo |', '| --- | --- | --- | --- | --- | --- | --- | --- |']
    for c_ in comps:
        b = c_['box']
        lines.append(f"| {c_['id']} | {c_['kind']} | {c_['host'] or '-'} | {b[0]:.0f}–{b[3]:.0f} | {b[1]:.0f}–{b[4]:.0f} | "
                     f"{b[2]:.0f}–{b[5]:.0f} | {STATUS_LABEL.get(c_['status'], c_['status'])} | {c_['joint'] or c_.get('joint_note') or ''} |")
    lines += ['', 'Fissaggi, carichi, profili LED, vani driver e passacavi: schema preliminare D01; dati reali pending.']
    return '\n'.join(lines) + '\n'


def e01_register(model):
    lines = ['# E01 - Registro utenze', '', f"Revisione {model['revision']} ({TODAY}). Stessi ID della tavola E01 e dei prospetti. "
             'Le utenze indicano predisposizioni, non circuiti: sezioni, protezioni, potenze e fissaggi sono del tecnico incaricato. '
             'Le luci dei render non sono potenze di progetto.', '',
             '| ID | Servizio / mobile | Tipo | Quantità | X, Y (stato) | Z (stato) | Supporto | Accesso manutenzione | Alimentatore | Percorso | Dati necessari |',
             '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for p in model['electrical_points']:
        need = []
        if p['x'] is None:
            need.append('posizione X/Y')
        if p['z'] is None:
            need.append('quota Z')
        for k in ('quantity', 'route', 'driver', 'support', 'access'):
            if 'da definire' in str(p[k]) or 'da scheda' in str(p[k]):
                need.append(k)
        xy = 'da definire' if p['x'] is None else f"{p['x']}, {p['y']}"
        z = 'da rilevare' if p['z'] is None else str(p['z'])
        lines.append(f"| {p['id']} | {p['service']} ({p['owner']}) | {'/'.join(p['kinds'])} | {p['quantity']} | {xy} ({STATUS_LABEL[p['xy_status']]}) | "
                     f"{z} ({STATUS_LABEL[p['z_status']]}) | {p['support']} | {p['access']} | {p['driver']} | {p['route']} | {', '.join(need) or '-'} |")
    lines += ['', '## Collegamenti sotto arredo da decidere', '']
    for p in model['electrical_points']:
        if p.get('connection_options'):
            lines.append(f"**{p['id']}** ({p['service']}): {p.get('decision', '')}")
            lines += [f"- {o}" for o in p['connection_options']]
            lines.append('')
    return '\n'.join(lines) + '\n'


# --- Proposte di layout quotate -----------------------------------------------------------

def apply_overrides(model, ov):
    m = copy.deepcopy(model)
    for fid, fields in ov.get('furniture', {}).items():
        next(f for f in m['furniture'] if f['id'] == fid).update(fields)
    for cid, fields in ov.get('slat_columns', {}).items():
        next(c for c in m['display_proposal']['slat_columns'] if c['id'] == cid).update(fields)
    for pid, fields in ov.get('functional_pairs', {}).items():
        next(p for p in m['functional_pairs'] if p['id'] == pid).update(fields)
    for k, v in ov.get('display_proposal', {}).items():
        m['display_proposal'][k] = v
    m['revision'] = model['revision'] + '-' + ov['id']
    return m


KEY_CHECKS = ['REQ-REQ_SCALA_CASSA', 'ADJ_CASSA_SINISTRA', 'FP01', 'FP02', 'FP02-PERCORSO', 'FP03', 'FP05', 'FP05-PERCORSO',
              'APPR-P_SAL', 'FP04']


def proposals(model):
    res0 = {r['id']: r for r in run_all(model)}
    stair = next(z for z in model['room_features'] if z['id'] == 'SCALE')
    sy1 = stair['y'] + stair['depth']
    yb = max(v[1] for v in model['envelope']['vertices'])
    req = model['requirements'][0]
    lines = ['# Proposte di layout quotate (R02)', '',
             f"Revisione base {model['revision']} ({TODAY}). Le varianti sono **proposte da approvare**: il modello di base resta invariato. "
             'Ogni variante è valutata con gli stessi controlli della base. Misure in mm, tutte preliminari.', '',
             '## Luce scala–cassa con la cassa sul muro sinistro', '',
             f"Scala fino a y {sy1} (S1; da P00 sarebbe 3850), fondo a y {yb}: fascia disponibile {yb - sy1} mm. "
             f"Lungo il muro sinistro, verso la vetrina, la scala inizia a y {stair['y']} e la porta d'ingresso occupa x 850–1750 con apertura di 900 mm.", '',
             '| Banco (profondità P) | Fascia necessaria (P + 1000 / P + 1200) | Fine scala necessaria (y ≤) | Con la scala del modello |', '| --- | --- | --- | --- |']
    for P in (600, 500, 450):
        lines.append(f"| {P} | {P + req['min']} / {P + req['target'][1]} | {yb - P - req['min']} | "
                     f"{'possibile' if sy1 <= yb - P - req['min'] else f'manca {P + req['min'] - (yb - sy1)} mm'} |")
    lines += ['', f"Verso la vetrina: la cassa dovrebbe finire entro y {stair['y'] - req['min']}, cioè una profondità massima di "
              f"{stair['y'] - req['min']} mm nella fascia y 0–{stair['y'] - req['min']}, dentro l'apertura della porta d'ingresso: non praticabile.", '',
              '**Conclusione nelle ipotesi P02:** con la cassa sul muro sinistro il requisito non si ottiene finché il rilievo conferma la scala fino a '
              f"y {sy1}. Servono: rilievo della fine scala e del parapetto, profondità reale del banco, oppure una deroga al vincolo «cassa sul muro sinistro» (V1).", '']
    for v in model.get('layout_proposals', []):
        m = apply_overrides(model, v)
        res = {r['id']: r for r in run_all(m)}
        lines += [f"## {v['id']} — {v['title']}", '', v['why'], '', f"**Vincoli toccati:** {v['impact']}", '',
                  '| Elemento | Prima | Dopo |', '| --- | --- | --- |']
        for fid, fields in v.get('furniture', {}).items():
            f0 = next(f for f in model['furniture'] if f['id'] == fid)
            lines.append(f"| {fid} | " + ', '.join(f"{k} {f0[k]}" for k in fields) + ' | ' + ', '.join(f"{k} {val}" for k, val in fields.items()) + ' |')
        for cid, fields in v.get('slat_columns', {}).items():
            c0 = next(c for c in model['display_proposal']['slat_columns'] if c['id'] == cid)
            lines.append(f"| {cid} | " + ', '.join(f"{k} {c0[k]}" for k in fields) + ' | ' + ', '.join(f"{k} {val}" for k, val in fields.items()) + ' |')
        for pid, fields in v.get('functional_pairs', {}).items():
            lines.append(f"| {pid} | criterio di percorso base | {json.dumps(fields.get('path', fields), ensure_ascii=False)} |")
        lines += ['', '| Controllo | Base | Variante |', '| --- | --- | --- |']
        for k in KEY_CHECKS:
            if k in res0 or k in res:
                a = res0.get(k)
                b = res.get(k)
                fa = f"{OUTCOME_LABEL[a['outcome']]}" + (f", {a['mm']:.0f} mm" if a and a['mm'] is not None else '') if a else '-'
                fb = f"{OUTCOME_LABEL[b['outcome']]}" + (f", {b['mm']:.0f} mm" if b and b['mm'] is not None else '') if b else '-'
                if fa != fb or k in v.get('focus', []):
                    lines.append(f"| {k} | {fa} | {fb} |")
        new = [r for r in res.values() if r['outcome'] in ('CONFLITTO', 'AVVISO') and r['id'] not in res0]
        if new:
            lines += ['', 'Nuove segnalazioni della variante:', ''] + [f"- {r['id']}: {r['text']}" for r in new]
        lines.append('')
    return '\n'.join(lines) + '\n'


# --- Generazione -----------------------------------------------------------------------

def render_status(model):
    """Render attesi dalla configurazione corrente e loro presenza."""
    cfg = json.loads((ROOT / 'config' / 'render.json').read_text(encoding='utf-8'))
    rows = []
    for cam in cfg['cameras']:
        f = OUT / 'render' / f"R01_{cam['name']}.png"
        rev = None
        meta = OUT / 'render' / 'render_meta.json'
        if meta.exists():
            rev = json.loads(meta.read_text(encoding='utf-8')).get(f.name)
        rows.append((cam['name'], f, f.exists(), rev))
    return rows


def generate(pdf=True):
    OUT.mkdir(exist_ok=True)
    model = load()
    manifest = []

    def emit(code, doc, fname, desc, scale):
        doc.saveas(OUT / f'{fname}.dxf')
        files = [f'{fname}.dxf']
        if pdf:
            export_pdf(doc, code, OUT / f'{fname}.pdf')
            files.append(f'{fname}.pdf')
        manifest.append((code, desc, scale, files))
    emit('A01', build_a01(model), 'A01_pianta_arredi_preliminare', "Pianta arredi quotata con ingombri d'uso e luce scala-cassa", '1:50')
    emit('E01', build_e01(model), 'E01_punti_utenza_preliminari', 'Punti utenza e abaco', '1:50')
    for spec in model['elevations']:
        emit(spec['code'], build_elevation(model, spec), elevation_name(spec), ' '.join(spec['title']), '1:20')
    emit('D01', build_d01(model), 'D01_dettagli_schema_preliminare', 'Schema preliminare dettagli dai componenti comuni (non esecutivo, dati pending)', '1:10')
    for v in model.get('layout_proposals', []):
        if v.get('sheet'):
            m = apply_overrides(model, v)
            code = f"A01-{v['id']}"
            emit(code, build_a01(m, code, ['PROPOSTA ' + v['id'] + ' (non approvata)', v['title'][:40], 'Piano terra'],
                                 ['Variante da approvare: la base', 'resta A01. ' + v['impact'][:40]]),
                 f"A01_{v['id']}_proposta", f"Proposta {v['id']}: {v['title']}", '1:50')
    text, n = q01(model)
    (OUT / 'Q01_quote_aperte.md').write_text(text, encoding='utf-8')
    (OUT / 'AB01_abaco_arredi.md').write_text(ab01(model), encoding='utf-8')
    (OUT / 'E01_registro_utenze.md').write_text(e01_register(model), encoding='utf-8')
    (OUT / 'proposte_layout.md').write_text(proposals(model), encoding='utf-8')
    write_report(model, OUT / 'criticita.md')
    manifest += [('Q01', f'Registro quote aperte ({n} righe)', '-', ['Q01_quote_aperte.md']),
                 ('AB01', 'Abaco arredi, distinta su misura e distinta componenti', '-', ['AB01_abaco_arredi.md']),
                 ('E01', 'Registro utenze completo', '-', ['E01_registro_utenze.md']),
                 ('-', 'Proposte di layout quotate', '-', ['proposte_layout.md']),
                 ('-', 'Controlli e superfici', '-', ['criticita.md'])]
    lines = ['# Manifesto degli elaborati generati', '', f"Revisione modello {model['revision']}, generati il {TODAY} con "
             '`python -m src.generate`. Tutte le tavole sono PRELIMINARE - NON PER CANTIERE; DXF in mm 1:1, PDF A3 da stampare al 100%.', '',
             '| Codice | Contenuto | Scala di stampa | File |', '| --- | --- | --- | --- |']
    lines += [f"| {c} | {d} | {s} | {', '.join(f)} |" for c, d, s, f in manifest]
    lines += ['', '## Render (generati da `python -m src.render`)', '', '| Vista | File | Presente | Revisione del modello |',
              '| --- | --- | --- | --- |']
    complete = True
    for name, f, ok, rev in render_status(model):
        lines.append(f"| {name} | render/{f.name} | {'sì' if ok else 'NO'} | {rev or 'non identificata'} |")
        complete &= ok and rev == model['revision']
    lines += ['', 'Set di render ' + ('completo e della revisione corrente.' if complete else
                                       '**incompleto o di revisione diversa: rigenerare con `python -m src.render`.**')]
    (OUT / 'MANIFEST.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    (OUT / 'quote_da_rilevare.md').write_text(
        '# Quote da rilevare\n\nIl registro completo delle quote aperte, dei conflitti e delle decisioni da prendere è '
        '[Q01_quote_aperte.md](Q01_quote_aperte.md), generato dallo stesso modello.\n', encoding='utf-8')
    return OUT


if __name__ == '__main__':
    # Python rende casuale l'hash delle stringhe a ogni avvio e da quello dipende
    # l'ordine di alcuni oggetti nei DXF: si riparte una volta con il seme fisso,
    # così la stessa revisione del modello produce sempre gli stessi file.
    if os.environ.get('PYTHONHASHSEED') != '0':
        env = {**os.environ, 'PYTHONHASHSEED': '0'}
        os.execvpe(sys.executable, [sys.executable, '-m', 'src.generate', *sys.argv[1:]], env)
    print(generate())
