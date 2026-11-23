"""Geometria 3D unica dei componenti (mm): la usano prospetti, abaco, controlli e render.

Ogni componente è un parallelepipedo allineato agli assi con:
  id, owner (mobile o gruppo), kind, mat (chiave di finitura per il render), box
  (x0, y0, z0, x1, y1, z1), host (ID della faccia di parete o None), status, joint.

Regole:
- width/depth/height dei mobili sono ingombri ESTERNI: tutte le parti stanno dentro.
- Le quote Z hanno un riferimento esplicito (base, asse o sommità) nel modello.
- joint = 'inlay' indica un elemento incassato nella parte che lo ospita (profilo LED
  in una fresata, marchio stampato, immagine nel telaio): l'intersezione è voluta.
- Le intersezioni fra pezzi da costruire sono vietate; i raccordi (mensola interrotta
  sul cubotto) sono risolti nella geometria e documentati in D01.
"""
from .model import bounds, host_face, back_side, smart_layout, smart_wall_geom, faces


def _c(cid, owner, kind, mat, box, host=None, status='assumed', joint=None, **extra):
    x0, y0, z0, x1, y1, z1 = box
    b = (min(x0, x1), min(y0, y1), min(z0, z1), max(x0, x1), max(y0, y1), max(z0, z1))
    return {'id': cid, 'owner': owner, 'kind': kind, 'mat': mat, 'box': b, 'host': host,
            'status': status, 'joint': joint, **extra}


# Direzione "da sinistra a destra" guardando il fronte del mobile
_RIGHT = {'-y': (1, 0), '+y': (-1, 0), '-x': (0, -1), '+x': (0, 1)}


class WallFrame:
    """Coordinate locali di un oggetto addossato a una parete: u lungo la parete, d dal retro."""

    def __init__(self, item):
        x0, y0, x1, y1 = bounds(item)
        self.front = item['front']
        rx, ry = _RIGHT[self.front]
        if rx:
            self.ax, self.p0, self.p1 = 'x', (x0 if rx > 0 else x1), (x1 if rx > 0 else x0)
        else:
            self.ax, self.p0, self.p1 = 'y', (y0 if ry > 0 else y1), (y1 if ry > 0 else y0)
        self.nax, self.back, self.s = {'-y': ('y', y1, -1), '+y': ('y', y0, 1),
                                       '-x': ('x', x1, -1), '+x': ('x', x0, 1)}[self.front]
        self.depth = (y1 - y0) if self.ax == 'x' else (x1 - x0)
        self.sg = 1 if self.p1 > self.p0 else -1

    def u(self, t, off=0):
        """Punto a frazione t lungo il mobile (sinistra→destra), più offset in mm verso destra."""
        return self.p0 + (self.p1 - self.p0) * t + self.sg * off

    def box(self, u0, u1, d0, d1, z0, z1):
        a0, a1 = self.back + self.s * d0, self.back + self.s * d1
        if self.ax == 'x':
            return (u0, a0, z0, u1, a1, z1)
        return (a0, u0, z0, a1, u1, z1)


