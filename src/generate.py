"""Genera le tavole preliminari dal modello parametrico unico.

Uscite in `outputs/`:
- A01 pianta arredi quotata (DXF + PDF A3, scala 1:50)
- E01 punti utenza preliminari (DXF + PDF A3, scala 1:50)
- quote_da_rilevare.md, criticita.md

Modello in millimetri 1:1 nello spazio modello; la scala 1:50 è solo
nell'impaginazione (layout di stampa con cartiglio).
"""
import datetime as dt

import ezdxf
from ezdxf.enums import TextEntityAlignment

from .model import load, bounds, OUT, STATUS_LABEL
from .checks import clearances, write_report, PASSAGGIO_MM, ACCOSTATO_MM

SCALE = 50                 # 1:50
SHEET = (420, 297)         # A3 orizzontale, mm
WARNING = 'PRELIMINARE - NON PER CANTIERE'

LAYERS = [
    ('WALLS', 7, 50), ('ROOMS_ASSUMED', 8, 25), ('FURNITURE_ASSUMED', 30, 35),
    ('FURNITURE_PENDING', 1, 35), ('FURNITURE_CATALOG', 3, 35), ('FURNITURE_VERIFIED', 7, 35),
    ('ELECTRICAL', 5, 35), ('DIM_ENVELOPE', 7, 18), ('DIM_FURNITURE', 8, 18),
    ('DIM_CLEARANCE', 6, 18), ('TEXT', 7, 18), ('WARNING', 1, 35), ('SHEET', 7, 25),
]
FURN_LAYER = {'assumed': 'FURNITURE_ASSUMED', 'pending': 'FURNITURE_PENDING',
              'catalog': 'FURNITURE_CATALOG', 'verified': 'FURNITURE_VERIFIED'}

# Testi e frecce in mm di carta, convertiti in unità modello.
TXT = 2.5 * SCALE


def new_doc():
    d = ezdxf.new('R2010', setup=True)
    d.header['$INSUNITS'] = 4  # millimetri
    d.header['$LWDISPLAY'] = 1
    for name, color, lw in LAYERS:
        d.layers.add(name, color=color, lineweight=lw)
    ds = d.dimstyles.duplicate_entry('EZDXF', 'LIMPIDIA_50')
    ds.dxf.dimtxt = TXT * 0.9
    ds.dxf.dimasz = 1.5 * SCALE
    ds.dxf.dimexo = 1.0 * SCALE
    ds.dxf.dimexe = 1.0 * SCALE
    ds.dxf.dimgap = 0.6 * SCALE
    ds.dxf.dimdec = 0
    ds.dxf.dimtsz = 0
    ds.dxf.dimtad = 1
    ds.dxf.dimlunit = 2
    ds.dxf.dimlfac = 1
    ds.dxf.dimtih = 0
    ds.dxf.dimtoh = 0
    ds.dxf.dimjust = 0
    ds.dxf.dimtmove = 2
    ds.dxf.dimclrt = 0
    ds.dxf.dimblk = 'ARCHTICK'
    return d


def rectangle(m, r, layer):
    x0, y0, x1, y1 = r
    m.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True, dxfattribs={'layer': layer})


def label(m, s, x, y, layer='TEXT', h=TXT, align=TextEntityAlignment.LEFT):
    t = m.add_text(s, height=h, dxfattribs={'layer': layer, 'style': 'OpenSans'})
    t.set_placement((x, y), align=align)
    return t


def dim(m, p1, p2, base, layer, angle=0, suffix=''):
    d = m.add_linear_dim(base=base, p1=p1, p2=p2, angle=angle, dimstyle='LIMPIDIA_50',
                         text='<>' + suffix, dxfattribs={'layer': layer})
    d.render()


def mark(status):
    """Le quote non verificate portano un asterisco."""
    return '' if status == 'verified' else ' *'


