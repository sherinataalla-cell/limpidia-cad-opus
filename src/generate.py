"""Genera gli elaborati preliminari coordinati dal modello parametrico unico.

Uscite in `outputs/` (vedi MANIFEST.md generato):
- A01 pianta arredi quotata con ingombri d'uso (DXF + PDF A3, 1:50)
- E01 punti utenza con abaco (DXF + PDF A3, 1:50)
- F01-F04 prospetti delle pareti attrezzate (DXF + PDF A3, 1:20)
- AB01 abaco arredi, Q01 registro quote aperte, criticita.md, MANIFEST.md

Modello in mm 1:1 nello spazio modello; la scala è solo nell'impaginazione.
"""
import datetime as dt
import math

import ezdxf
from ezdxf.enums import TextEntityAlignment

from .model import (load, bounds, OUT, STATUS_LABEL, weakest, placement_status, front_band, back_side,
                    door_sweep, door_open_leaf, smart_layout, areas, room)
from .checks import run_all, clearances, write_report, LABEL as OUTCOME_LABEL

SHEET = (420, 297)         # A3 orizzontale, mm
WARNING = 'PRELIMINARE - NON PER CANTIERE'
TODAY = dt.date.today().isoformat()

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
    for r in model.get('rooms', []):
        net = r['net']
        cx = sum(p[0] for p in net) / len(net)
        sal_area = areas(model)['saletta netta (facce interne dei tramezzi)']
        if labels:
            sh.text('SALETTA', 5000, 3450, 'ROOMS', TXT * 1.1, TextEntityAlignment.MIDDLE_CENTER)
            sh.text(f'{sal_area:.2f} m² netti{mark(r["status"])}'.replace('.', ','), 5000, 3450 - 1.4 * TXT, 'ROOMS', TXT,
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


def dims_plan(sh, model):
    S = sh.S
    v = model['envelope']['vertices']
    est = model['envelope']['status']
    xs = [p[0] for p in v]
    ys = [p[1] for p in v]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    sh.dim((x0, y1), (x1, y1), (0, y1 + 13 * S), 'DIM_ENVELOPE', 0, mark(est))
    sh.dim((x0, y0), (x0, y1), (x0 - 13 * S, 0), 'DIM_ENVELOPE', 90, mark(est))
    sh.dim((5500, 4750), (5500, 4300), (0, 0), 'DIM_ENVELOPE', 90, mark(est))
    # catena sul fondo e lato destro
    sh.dim((0, 4750), (5500, 4750), (0, y1 + 7 * S), 'DIM_ENVELOPE', 0, mark(est))
    sh.dim((5500, 4750), (7500, 4750), (0, y1 + 7 * S), 'DIM_ENVELOPE', 0, mark(est))
    sh.dim((7500, 0), (7500, 4300), (x1 + 13 * S, 0), 'DIM_ENVELOPE', 90, mark(est))
    sh.dim((5500, 4300), (5500, 4750), (5500 + 3 * S, 0), 'DIM_ENVELOPE', 90, mark(est))
    # facciata
    segs = model.get('facade', [])
    for s in segs:
        sh.dim((s['x0'], 0), (s['x1'], 0), (0, -6 * S), 'DIM_ENVELOPE', 0, mark(s['status']))
    # saletta: larghezza e profondità nette, spessore tramezzo
    sal = room(model, 'SALETTA')
    st = sal['status']
    net = sal['net']
    nx0 = min(p[0] for p in net)
    ny0 = min(p[1] for p in net)
    sh.dim((nx0, 4000), (7500, 4000), (0, 4000), 'DIM_FURNITURE', 0, mark(st))
    sh.dim((4300, ny0), (4300, 4750), (4300, 0), 'DIM_FURNITURE', 90, mark(st))
    sh.dim((6700, ny0), (6700, 4300), (6700, 0), 'DIM_FURNITURE', 90, mark(st))
    w = next(w for w in model['walls'] if w['id'] == 'W_SAL_O')
    sh.dim((w['x'], 3300), (w['x'] + w['width'], 3300), (0, 3300), 'DIM_FURNITURE', 0, mark(w['status']))
    sh.dim((3390, 2680), (3390, 0), (3390 - 2 * S, 0), 'DIM_ENVELOPE', 90, mark(st))
    sh.dim((7500, 0), (7500, 2680), (x1 + 6 * S, 0), 'DIM_ENVELOPE', 90, mark(st))
    sh.dim((0, 4750), (3390, 4750), (0, y1 + 2.5 * S), 'DIM_ENVELOPE', 0, mark(st))
    for op in model.get('openings', []):
        if op['y'] > 0:
            sh.dim((op['x0'], op['y']), (op['x1'], op['y']), (0, op['y'] - 3 * S), 'DIM_ENVELOPE', 0, mark(op['status']))
    # scala
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
        if fr == '-y':
            yd = y0 - 2 * S
        xd = x0 - 2 * S if fr == '-x' else x1 + 2 * S
        sh.dim((x0, y0), (x1, y0), (0, yd), 'DIM_FURNITURE', 0, st)
        sh.dim((x0, y0), (x0, y1), (xd, 0), 'DIM_FURNITURE', 90, st)


def dims_clearances(sh, model):
    for c in clearances(model):
        a, b = c['ra'], c['rb']
        if c['mm'] is None or c['mm'] <= 1:
            continue
        # quota sull'asse in cui i due oggetti si fronteggiano
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


def plan_limits(model, pad_mm=2000):
    xs = [v[0] for v in model['envelope']['vertices']]
    ys = [v[1] for v in model['envelope']['vertices']]
    return min(xs) - pad_mm, min(ys) - pad_mm * 0.9, max(xs) + pad_mm * 0.7, max(ys) + pad_mm * 0.6


LEGEND_A01 = [(7, 'Muratura esistente (ipotesi)'), (8, 'Tramezzo proposto 10 cm'), (30, 'Mobile, misure ipotesi'),
              (3, 'Mobile da catalogo'), (1, 'Mobile da definire'), (140, "Ingombro d'uso ipotizzato"),
              (6, 'Distanza di coppia funzionale (FPxx)')]
LEGEND_E01 = [(7, 'Muratura esistente (ipotesi)'), (8, 'Tramezzo proposto'), (30, 'Ingombro mobili'),
              (5, 'Punto utenza: X/Y ipotesi, Z da rilevare')]


def build_a01(model):
    sh = Sheet(50)
    draw_plan(sh, model)
    draw_furniture(sh, model)
    draw_use(sh, model)
    dims_plan(sh, model)
    dims_furniture(sh, model)
    dims_clearances(sh, model)
    res = [r for r in run_all(model) if r['cat'] in ('uso', 'porte', 'contenimento', 'sovrapposizione')]

    def table(lay, t):
        y = 112
        t("INGOMBRI D'USO E VERIFICHE (dettaglio in outputs/criticita.md)", 15, y, 2.6)
        y -= 5
        for r in res:
            txt = f"{r['id']:<10} {OUTCOME_LABEL[r['outcome']]:<34} {r['text']}"
            t(txt[:175], 15, y, 1.8)
            y -= 3.4
            if y < 14:
                break
    sh.layout('A01', ['Pianta arredi quotata', "con ingombri d'uso", 'Piano terra'], LEGEND_A01, model,
              plan_limits(model), (12, 118, 302, 285),
              notes=["Fasce d'uso: ipotesi di screening,", 'non misure di prodotto.'], extra=table)
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
        t('ABACO UTENZE (stessi ID della pianta; X/Y ipotesi, Z da rilevare; circuiti e protezioni a cura del tecnico)', 15, y, 2.4)
        y -= 5
        t('ID     Servizio / mobile                                         Tipo              X     Y     Z         Supporto / accesso', 15, y, 1.9)
        y -= 4
        for p in model['electrical_points']:
            xy = f"{p['x'] if p['x'] is not None else '-':>5} {p['y'] if p['y'] is not None else '-':>5}"
            z = 'DA RILEVARE' if p['z'] is None else f"{p['z']}"
            t(f"{p['id']:<6} {p['service'][:58]:<58} {'/'.join(p['kinds']):<17} {xy} {z:<11}", 15, y, 1.9)
            y -= 3.2
            t(f"         supporto: {p['support']}; accesso: {p['access']}; alimentatore: {p['driver']}"[:190], 15, y, 1.6, 'TEXT')
            y -= 3.6
    sh.layout('E01', ['Punti utenza energia/dati', 'e alimentazioni LED', 'Piano terra'], LEGEND_E01, model,
              plan_limits(model), (12, 118, 302, 285),
              notes=['Simbolo: cerchio energia, croce dati,', 'cerchio interno alimentazione LED.',
                     'Le luci dei render non sono potenze.'], extra=table)
    return sh.doc


# --- Prospetti --------------------------------------------------------------------

ELEVATIONS = [
    {'code': 'F01', 'title': ['Prospetto parete di fondo', 'cassa e C1'], 'axis': 'x', 'fixed': 4750,
     'from': 0, 'to': 3390, 'sign': 1, 'look': '+y'},
    {'code': 'F02', 'title': ['Prospetto parete smart', 'tramezzo W_SAL_O lato scala'], 'axis': 'y', 'fixed': 3390,
     'from': 4750, 'to': 2680, 'sign': -1, 'look': '+x'},
    {'code': 'F03', 'title': ['Prospetto fronte saletta', 'C2, C3 e porta P_SAL'], 'axis': 'x', 'fixed': 2680,
     'from': 3390, 'to': 7500, 'sign': 1, 'look': '+y'},
    {'code': 'F04', 'title': ['Prospetto parete laterale', 'consulenza, C4'], 'axis': 'y', 'fixed': 7500,
     'from': 2680, 'to': 0, 'sign': -1, 'look': '+x'},
]


def _u(spec, x, y):
    c = x if spec['axis'] == 'x' else y
    return (c - spec['from']) * spec['sign']


def _on_wall(spec, item):
    """Vero se il retro del mobile sta sulla parete del prospetto."""
    x0, y0, x1, y1 = bounds(item)
    back = back_side(item)
    val = {'x0': x0, 'x1': x1, 'y0': y0, 'y1': y1}[back]
    along = 'x' if back.startswith('y') else 'y'
    lo, hi = sorted((spec['from'], spec['to']))
    a0, a1 = (x0, x1) if along == 'x' else (y0, y1)
    return along == spec['axis'] and abs(val - spec['fixed']) <= 60 and a0 >= lo - 1 and a1 <= hi + 1


def build_elevation(model, spec):
    sh = Sheet(20)
    S, TXT = sh.S, sh.TXT
    H = model['ceiling']['height']
    L = abs(spec['to'] - spec['from'])
    sh.line((0, 0), (L, 0), 'WALLS', lineweight=70)
    sh.line((0, H), (L, H), 'WALLS', linetype='DASHED', ltscale=6)
    sh.line((0, 0), (0, H), 'WALLS', lineweight=50)
    sh.line((L, 0), (L, H), 'WALLS', lineweight=50)
    sh.text(f"soffitto {H}{mark(model['ceiling']['status'])} (S3, ribassamenti da rilevare)", 100, H + 60, 'TEXT', TXT * 0.8)
    sh.dim((L, 0), (L, H), (L + 6 * S, 0), 'DIM_ENVELOPE', 90, mark(model['ceiling']['status']))
    sh.dim((0, 0), (L, 0), (0, -9 * S), 'DIM_ENVELOPE', 0, mark(model['envelope']['status']))
    disp = model.get('display_proposal', {})
    # Mobili appoggiati a questa parete
    for f in model['furniture']:
        if not _on_wall(spec, f):
            continue
        x0, y0, x1, y1 = bounds(f)
        u0, u1 = sorted((_u(spec, x0, y0 if spec['axis'] == 'x' else y0), _u(spec, x1 if spec['axis'] == 'x' else x0, y1)))
        h = f['height']
        st = weakest(f['status'], f.get('height_status'))
        lay = FURN_LAYER[weakest(f['status'], f.get('position_status'))]
        if f['id'].startswith('C') and f['id'] != 'CASSA':
            sh.rect((u0, 80, u1, h), lay)
            sh.rect((u0 + 20, 0, u1 - 20, 80), lay)
            for zz in (h * 0.38, h * 0.70):
                sh.line((u0 + 30, zz), (u1 - 30, zz), 'DISPLAY', color=2, lineweight=35)
            # mensole sfalsate, cubotti
            if f['id'] in disp.get('over', []):
                for li, z in enumerate(disp['shelf_levels']):
                    off = disp['stagger'] if li % 2 else 0
                    a, b = u0 + off, u1 - disp['stagger'] + off
                    sh.rect((a, z, b, z + disp['shelf_thickness']), 'DISPLAY')
                    if li == 1:
                        c = disp['cubby']['size']
                        cx = a + (b - a) * 0.62
                        sh.rect((cx, z + disp['shelf_thickness'], cx + c, z + disp['shelf_thickness'] + c), 'DISPLAY', color=40)
                sh.dim((u1, 0), (u1, disp['shelf_levels'][0]), (u1 + 2 * S, 0), 'DIM_FURNITURE', 90, mark(disp['status']))
                for z0, z1 in zip(disp['shelf_levels'], disp['shelf_levels'][1:]):
                    sh.dim((u1, z0), (u1, z1), (u1 + 2 * S, 0), 'DIM_FURNITURE', 90, mark(disp['status']))
        else:
            sh.rect((u0, 0, u1, h), lay)
            if f['id'] == 'CASSA':
                sh.text('marchio ufficiale (assets/brand)', (u0 + u1) / 2, h / 2, 'TEXT', TXT * 0.7, TextEntityAlignment.MIDDLE_CENTER)
        sh.text(f['id'], (u0 + u1) / 2, h + 60, lay, TXT, TextEntityAlignment.BOTTOM_CENTER)
        sh.dim((u0, 0), (u1, 0), (0, -3 * S), 'DIM_FURNITURE', 0, mark(f['status']))
        sh.dim((u0, 0), (u0, h), (u0 - 2 * S, 0), 'DIM_FURNITURE', 90, mark(st))
    # Colonne listelli + specchio
    for c in disp.get('slat_columns', []):
        x0, y0, x1, y1 = bounds(c)
        on = (spec['axis'] == 'x' and abs((y1 if spec['look'] == '+y' else y0) - spec['fixed']) <= 60) or \
             (spec['axis'] == 'y' and abs(x1 - spec['fixed']) <= 60)
        lo, hi = sorted((spec['from'], spec['to']))
        a0, a1 = (x0, x1) if spec['axis'] == 'x' else (y0, y1)
        if not on or a0 < lo or a1 > hi:
            continue
        u0, u1 = sorted((_u(spec, a0, a0), _u(spec, a1, a1)))
        sm = disp['slat_mirror']
        k = u0
        while k + sm['slat'] <= u1:
            sh.rect((k, 0, k + sm['slat'], H - 400), 'DISPLAY', color=40)
            k += sm['slat'] + sm['slat_gap']
        mw = sm['mirror_width']
        mu = (u0 + u1 - mw) / 2
        sh.rect((mu, sm['mirror_bottom'], mu + mw, sm['mirror_bottom'] + sm['mirror_height']), 'DISPLAY', color=5)
        sh.text(f"{c['id']} listelli + specchio", (u0 + u1) / 2, H - 340, 'DISPLAY', TXT * 0.7, TextEntityAlignment.BOTTOM_CENTER)
        sh.dim((u0, 0), (u1, 0), (0, -3 * S), 'DIM_FURNITURE', 0, mark(disp['status']))
    # Porte sulla parete
    for op in model.get('openings', []):
        if spec['axis'] == 'x' and op['y'] == spec['fixed']:
            u0, u1 = sorted((_u(spec, op['x0'], 0), _u(spec, op['x1'], 0)))
            if u0 < 0 or u1 > L:
                continue
            # altezza del vano non nota: montanti tratteggiati e simbolo solo indicativi (nessuna quota Z)
            for a, b in (((u0, 0), (u0, 2100)), ((u1, 0), (u1, 2100)), ((u0, 2100), (u1, 2100))):
                sh.line(a, b, 'DOORS', linetype='DASHED', ltscale=6)
            sh.text(f"{op['id']} vano {op['opening_width']}{mark(op['status'])}", (u0 + u1) / 2, 2260, 'DOORS',
                    TXT * 0.75, TextEntityAlignment.BOTTOM_CENTER)
            sh.text("altezza DA RILEVARE (simbolo)", (u0 + u1) / 2, 2160, 'DOORS',
                    TXT * 0.75, TextEntityAlignment.BOTTOM_CENTER)
            sh.dim((u0, 0), (u1, 0), (0, -3 * S), 'DIM_FURNITURE', 0, mark(op['status']))
    # Parete smart
    if spec['code'] == 'F02' and 'smart_wall' in model:
        sw = model['smart_wall']
        sh.hatch([(0, 0), (L, 0), (L, H), (0, H)], 'BRICK', 'BRICK', color=32, scale=12)
        lay_ = smart_layout(model)
        p = sw['panels']
        for k, (ya, yb) in enumerate(lay_['panels']):
            u0, u1 = sorted((_u(spec, 0, ya), _u(spec, 0, yb)))
            sh.rect((u0, p['bottom'], u1, p['bottom'] + p['height']), 'DISPLAY', color=7)
            sh.hatch([(u0, p['bottom']), (u1, p['bottom']), (u1, p['bottom'] + p['height']), (u0, p['bottom'] + p['height'])],
                     'DISPLAY', color=254)
            sh.text(sw['panel_titles'][k], (u0 + u1) / 2, p['bottom'] + p['height'] - 120, 'TEXT', TXT * 0.7,
                    TextEntityAlignment.MIDDLE_CENTER)
            s = sw['shelf']
            sh.rect((u0, s['z'], u1, s['z'] + 25), 'DISPLAY', color=7)
            lb = sw['label']
            lu = (u0 + u1 - lb['width']) / 2
            sh.rect((lu, lb['z'], lu + lb['width'], lb['z'] + lb['height']), 'DISPLAY', color=7)
        # quote orizzontali della composizione: margine + 4 pannelli + 3 interassi
        pts = [0]
        for ya, yb in lay_['panels']:
            u0, u1 = sorted((_u(spec, 0, ya), _u(spec, 0, yb)))
            pts += [u0, u1]
        pts.append(L)
        for a, b in zip(pts, pts[1:]):
            if b - a > 1:
                sh.dim((a, p['bottom'] + p['height']), (b, p['bottom'] + p['height']), (0, p['bottom'] + p['height'] + 4 * S),
                       'DIM_FURNITURE', 0, mark(p['status']))
        first = (pts[1], pts[-2])  # estremi della composizione
        sh.dim((first[0], 0), (first[1], 0), (0, -3 * S), 'DIM_FURNITURE', 0,
               f" fascia (S2: {sw['band']['length']})" + mark(sw['band']['status']))
        sh.dim((L, 0), (L, sw['label']['z']), (L + 2 * S, 0), 'DIM_FURNITURE', 90, mark(p['status']))
        sh.dim((L, sw['label']['z']), (L, sw['shelf']['z']), (L + 2 * S, 0), 'DIM_FURNITURE', 90, mark(p['status']))
        sh.dim((L, sw['shelf']['z']), (L, p['bottom']), (L + 2 * S, 0), 'DIM_FURNITURE', 90, mark(p['status']))
        sh.dim((L, p['bottom']), (L, p['bottom'] + p['height']), (L + 2 * S, 0), 'DIM_FURNITURE', 90, mark(p['status']))
        sh.text(f"rivestimento mattoni sp. {sw['cladding']['thickness']}{mark(sw['cladding']['status'])}", 100, H - 250,
                'TEXT', TXT * 0.8)
    # Utenze sulla parete
    for pnt in model['electrical_points']:
        if pnt['x'] is None:
            continue
        coord = pnt['x'] if spec['axis'] == 'x' else pnt['y']
        other = pnt['y'] if spec['axis'] == 'x' else pnt['x']
        lo, hi = sorted((spec['from'], spec['to']))
        if abs(other - spec['fixed']) <= 30 and lo - 1 <= coord <= hi + 1:
            u = _u(spec, coord, coord)
            sh.line((u, 0), (u, 2750), 'ELECTRICAL', linetype='DASHED', ltscale=4)
            sh.text(f"{pnt['id']} Z DA RILEVARE", u + 40, 2800, 'ELECTRICAL', TXT * 0.75, rot=90)
    sh.text('lato sinistro guardando la parete', 0, -14 * S, 'TEXT', TXT * 0.7)
    lim = (-12 * S, -18 * S, L + 14 * S, H + 6 * S)
    sh.layout(spec['code'], spec['title'] + [f"vista verso {spec['look']}"],
              [(7, 'Muratura / tramezzo'), (30, 'Mobile, misure ipotesi'), (8, 'Mensole, listelli (proposta)'),
               (5, 'Utenza: Z da rilevare'), (32, 'Rivestimento mattoni')], model, lim, (14, 14, 302, 285),
              notes=['Altezze dei mobili: ipotesi da schede.', 'Mensole e listelli: proposta da S4,',
                     'non misure rilevate.'])
    return sh.doc


# --- Esportazione --------------------------------------------------------------------

def export_pdf(doc, layout_name, path):
    from ezdxf.addons.drawing import Frontend, RenderContext, pymupdf, layout, config
    lay = doc.layouts.get(layout_name)
    backend = pymupdf.PyMuPdfBackend()
    cfg = config.Configuration(background_policy=config.BackgroundPolicy.WHITE,
                               color_policy=config.ColorPolicy.COLOR, lineweight_scaling=1.0)
    Frontend(RenderContext(doc), backend, config=cfg).draw_layout(lay, finalize=True)
    page = layout.Page(*SHEET, layout.Units.mm)
    path.write_bytes(backend.get_pdf_bytes(page, settings=layout.Settings(scale=1, fit_page=False)))
    return path


# --- Registri ----------------------------------------------------------------------

def q01(model):
    """Registro di tutte le quote non verificate e dei dati mancanti."""
    rows = []

    def add(ref, what, value, status, source):
        if status != 'verified':
            rows.append((ref, what, value, STATUS_LABEL.get(status, status), source))
    e = model['envelope']
    v = e['vertices']
    for a, b in zip(v, v[1:] + v[:1]):
        add('ENVELOPE', f'lato {a} → {b}', f"{abs(b[0]-a[0]) + abs(b[1]-a[1])}", e['status'], e['source'])
    add('ENVELOPE', 'spessori dei muri esistenti, diagonali, fuori squadra', '-', 'pending', 'rilievo')
    add('SOFFITTO', 'quota interna del soffitto e ribassamenti', model['ceiling']['height'], model['ceiling']['status'], model['ceiling']['source'])
    for s in model.get('facade', []):
        add(s['id'], f"facciata {s['type']} x {s['x0']}–{s['x1']}", s['x1'] - s['x0'], s['status'], s['source'])
    for w in model.get('walls', []):
        add(w['id'], f"{w['desc']}: x {w['x']}, y {w['y']}, {w['width']} × {w['depth']}", '-', w['status'], w['source'])
    for op in model.get('openings', []):
        add(op['id'], f"{op['desc']}: vano {op['x0']}–{op['x1']}, luce {op['clear_width'] or 'da rilevare'}, verso", op['opening_width'], op['status'], op['source'])
        add(op['id'], 'altezza del vano, spallette, serramento', '-', 'pending', 'rilievo')
    for r in model.get('rooms', []):
        add(r['id'], 'dimensioni nette della saletta', '4010 × 1970/1520', r['status'], r['source'])
    for z in model['room_features']:
        add(z['id'], 'posizione e dimensioni' + (' (spessore e sporgenza corrimano)' if z['type'] == 'line' else ''), '-', z['status'], z['source'])
    for f in model['furniture']:
        add(f['id'], 'dimensioni in pianta', f"{f['width']} × {f['depth']}", f['status'], f['source'])
        add(f['id'], 'posizione nel locale', f"x {f['x']}, y {f['y']}", f['position_status'], f['source'])
        add(f['id'], 'altezza', f['height'], f['height_status'], 'scheda prodotto da archiviare')
    for k, u in model.get('use_assumptions', {}).items():
        if isinstance(u, dict) and 'status' in u:
            add('USO', f"{k}: {u.get('note', '')}", u.get('value'), u['status'], u['source'])
    add('USO', 'railing_thickness: spessore e sporgenza del corrimano', '-', 'pending', 'rilievo')
    sw = model.get('smart_wall')
    if sw:
        add('SMART', 'fascia smart', sw['band']['length'], sw['band']['status'], sw['band']['source'])
        add('SMART', 'pannelli: larghezza, interasse, altezza, quota', f"{sw['panels']['width']}/{sw['panels']['gap']}/{sw['panels']['height']}/{sw['panels']['bottom']}",
            sw['panels']['status'], sw['panels']['source'])
        add('SMART', 'rivestimento mattoni: spessore e fissaggio', sw['cladding']['thickness'], sw['cladding']['status'], sw['cladding']['source'])
    dp = model.get('display_proposal')
    if dp:
        add('ESPOSIZIONE', 'livelli mensole, cubotti, listelli e specchi', str(dp['shelf_levels']), dp['status'], dp['source'])
    for p in model['electrical_points']:
        add(p['id'], f"posizione X/Y ({p['service']})", f"{p['x']}, {p['y']}", p['xy_status'], 'S0')
        add(p['id'], 'quota Z, quantità, supporto, alimentatore, percorso', '-', p['z_status'], 'elettricista')
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
    lines += ['', '## Decisioni da prendere', '',
              '- Lato operatore della cassa e prodotto reale (oggi segnaposto 1200 × 600 a contatto con il fondo e il muro sinistro).',
              '- C1 da 1200 o 1500; C2/C3 da 120 cm; C4 da 150 cm: varianti da confermare.',
              '- Lati di seduta della scrivania (operatore verso C4 o verso la saletta).',
              '- Supporto di E05 ed E06 (pavimento sotto il mobile o parete) e modalità di accesso.',
              '- Composizione della parete smart (pannelli 410 mm, interasse 470 mm: proposta).',
              '- Verbale di rilievo: data, tecnico, foto e strumenti per ogni quota inserita come verificata.']
    return '\n'.join(lines) + '\n', len(rows)


def ab01(model):
    links = {'ISOLA_SMART': 'https://www.arredamento1.it/collezioni-di-mobili/collezione-di-mobili-monfero/madia-monfero.html',
             'C1': 'https://de.homary.com/lditem/lumio-59-led-6-drawer-dresser-with-charging-station-54469.html',
             'C2': 'Lumio (stessa famiglia, variante 120 da verificare)', 'C3': 'Lumio (stessa famiglia, variante 120 da verificare)',
             'C4': 'https://de.homary.com/lditem/lumio-59-led-6-drawer-dresser-with-charging-station-54469.html',
             'SCRIVANIA': 'https://de.homary.com/item/modern-63-rectangular-walnut-wood-desk-with-charging-station-storage-55649.html',
             'CASSA': 'https://amzn.eu/d/0awMXHm3'}
    finish = {'CASSA': 'bianca, marchio ufficiale sul frontale', 'C1': 'noce scuro, due linee LED', 'C2': 'noce scuro, due linee LED',
              'C3': 'noce scuro, due linee LED', 'C4': 'noce scuro, due linee LED', 'SCRIVANIA': 'noce',
              'ISOLA_SMART': 'Monfero cachemire, ante verso la vendita'}
    lines = ['# AB01 - Abaco arredi', '', f"Revisione {model['revision']} ({TODAY}). Dimensioni di prodotto separate dalla posa. "
             'Le schede della variante scelta vanno archiviate (PDF o screenshot) prima di portare una dimensione a `verified`.', '',
             '## Arredi di catalogo', '',
             '| ID | Prodotto / fonte | L × P × H (mm) | Stato dimensioni | Posizione X, Y | Stato posa | Finitura | Frontale |',
             '| --- | --- | --- | --- | --- | --- | --- | --- |']
    for f in model['furniture']:
        lines.append(f"| {f['id']} | {links.get(f['id'], '-')} | {f['width']} × {f['depth']} × {f['height']} | "
                     f"{STATUS_LABEL[f['status']]} (H {STATUS_LABEL[f['height_status']]}) | {f['x']}, {f['y']} | "
                     f"{STATUS_LABEL[f['position_status']]} | {finish.get(f['id'], '')} | {f['front']} |")
    dp = model.get('display_proposal', {})
    sw = model.get('smart_wall', {})
    lines += ['', '## Componenti su misura (distinta per il falegname, proposta da validare)', '',
              '| Componente | Quantità | Misure proposte (mm) | Stato | Fonte |', '| --- | --- | --- | --- | --- |']
    n_over = len(dp.get('over', []))
    lines.append(f"| Mensole bianche sfalsate | {n_over} pareti × {len(dp.get('shelf_levels', []))} livelli | prof. {dp.get('shelf_depth')}, "
                 f"sp. {dp.get('shelf_thickness')}, livelli {dp.get('shelf_levels')}, sfalsamento {dp.get('stagger')} | ipotesi | S4, proposta |")
    if dp.get('cubby'):
        c = dp['cubby']
        lines.append(f"| Cubotti aperti rovere | {n_over} | {c['size']} × {c['size']} × prof. {c['depth']}, pannello {c['board']} | ipotesi | S4, proposta |")
    if dp.get('slat_mirror'):
        s = dp['slat_mirror']
        lines.append(f"| Colonne listelli rovere + specchio | {len(dp.get('slat_columns', []))} | larghezza {s['width']}, listello {s['slat']} "
                     f"passo {s['slat'] + s['slat_gap']}, specchio {s['mirror_width']} × {s['mirror_height']} a {s['mirror_bottom']} | ipotesi | S4, proposta |")
    if sw:
        p = sw['panels']
        lines.append(f"| Telai smart con immagine e titolo | {p['count']} | {p['width']} × {p['height']}, interasse {p['width'] + p['gap']}, "
                     f"base a {p['bottom']} | ipotesi | S4/S2, proposta |")
        lines.append(f"| Ripiani prodotto smart | {p['count']} | {sw['shelf']['width']} × {sw['shelf']['depth']} a {sw['shelf']['z']} | ipotesi | S4, proposta |")
        lines.append(f"| Cartellini smart | {p['count']} | {sw['label']['width']} × {sw['label']['height']} a {sw['label']['z']} | ipotesi | S4, proposta |")
        lines.append(f"| Rivestimento mattoni marrone scuro | 1 parete | {sw['y1'] - sw['y0']} × soffitto, sp. {sw['cladding']['thickness']} | ipotesi | decisioni |")
    lines += ['', 'Fissaggi, carichi, profili LED, vani driver e passacavi: dettaglio D01 da sviluppare dopo le schede reali.']
    return '\n'.join(lines) + '\n'


OUTPUTS = [
    ('A01', build_a01, 'A01_pianta_arredi_preliminare', 'Pianta arredi quotata con ingombri d\'uso', '1:50'),
    ('E01', build_e01, 'E01_punti_utenza_preliminari', 'Punti utenza e abaco', '1:50'),
]


def generate(pdf=True):
    OUT.mkdir(exist_ok=True)
    model = load()
    manifest = []
    for name, builder, fname, desc, scale in OUTPUTS:
        d = builder(model)
        d.saveas(OUT / f'{fname}.dxf')
        files = [f'{fname}.dxf']
        if pdf:
            export_pdf(d, name, OUT / f'{fname}.pdf')
            files.append(f'{fname}.pdf')
        manifest.append((name, desc, scale, files))
    for spec in ELEVATIONS:
        d = build_elevation(model, spec)
        fname = f"{spec['code']}_prospetto_{'_'.join(spec['title'][0].split()[2:]).lower()}"
        d.saveas(OUT / f'{fname}.dxf')
        files = [f'{fname}.dxf']
        if pdf:
            export_pdf(d, spec['code'], OUT / f'{fname}.pdf')
            files.append(f'{fname}.pdf')
        manifest.append((spec['code'], ' '.join(spec['title']), '1:20', files))
    text, n = q01(model)
    (OUT / 'Q01_quote_aperte.md').write_text(text, encoding='utf-8')
    (OUT / 'AB01_abaco_arredi.md').write_text(ab01(model), encoding='utf-8')
    write_report(model, OUT / 'criticita.md')
    manifest += [('Q01', f'Registro quote aperte ({n} righe)', '-', ['Q01_quote_aperte.md']),
                 ('AB01', 'Abaco arredi e distinta su misura', '-', ['AB01_abaco_arredi.md']),
                 ('-', 'Controlli e superfici', '-', ['criticita.md'])]
    lines = ['# Manifesto degli elaborati generati', '', f"Revisione modello {model['revision']}, generati il {TODAY} con "
             '`python -m src.generate`. Tutte le tavole sono PRELIMINARE - NON PER CANTIERE; DXF in mm 1:1, PDF A3 da stampare al 100%.', '',
             '| Codice | Contenuto | Scala di stampa | File |', '| --- | --- | --- | --- |']
    lines += [f"| {c} | {d} | {s} | {', '.join(f)} |" for c, d, s, f in manifest]
    lines += ['| D01 | Dettagli mensole, LED, driver, passacavi | - | non generato in questa revisione: servono le schede reali |',
              '| R01 | Render dal modello | - | `python -m src.render` → render/ (non generati da questo comando) |']
    (OUT / 'MANIFEST.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    # Nome richiesto da CLAUDE.md: rimanda al registro completo Q01 (stessi dati, una sola fonte)
    (OUT / 'quote_da_rilevare.md').write_text(
        '# Quote da rilevare\n\nIl registro completo delle quote aperte, dei conflitti e delle decisioni da prendere è '
        '[Q01_quote_aperte.md](Q01_quote_aperte.md), generato dallo stesso modello.\n', encoding='utf-8')
    return OUT


if __name__ == '__main__':
    print(generate())