def furniture_components(model, f):
    P = model['furniture_parts']
    st = f['status']
    h = f['height']
    fid = f['id']
    host = host_face(model, f)
    x0, y0, x1, y1 = bounds(f)
    out = []
    if fid == 'CASSA':
        c = P['cassa']
        wf = WallFrame(f)
        out.append(_c(fid + '_zoccolo', fid, 'plinth', 'metal',
                      wf.box(wf.u(0, c['plinth_inset']), wf.u(1, -c['plinth_inset']), c['plinth_inset'], wf.depth - c['plinth_inset'],
                             0, c['plinth_height']), host, st))
        out.append(_c(fid + '_corpo', fid, 'body', 'cassa',
                      wf.box(wf.u(0), wf.u(1), 0, wf.depth - 1, c['plinth_height'], h - c['top_thickness']), host, st))
        out.append(_c(fid + '_top', fid, 'top', 'white', wf.box(wf.u(0), wf.u(1), 0, wf.depth, h - c['top_thickness'], h), host, st))
        lw = (x1 - x0 if wf.ax == 'x' else y1 - y0) * 0.55
        mid = wf.u(0.5)
        zc = (c['plinth_height'] + h - c['top_thickness']) * 0.6
        lh = lw * 438 / 1380
        out.append(_c(fid + '_marchio', fid, 'logo', 'logo',
                      wf.box(mid - wf.sg * lw / 2, mid + wf.sg * lw / 2, wf.depth - 1, wf.depth - 0.5, zc - lh / 2, zc + lh / 2),
                      host, 'catalog', 'inlay', asset='assets/brand/limpidia.png'))
    elif fid == 'ISOLA_SMART':
        t = P['isola']['top_thickness']
        out.append(_c(fid + '_corpo', fid, 'body', 'island', (x0, y0, 0, x1, y1, h - t), host, st))
        out.append(_c(fid + '_top', fid, 'top', 'white', (x0, y0, h - t, x1, y1, h), host, st))
    elif fid == 'SCRIVANIA':
        d = P['scrivania']
        t, ins, pl, pt = d['top_thickness'], d['inset'], d['pedestal_length'], d['panel_thickness']
        out.append(_c(fid + '_piano', fid, 'top', 'desk', (x0, y0, h - t, x1, y1, h), host, st))
        if (y1 - y0) >= (x1 - x0):   # lato lungo su Y
            out.append(_c(fid + '_cassettiera', fid, 'body', 'white', (x0 + ins, y0 + ins, 0, x1 - ins, y0 + ins + pl, h - t), host, st))
            out.append(_c(fid + '_fianco', fid, 'body', 'white', (x0 + ins, y1 - ins - pt, 0, x1 - ins, y1 - ins, h - t), host, st))
        else:
            out.append(_c(fid + '_cassettiera', fid, 'body', 'white', (x0 + ins, y0 + ins, 0, x0 + ins + pl, y1 - ins, h - t), host, st))
            out.append(_c(fid + '_fianco', fid, 'body', 'white', (x1 - ins - pt, y0 + ins, 0, x1 - ins, y1 - ins, h - t), host, st))
    else:  # cassettiere
        c = P['drawers']
        led = model['display_proposal']['drawer_led']
        wf = WallFrame(f)
        pi = c['plinth_inset']
        out.append(_c(fid + '_zoccolo', fid, 'plinth', 'metal',
                      wf.box(wf.u(0, pi), wf.u(1, -pi), 0, wf.depth - 30, 0, c['plinth_height']), host, st))
        out.append(_c(fid + '_corpo', fid, 'body', 'drawers', wf.box(wf.u(0), wf.u(1), 0, wf.depth, c['plinth_height'], h), host, st))
        for k, fr in enumerate(led['axes_fraction']):
            zz = h * fr
            out.append(_c(f'{fid}_led_{k+1}', fid, 'led', 'led',
                          wf.box(wf.u(0, led['inset']), wf.u(1, -led['inset']), wf.depth - led['groove_depth'], wf.depth,
                                 zz - led['height'] / 2, zz + led['height'] / 2), host, led['status'], 'inlay', axis_z=zz))
    return out