def draw_base(m, model):
    env = model['envelope']
    m.add_lwpolyline(env['vertices'], close=True, dxfattribs={'layer': 'WALLS', 'lineweight': 70})
    for f in model['room_features']:
        if f['type'] == 'zone':
            r = bounds(f)
            rectangle(m, r, 'ROOMS_ASSUMED')
            h = m.add_hatch(color=8, dxfattribs={'layer': 'ROOMS_ASSUMED'})
            h.set_pattern_fill('ANSI31', scale=12, color=9)
            x0, y0, x1, y1 = r
            h.paths.add_polyline_path([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
            label(m, f['id'], (x0 + x1) / 2, (y0 + y1) / 2, 'ROOMS_ASSUMED', TXT * 1.1,
                  TextEntityAlignment.MIDDLE_CENTER)
        else:
            m.add_line(f['start'], f['end'], dxfattribs={'layer': 'ROOMS_ASSUMED', 'linetype': 'DASHED',
                                                         'ltscale': 10})
            mx = (f['start'][0] + f['end'][0]) / 2
            my = (f['start'][1] + f['end'][1]) / 2
            t = label(m, f['id'], mx - 60, my, 'ROOMS_ASSUMED', TXT * 0.8, TextEntityAlignment.MIDDLE_CENTER)
            t.dxf.rotation = 90
    # Lati di riferimento, solo testo descrittivo
    xs = [v[0] for v in env['vertices']]
    ys = [v[1] for v in env['vertices']]
    label(m, 'VETRINA / INGRESSO (posizione porta da rilevare)', (min(xs) + max(xs)) / 2, max(ys) + 2.5 * SCALE,
          'TEXT', TXT, TextEntityAlignment.BOTTOM_CENTER)
    label(m, 'PARETE DI FONDO', (min(xs) + max(xs)) / 2, min(ys) - 1.2 * SCALE, 'TEXT', TXT * 0.9,
          TextEntityAlignment.TOP_CENTER)


def dims_envelope(m, model):
    v = model['envelope']['vertices']
    st = mark(model['envelope']['status'])
    xs = [p[0] for p in v]
    ys = [p[1] for p in v]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    off = 12 * SCALE
    # Totale lungo X sopra la vetrina, totale lungo Y a sinistra
    dim(m, (x0, y1), (x1, y1), (0, y1 + off), 'DIM_ENVELOPE', 0, st)
    dim(m, (x0, y0), (x0, y1), (x0 - off, 0), 'DIM_ENVELOPE', 90, st)
    # Ogni lato del perimetro, catena interna
    for (ax, ay), (bx, by) in zip(v, v[1:] + v[:1]):
        if ay == by and ay not in (y1,):
            dim(m, (ax, ay), (bx, by), (0, ay - 6 * SCALE if ay == y0 else ay - 3 * SCALE), 'DIM_ENVELOPE', 0, st)
        elif ax == bx and ax != x0:
            dim(m, (ax, ay), (bx, by), (ax + 6 * SCALE, 0), 'DIM_ENVELOPE', 90, st)


def dims_furniture(m, model):
    for f in model['furniture']:
        x0, y0, x1, y1 = bounds(f)
        st = mark(f['status'])
        dim(m, (x0, y1), (x1, y1), (0, y1 + 2 * SCALE), 'DIM_FURNITURE', 0, st)
        dim(m, (x1, y0), (x1, y1), (x1 + 2 * SCALE, 0), 'DIM_FURNITURE', 90, st)


def dims_clearances(m, model):
    """Distanze libere fra elementi affacciati (quota magenta)."""
    seen = set()
    for r in clearances(model):
        if r['mm'] <= ACCOSTATO_MM or r['axis'] not in ('x', 'y'):
            continue
        a, b = r['ra'], r['rb']
        if r['axis'] == 'x':
            lo, hi = (a, b) if a[2] <= b[0] else (b, a)
            ys = max(lo[1], hi[1]), min(lo[3], hi[3])
            y = (ys[0] + ys[1]) / 2
            key = ('x', lo[2], hi[0], round(y, -2))
            if key in seen:
                continue
            seen.add(key)
            dim(m, (lo[2], y), (hi[0], y), (0, y), 'DIM_CLEARANCE', 0, ' libero')
        else:
            lo, hi = (a, b) if a[3] <= b[1] else (b, a)
            xs = max(lo[0], hi[0]), min(lo[2], hi[2])
            x = (xs[0] + xs[1]) / 2
            key = ('y', lo[3], hi[1], round(x, -2))
            if key in seen:
                continue
            seen.add(key)
            dim(m, (x, lo[3]), (x, hi[1]), (x, 0), 'DIM_CLEARANCE', 90, ' libero')


def draw_furniture(m, model, with_labels=True):
    for f in model['furniture']:
        r = bounds(f)
        layer = FURN_LAYER[f['status']]
        rectangle(m, r, layer)
        if with_labels:
            cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
            t = label(m, f['id'], cx, cy, layer, TXT, TextEntityAlignment.MIDDLE_CENTER)
            if f['depth'] > f['width'] * 1.5:
                t.dxf.rotation = 90


def sheet(doc, name, title, legend, model, limits):
    """Layout A3 con viewport 1:50, cartiglio e legenda."""
    lay = doc.layouts.new(name)
    lay.page_setup(size=SHEET, margins=(0, 0, 0, 0), units='mm')
    W, H = SHEET
    lay.add_lwpolyline([(10, 10), (W - 10, 10), (W - 10, H - 10), (10, H - 10)], close=True,
                       dxfattribs={'layer': 'SHEET', 'lineweight': 50})
    # Area disegno a sinistra, colonna cartiglio a destra
    col = W - 10 - 110
    lay.add_line((col, 10), (col, H - 10), dxfattribs={'layer': 'SHEET'})
    xmin, ymin, xmax, ymax = limits
    cx, cy = (xmin + xmax) / 2, (ymin + ymax) / 2
    vw, vh = col - 20, H - 30
    lay.add_viewport(center=(10 + 5 + vw / 2, 15 + vh / 2 + 5), size=(vw, vh),
                     view_center_point=(cx, cy), view_height=vh * SCALE)

    def t(s, x, y, h=2.5, layer='TEXT', align=TextEntityAlignment.LEFT):
        e = lay.add_text(s, height=h, dxfattribs={'layer': layer, 'style': 'OpenSans'})
        e.set_placement((x, y), align=align)

    x = col + 5
    y = H - 20
    t('LIMPIDIA', x, y, 6)
    y -= 7
    t('Via Andrea Solari 3, Milano', x, y, 2.8)
    y -= 10
    t(name, x, y, 9)
    y -= 7
    for line in title:
        t(line, x, y, 3.2)
        y -= 5
    y -= 4
    t('LEGENDA', x, y, 3)
    y -= 6
    for color, text in legend:
        lay.add_line((x, y + 1), (x + 8, y + 1), dxfattribs={'color': color, 'lineweight': 50})
        t(text, x + 11, y, 2.4)
        y -= 5
    y -= 3
    for line in ['* quota non verificata (ipotesi, catalogo o da definire).',
                 'Le misure derivano da config/geometry.json',
                 f"rev. modello {model['revision']}. Unità mm.",
                 'Simboli elettrici = utenze, non circuiti.']:
        t(line, x, y, 2.2)
        y -= 4.2
    # Cartiglio in basso
    yb = 62
    lay.add_line((col, yb), (W - 10, yb), dxfattribs={'layer': 'SHEET'})
    rows = [('Scala', '1:50 su A3'), ('Revisione', model['revision']), ('Data', dt.date.today().isoformat()),
            ('Stato', 'PRELIMINARE'), ('Validazione', 'da tecnico incaricato')]
    yy = yb - 7
    for k, v in rows:
        t(k, x, yy, 2.4)
        t(v, x + 30, yy, 2.8)
        yy -= 6
    t(WARNING, x, 16, 3.4, 'WARNING')
    return lay


def plot_limits(model):
    xs = [v[0] for v in model['envelope']['vertices']]
    ys = [v[1] for v in model['envelope']['vertices']]
    pad = 18 * SCALE
    return min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad


def export_pdf(doc, layout_name, path):
    """PDF vettoriale del layout di stampa (richiede PyMuPDF)."""
    try:
        from ezdxf.addons.drawing import Frontend, RenderContext, pymupdf, layout, config
    except ImportError:
        return None
    lay = doc.layouts.get(layout_name)
    backend = pymupdf.PyMuPdfBackend()
    cfg = config.Configuration(background_policy=config.BackgroundPolicy.WHITE,
                               color_policy=config.ColorPolicy.COLOR,
                               lineweight_scaling=1.0)
    Frontend(RenderContext(doc), backend, config=cfg).draw_layout(lay, finalize=True)
    page = layout.Page(*SHEET, layout.Units.mm)
    path.write_bytes(backend.get_pdf_bytes(page, settings=layout.Settings(scale=1, fit_page=False)))
    return path


LEGEND_A01 = [(7, 'Perimetro locale (ipotesi)'), (8, 'Zone fisse: scala, saletta'), (30, 'Mobile, misure ipotesi'),
              (3, 'Mobile da catalogo'), (1, 'Mobile da definire'), (6, f'Distanza libera (soglia {PASSAGGIO_MM})')]
LEGEND_E01 = [(7, 'Perimetro locale (ipotesi)'), (30, 'Ingombro mobili'), (5, 'Punto utenza (quota Z da rilevare)')]


def build_a01(model):
    d = new_doc()
    m = d.modelspace()
    draw_base(m, model)
    draw_furniture(m, model)
    dims_envelope(m, model)
    dims_furniture(m, model)
    dims_clearances(m, model)
    label(m, WARNING, 0, plot_limits(model)[1] + 3 * SCALE, 'WARNING', TXT * 1.4)
    sheet(d, 'A01', ['Pianta arredi quotata', 'Piano terra'], LEGEND_A01, model, plot_limits(model))
    return d


def build_e01(model):
    d = new_doc()
    m = d.modelspace()
    draw_base(m, model)
    draw_furniture(m, model, with_labels=True)
    dims_envelope(m, model)
    rows = []
    for p in model['electrical_points']:
        m.add_circle((p['x'], p['y']), 1.6 * SCALE, dxfattribs={'layer': 'ELECTRICAL', 'lineweight': 35})
        m.add_line((p['x'] - 1.6 * SCALE, p['y']), (p['x'] + 1.6 * SCALE, p['y']), dxfattribs={'layer': 'ELECTRICAL'})
        label(m, p['id'], p['x'] + 2.2 * SCALE, p['y'] + 1.2 * SCALE, 'ELECTRICAL', TXT)
        rows.append(p)
    lim = plot_limits(model)
    label(m, WARNING + ' - SIMBOLI = UTENZE, NON CIRCUITI O PRESE DEFINITIVE', 0, lim[1] + 3 * SCALE,
          'WARNING', TXT * 1.2)
    sheet(d, 'E01', ['Punti utenza energia/dati', 'e alimentazioni LED', 'Piano terra'], LEGEND_E01, model, lim)
    lay = d.layouts.get('E01')
    # Elenco utenze nella colonna del cartiglio
    yy = 120
    e = lay.add_text('UTENZE (X, Y in mm; Z da rilevare)', height=2.6, dxfattribs={'layer': 'TEXT', 'style': 'OpenSans'})
    e.set_placement((SHEET[0] - 115, yy + 6))
    for p in rows:
        e = lay.add_text(f"{p['id']}  {p['service']}  ({p['x']}, {p['y']})", height=2.2, dxfattribs={'layer': 'ELECTRICAL', 'style': 'OpenSans'})
        e.set_placement((SHEET[0] - 115, yy))
        yy -= 4.2
    return d


def quote_da_rilevare(model):
    unresolved = [f"- {f['id']}: {f['status']} - {f.get('note', '')}" for f in model['furniture'] if f['status'] != 'verified']
    unresolved += [f"- {p['id']}: Z non verificata; utenza {p['service']}" for p in model['electrical_points'] if p['z'] is None]
    return '# Quote aperte e verifiche\n\n' + '\n'.join(unresolved) + '\n'


def generate(pdf=True):
    OUT.mkdir(exist_ok=True)
    model = load()
    for name, builder, fname in [('A01', build_a01, 'A01_pianta_arredi_preliminare'),
                                 ('E01', build_e01, 'E01_punti_utenza_preliminari')]:
        d = builder(model)
        d.saveas(OUT / f'{fname}.dxf')
        if pdf:
            export_pdf(d, name, OUT / f'{fname}.pdf')
    (OUT / 'quote_da_rilevare.md').write_text(quote_da_rilevare(model), encoding='utf-8')
    write_report(model, OUT / 'criticita.md')
    return OUT


if __name__ == '__main__':
    print(generate())