def display_components(model):
    dp = model.get('display_proposal', {})
    if not dp:
        return []
    furn = {f['id']: f for f in model['furniture']}
    out = []
    D, TH, stg = dp['shelf_depth'], dp['shelf_thickness'], dp['stagger']
    cb = dp['cubby']
    sl = dp['shelf_led']
    for fid in dp.get('over', []):
        f = furn[fid]
        wf = WallFrame(f)
        host = host_face(model, f)
        own = 'ESP_' + fid
        levels = dp['shelf_levels']
        # cubotto sulla mensola di indice 1, a 0.62 della sua lunghezza
        cubby = None
        if len(levels) > 1:
            off = stg
            a, b = wf.u(0, off), wf.u(1, off - stg)
            ca = a + (b - a) * 0.62
            cbb = ca + wf.sg * cb['size']
            zc = levels[1] + TH
            cubby = (min(ca, cbb), max(ca, cbb), zc, zc + cb['size'])
        for li, z in enumerate(levels):
            off = stg if li % 2 else 0
            ua, ub = wf.u(0, off), wf.u(1, off - stg)
            clr = dp.get('end_clearance', {}).get(fid, {})
            if clr.get('right'):   # fine mensola arretrata dal lato destro (dato esplicito del modello)
                lim = wf.u(1, -clr['right'])
                ub = min(ub, lim) if wf.sg > 0 else max(ub, lim)
            if clr.get('left'):
                lim = wf.u(0, clr['left'])
                ua = max(ua, lim) if wf.sg > 0 else min(ua, lim)
            a, b = sorted((ua, ub))
            pieces = [(a, b)]
            if cubby and z < cubby[3] and z + TH > cubby[2]:
                # raccordo: mensola interrotta sui fianchi del cubotto (D01)
                pieces = [(a, cubby[0]), (cubby[1], b)]
            for k, (pa, pb) in enumerate(pieces):
                if pb - pa < 50:
                    continue
                tag = f'{fid}_mensola_{li+1}' + ('' if len(pieces) == 1 else 'ab'[k])
                out.append(_c(tag, own, 'shelf', 'shelves', wf.box(pa, pb, 0, D, z, z + TH), host, dp['status'],
                              z_ref='base', joint_note='interrotta sul cubotto' if len(pieces) > 1 else None))
                out.append(_c(tag + '_led', own, 'led', 'led', wf.box(pa + sl['inset'], pb - sl['inset'], sl['inset'], D - sl['inset'],
                                                                     z - sl['height'], z), host, sl['status']))
        if cubby:
            u0, u1, z0, z1 = cubby
            bd, dep = cb['board'], cb['depth']
            parts = {'fianco_sx': wf.box(u0, u0 + bd, 0, dep, z0, z1), 'fianco_dx': wf.box(u1 - bd, u1, 0, dep, z0, z1),
                     'fondo': wf.box(u0 + bd, u1 - bd, 0, bd, z0, z1), 'base': wf.box(u0 + bd, u1 - bd, bd, dep, z0, z0 + bd),
                     'cielo': wf.box(u0 + bd, u1 - bd, bd, dep, z1 - bd, z1)}
            for name, box in parts.items():
                out.append(_c(f'{fid}_cubotto_{name}', own, 'cubby', 'oak', box, host, dp['status']))
            out.append(_c(f'{fid}_cubotto_led', own, 'led', 'led', wf.box(u0 + bd, u1 - bd, bd, dep - 20, z1 - bd - 6, z1 - bd),
                          host, sl['status']))
    # Colonne listelli + specchio
    sm = dp.get('slat_mirror')
    H = model['ceiling']['height']
    top = H - sm['top_gap_from_ceiling'] if sm else None
    for c in dp.get('slat_columns', []):
        x0, y0, x1, y1 = bounds(c)
        wide_x = (x1 - x0) >= (y1 - y0)
        front = {True: ('-y' if _near_wall(model, c, 'y1') else '+y'), False: ('-x' if _near_wall(model, c, 'x1') else '+x')}[wide_x]
        item = dict(c, front=front)
        wf = WallFrame(item)
        host = host_face(model, item)
        k = 0
        umin, umax = min(wf.p0, wf.p1), max(wf.p0, wf.p1)
        n = int((umax - umin + sm['slat_gap']) // (sm['slat'] + sm['slat_gap']))
        used = n * sm['slat'] + (n - 1) * sm['slat_gap']
        u = umin + (umax - umin - used) / 2          # gruppo di listelli centrato sulla colonna
        while k < n:
            out.append(_c(f"{c['id']}_listello_{k+1}", c['id'], 'slat', 'oak', wf.box(u, u + sm['slat'], 0, sm['slat_depth'], 0, top),
                          host, c['status'], z_ref='sommità = soffitto - top_gap_from_ceiling'))
            u += sm['slat'] + sm['slat_gap']
            k += 1
        mid = wf.u(0.5)
        mw, pl, mt = sm['mirror_width'], sm['mirror_plate'], sm['mirror_thickness']
        zb, zt = sm['mirror_bottom'], sm['mirror_bottom'] + sm['mirror_height']
        out.append(_c(f"{c['id']}_piastra", c['id'], 'frame', 'metal',
                      wf.box(mid - mw / 2 - 15, mid + mw / 2 + 15, sm['slat_depth'], sm['slat_depth'] + pl, zb - 15, zt + 15), host, c['status']))
        out.append(_c(f"{c['id']}_specchio", c['id'], 'mirror', 'mirror',
                      wf.box(mid - mw / 2, mid + mw / 2, sm['slat_depth'] + pl, sm['slat_depth'] + pl + mt, zb, zt), host, c['status']))
    return out


def _near_wall(model, c, side):
    x0, y0, x1, y1 = bounds(c)
    v = {'x0': x0, 'x1': x1, 'y0': y0, 'y1': y1}[side]
    for f in faces(model).values():
        ax = 'x' if side.startswith('y') else 'y'
        if f['axis'] == ax and abs(f['fixed'] - v) <= 30:
            return True
    return False


def smart_components(model):
    if 'smart_wall' not in model:
        return []
    sw = model['smart_wall']
    g = smart_wall_geom(model)
    L = smart_layout(model)
    p = sw['panels']
    host = next((fid for fid, f in faces(model).items() if f['axis'] == 'y' and f['fixed'] == g['face_x'] and f['n'] == (-1, 0)), None)
    face = g['cladding_face']
    H = model['ceiling']['height']
    out = [_c('SMART_rivestimento', 'SMART', 'cladding', 'brick', (face, g['y0'], 0, g['face_x'], g['y1'], H), host,
              sw['cladding']['status'])]
    for k, (ya, yb) in enumerate(L['panels']):
        n = k + 1
        z0, z1 = p['bottom'], p['bottom'] + p['height']
        fb = p['frame_border']
        out.append(_c(f'SMART_telaio_{n}', 'SMART', 'frame', 'metal', (face - p['frame_depth'], ya, z0, face, yb, z1), host, p['status'],
                      title=sw['panel_titles'][k]))
        out.append(_c(f'SMART_immagine_{n}', 'SMART', 'image', 'panel', (face - p['frame_depth'], ya + fb, z0 + fb,
                                                                          face - p['frame_depth'] + 1, yb - fb, z1 - fb),
                      host, sw['images']['status'], 'inlay', title=sw['panel_titles'][k], placeholder=True))
        s = sw['shelf']
        cy = (ya + yb) / 2
        out.append(_c(f'SMART_ripiano_{n}', 'SMART', 'shelf', 'oak', (face - s['depth'], cy - s['width'] / 2, s['z'],
                                                                      face, cy + s['width'] / 2, s['z'] + s['thickness']), host, s['status'], z_ref='base'))
        lb = sw['label']
        out.append(_c(f'SMART_cartellino_{n}', 'SMART', 'label', 'white', (face - lb['depth'], cy - lb['width'] / 2, lb['z'],
                                                                           face, cy + lb['width'] / 2, lb['z'] + lb['height']),
                      host, lb['status'], z_ref='base', text=sw.get('label_texts', [''] * 4)[k]))
    return out


def all_components(model):
    out = []
    for f in model['furniture']:
        out += furniture_components(model, f)
    out += display_components(model)
    out += smart_components(model)
    return out


def by_owner(comps, owner):
    return [c for c in comps if c['owner'] == owner]


def union_bounds(comps):
    bs = [c['box'] for c in comps]
    return (min(b[0] for b in bs), min(b[1] for b in bs), min(b[2] for b in bs),
            max(b[3] for b in bs), max(b[4] for b in bs), max(b[5] for b in bs))


def overlap_volume(a, b):
    dx = min(a[3], b[3]) - max(a[0], b[0])
    dy = min(a[4], b[4]) - max(a[1], b[1])
    dz = min(a[5], b[5]) - max(a[2], b[2])
    return dx * dy * dz if dx > 0 and dy > 0 and dz > 0 else 0.0


def unexplained_overlaps(comps, tol=1.0):
    """Coppie di pezzi che si compenetrano senza un raccordo dichiarato (inlay)."""
    bad = []
    solid = [c for c in comps if c['joint'] != 'inlay']
    for i, a in enumerate(solid):
        for b in solid[i + 1:]:
            if overlap_volume(a['box'], b['box']) > tol:
                bad.append((a['id'], b['id']))
    return bad
