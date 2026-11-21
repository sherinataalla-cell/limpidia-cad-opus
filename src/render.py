"""Anteprima 3D dal modello parametrico (Blender/Cycles via `bpy`).

Uso:  python -m src.render            (tutte le inquadrature)
      python -m src.render --fast     (bozza veloce)

Tutta la geometria (involucro, facciata, tramezzi, porte, saletta, parete smart,
mobili con fronte e altezza, mensole e colonne listelli della proposta, soffitto)
viene da config/geometry.json, la stessa fonte delle tavole. config/render.json
contiene solo parametri visivi (colori, luci, camere) e ipotesi grafiche che le
tavole non usano. È un'anteprima: NON è una fonte metrica.
"""
import json
import math
import sys

from .model import (load, bounds, rect_cells, floor_poly, smart_layout, envelope_edges, outward,
                    ROOT, OUT)

RENDER_CFG = ROOT / 'config' / 'render.json'
LOGO = ROOT / 'assets' / 'brand' / 'limpidia.png'
MM = 0.001


def _bpy():
    try:
        import bpy  # noqa: F401
        return bpy
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("Serve il modulo Blender: pip install bpy (Python 3.11-3.13)") from exc


# --- Materiali ----------------------------------------------------------------

def material(bpy, name, color, roughness=0.5, emission=None, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = roughness
    p.inputs['Metallic'].default_value = metallic
    if emission:
        p.inputs['Emission Color'].default_value = (*emission[0], 1)
        p.inputs['Emission Strength'].default_value = emission[1]
    return m


def clear_glass(bpy, name='vetro', fac=0.04):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    gl = nt.nodes.new('ShaderNodeBsdfGlossy')
    gl.inputs['Roughness'].default_value = 0.02
    mix = nt.nodes.new('ShaderNodeMixShader')
    mix.inputs['Fac'].default_value = fac
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(gl.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs['Surface'])
    return m


def mirror(bpy):
    return material(bpy, 'specchio', (0.9, 0.9, 0.9), 0.02, metallic=1.0)


def wood(bpy, name, color, roughness, scale=6.0, axis='x'):
    """Venatura procedurale lungo l'asse indicato (coordinate mondo, non deformate dalla scala)."""
    m = material(bpy, name, color, roughness)
    nt = m.node_tree
    p = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeNewGeometry')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = {'x': (0.6, 6, 0.6), 'y': (6, 0.6, 0.6), 'z': (6, 6, 0.6)}[axis]
    wave = nt.nodes.new('ShaderNodeTexWave')
    wave.inputs['Scale'].default_value = scale
    wave.inputs['Distortion'].default_value = 2.5
    wave.inputs['Detail'].default_value = 4
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (*[c * 0.82 for c in color], 1)
    ramp.color_ramp.elements[1].color = (*color, 1)
    nt.links.new(tc.outputs['Position'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], wave.inputs['Vector'])
    nt.links.new(wave.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], p.inputs['Base Color'])
    return m


def brick(bpy, name, color, mortar, plane='yz'):
    m = material(bpy, name, color, 0.85)
    nt = m.node_tree
    p = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeNewGeometry')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    mp = nt.nodes.new('ShaderNodeCombineXYZ')  # mattoni sul piano della parete
    nt.links.new(tc.outputs['Position'], sep.inputs['Vector'])
    a, b, c = ('Y', 'Z', 'X') if plane == 'yz' else ('X', 'Z', 'Y')
    nt.links.new(sep.outputs[a], mp.inputs['X'])
    nt.links.new(sep.outputs[b], mp.inputs['Y'])
    nt.links.new(sep.outputs[c], mp.inputs['Z'])
    t = nt.nodes.new('ShaderNodeTexBrick')
    t.inputs['Color1'].default_value = (*color, 1)
    t.inputs['Color2'].default_value = (*[k * 0.78 for k in color], 1)
    t.inputs['Mortar'].default_value = (*mortar, 1)
    t.inputs['Scale'].default_value = 1.0
    t.inputs['Mortar Size'].default_value = 0.010
    t.inputs['Brick Width'].default_value = 0.25
    t.inputs['Row Height'].default_value = 0.065
    nt.links.new(mp.outputs['Vector'], t.inputs['Vector'])
    nt.links.new(t.outputs['Color'], p.inputs['Base Color'])
    return m


def logo_material(bpy, base):
    """Marchio ufficiale (assets/brand/limpidia.png) sul fondo del materiale indicato."""
    m = material(bpy, 'marchio', base, 0.3)
    if not LOGO.exists():
        return m
    nt = m.node_tree
    p = nt.nodes['Principled BSDF']
    img = nt.nodes.new('ShaderNodeTexImage')
    img.image = bpy.data.images.load(str(LOGO))
    img.extension = 'CLIP'
    mix = nt.nodes.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    mix.inputs['A'].default_value = (*base, 1)
    nt.links.new(img.outputs['Alpha'], mix.inputs['Factor'])
    nt.links.new(img.outputs['Color'], mix.inputs['B'])
    nt.links.new(mix.outputs['Result'], p.inputs['Base Color'])
    return m


# --- Primitive ----------------------------------------------------------------

def box(bpy, name, x0, y0, z0, x1, y1, z1, mat):
    """Parallelepipedo da coordinate in mm (ordine qualsiasi)."""
    x0, x1 = sorted((x0, x1))
    y0, y1 = sorted((y0, y1))
    z0, z1 = sorted((z0, z1))
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.active_object
    o.name = name
    o.scale = ((x1 - x0) * MM, (y1 - y0) * MM, (z1 - z0) * MM)
    o.location = ((x0 + x1) / 2 * MM, (y0 + y1) / 2 * MM, (z0 + z1) / 2 * MM)
    o.data.materials.append(mat)
    return o


def plane(bpy, name, center, size, normal, mat):
    """Rettangolo verticale (size = larghezza, altezza in mm) con normale '-y' o '-x' ecc."""
    bpy.ops.mesh.primitive_plane_add(size=1)
    o = bpy.context.active_object
    o.name = name
    o.scale = (size[0] * MM, size[1] * MM, 1)
    o.location = tuple(c * MM for c in center)
    rot = {'-y': (90, 0, 0), '+y': (90, 0, 180), '-x': (90, 0, -90), '+x': (90, 0, 90)}[normal]
    o.rotation_euler = tuple(math.radians(r) for r in rot)
    o.data.materials.append(mat)
    return o


def label(bpy, text, center, normal, size, mat):
    """Testo rivolto verso `normal`, centrato in `center` (mm)."""
    bpy.ops.object.text_add(location=tuple(c * MM for c in center))
    o = bpy.context.active_object
    o.data.body = text
    o.data.size = size * MM
    o.data.align_x = 'CENTER'
    o.data.align_y = 'CENTER'
    o.data.extrude = 0.0004
    rot = {'-y': (90, 0, 0), '+y': (90, 0, 180), '-x': (90, 0, -90), '+x': (90, 0, 90)}[normal]
    o.rotation_euler = tuple(math.radians(r) for r in rot)
    o.data.materials.append(mat)
    return o


def look_at(obj, target):
    from mathutils import Vector
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


# Direzione "da sinistra a destra" guardando il fronte del mobile (come nei prospetti F01-F04)
_RIGHT = {'-y': (1, 0), '+y': (-1, 0), '-x': (0, -1), '+x': (0, 1)}


def along(item):
    """Estremi del mobile lungo la parete, ordinati da sinistra a destra guardando il fronte."""
    x0, y0, x1, y1 = bounds(item)
    rx, ry = _RIGHT[item['front']]
    if rx:
        return ('x', (x0, x1) if rx > 0 else (x1, x0))
    return ('y', (y0, y1) if ry > 0 else (y1, y0))


def back_plane(item):
    """Coordinata del retro e verso del fronte (+1/-1) sull'asse normale alla parete."""
    x0, y0, x1, y1 = bounds(item)
    return {'-y': ('y', y1, -1), '+y': ('y', y0, 1), '-x': ('x', x1, -1), '+x': ('x', x0, 1)}[item['front']]


def wall_box(bpy, name, item, u0, u1, d0, d1, z0, z1, mat):
    """Box definito lungo la parete (u) e in profondità dal retro (d), per qualsiasi fronte."""
    ax, _ = along(item)
    nax, back, s = back_plane(item)
    a0, a1 = back + s * d0, back + s * d1
    if ax == 'x':
        return box(bpy, name, u0, a0, z0, u1, a1, z1, mat)
    return box(bpy, name, a0, u0, z0, a1, u1, z1, mat)


def u_at(item, t, off=0):
    """Punto a frazione t lungo il mobile (sinistra→destra guardando il fronte), più offset in mm."""
    _, (p0, p1) = along(item)
    sgn = 1 if p1 > p0 else -1
    return p0 + (p1 - p0) * t + sgn * off


# --- Scena --------------------------------------------------------------------

def build_scene(bpy, model, cfg):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    F = cfg['finishes']
    M = {
        'walls': material(bpy, 'pareti', F['walls']['color'], F['walls']['roughness']),
        'floor': wood(bpy, 'pavimento', F['floor']['color'], F['floor']['roughness'], 3.0, 'y'),
        'drawers': wood(bpy, 'noce_scuro', F['drawers']['color'], F['drawers']['roughness']),
        'shelves': material(bpy, 'mensole', F['shelves']['color'], F['shelves']['roughness']),
        'oak': wood(bpy, 'rovere', F['cubes']['color'], F['cubes']['roughness'], 8.0, 'z'),
        'cassa': material(bpy, 'cassa', F['cassa']['color'], F['cassa']['roughness']),
        'desk': wood(bpy, 'scrivania', F['desk']['color'], F['desk']['roughness']),
        'white': material(bpy, 'bianco', (0.93, 0.93, 0.92), 0.35),
        'island': material(bpy, 'isola', F['island']['color'], F['island']['roughness']),
        'brick': brick(bpy, 'mattoni', F['brick']['color'], F['brick']['mortar']),
        'ceiling': material(bpy, 'soffitto', F['ceiling']['color'], F['ceiling']['roughness']),
        'glass': clear_glass(bpy),
        'mirror': mirror(bpy),
        'metal': material(bpy, 'metallo', (0.12, 0.12, 0.12), 0.35, metallic=0.6),
        'steel': material(bpy, 'acciaio', (0.7, 0.7, 0.7), 0.25, metallic=1.0),
        'void': material(bpy, 'vano_scala', (0.03, 0.03, 0.03), 1.0),
        'led': material(bpy, 'led', (1, 1, 1), 0.5, emission=((1.0, 0.82, 0.6), 10)),
        'panel': material(bpy, 'pannello_smart', (0.04, 0.05, 0.07), 0.2, emission=((0.55, 0.65, 0.85), 1.2)),
        'ink': material(bpy, 'scritte', (0.95, 0.95, 0.95), 0.4, emission=((1, 1, 1), 1.5)),
        'ink_dark': material(bpy, 'scritte_scure', (0.08, 0.08, 0.08), 0.5),
        'door': material(bpy, 'porta', (0.94, 0.94, 0.93), 0.3),
        'logo': logo_material(bpy, tuple(F['cassa']['color'])),
    }
    H = model['ceiling']['height']
    T = cfg['wall_thickness']
    V = cfg['visual_assumptions']
    verts = model['envelope']['vertices']
    xs = [v[0] for v in verts]
    ys = [v[1] for v in verts]
    X0, X1, Y0, Y1 = min(xs), max(xs), min(ys), max(ys)

    # Pavimento dal poligono reale (concavità e foro scala) e soffitto
    for k, (a, b, c, d) in enumerate(rect_cells(floor_poly(model))):
        box(bpy, f'pavimento_{k}', a, b, -40, c, d, 0, M['floor'])
    ceil = box(bpy, 'soffitto', X0 - T, Y0 - T, H, X1 + T, Y1 + T, H + 50, M['ceiling'])

    # Scala: gradini in discesa (ipotesi visiva: n. e alzata non rilevati)
    st = next(z for z in model['room_features'] if z['id'] == 'SCALE')
    sx0, sy0, sx1, sy1 = bounds(st)
    tread, rise = V['stair_tread'], V['stair_rise']
    n = int((sy1 - sy0) // tread)
    for k in range(n):
        ya = sy1 - (k + 1) * tread
        box(bpy, f'gradino_{k}', sx0, ya, -(k + 1) * rise - 40, sx1, ya + tread, -(k + 1) * rise, M['floor'])
        box(bpy, f'gradino_led_{k}', sx0 + 20, ya + tread - 15, -(k + 1) * rise - 8, sx1 - 20, ya + tread - 5,
            -(k + 1) * rise - 2, M['led'])
    box(bpy, 'vano_scala', sx0, sy0, -n * rise - 600, sx1, sy1, -n * rise - 500, M['void'])

    # Perimetro: pareti estruse verso l'esterno, tranne la facciata (elementi propri)
    for i, (a, b) in enumerate(envelope_edges(verts)):
        (ax, ay), (bx, by) = a, b
        nx, ny = outward(a, b, verts)
        if ay == by == Y0:
            continue
        if ay == by:
            box(bpy, f'muro_{i}', min(ax, bx) - T, ay, 0, max(ax, bx) + T, ay + ny * T, H + 1, M['walls'])  # +1: niente facce coincidenti negli angoli
        else:
            box(bpy, f'muro_{i}', ax, min(ay, by) - T, 0, ax + nx * T, max(ay, by) + T, H, M['walls'])

    # Facciata: pilastri, vetrine e porta d'ingresso dal modello
    gh = V['glazing_top']
    for e in model['facade']:
        a, b = e['x0'], e['x1']
        if e['type'] == 'pier':
            box(bpy, e['id'], a, Y0 - T, 0, b, Y0, H, M['walls'])
        else:
            box(bpy, e['id'] + '_architrave', a, Y0 - T, gh, b, Y0, H, M['walls'])
            box(bpy, e['id'] + '_telaio_basso', a, Y0 - T / 2 - 30, 0, b, Y0 - T / 2 + 30, 40, M['metal'])
            box(bpy, e['id'] + '_telaio_alto', a, Y0 - T / 2 - 30, gh - 40, b, Y0 - T / 2 + 30, gh, M['metal'])
            if e['type'] == 'glazing':
                box(bpy, e['id'], a, Y0 - T / 2 - 6, 40, b, Y0 - T / 2 + 6, gh - 40, M['glass'])

    # Porte: anta aperta (posizione di apertura del modello)
    for op in model.get('openings', []):
        hx, hy = op['hinge']
        _, sy = op['swing_quadrant']
        dh = V['door_height']
        mat = M['glass'] if op['wall'] == 'facciata' else M['door']
        y_end = hy + sy * op['leaf']
        box(bpy, op['id'] + '_anta', hx - 20, hy, 0, hx + 20, y_end, dh, mat)
        if op['wall'] == 'facciata':
            box(bpy, op['id'] + '_telaio', hx - 25, hy, 0, hx + 25, y_end, 50, M['metal'])
            box(bpy, op['id'] + '_maniglia', hx - 60, y_end - 120, 900, hx + 60, y_end - 100, 1300, M['steel'])
        else:
            box(bpy, op['id'] + '_maniglia', hx - 50, y_end - 90, 1000, hx + 50, y_end - 70, 1020, M['steel'])

    # Tramezzi saletta (impronte del modello), con architrave sopra la porta
    for w in model.get('walls', []):
        x0, y0, x1, y1 = bounds(w)
        box(bpy, w['id'], x0, y0, 0, x1, y1, H, M['walls'])
    for op in model.get('openings', []):
        if op['wall'] != 'facciata':
            w = next(w for w in model['walls'] if w['id'].startswith(op['wall']))
            box(bpy, op['id'] + '_architrave', op['x0'], w['y'], V['door_height'], op['x1'], w['y'] + w['depth'], H,
                M['walls'])

    # Parete smart: rivestimento in mattoni e composizione dal modello
    sw = model['smart_wall']
    fx, cl = sw['face_x'], sw['cladding']['thickness']
    box(bpy, 'mattoni', fx - cl, sw['y0'], 0, fx, sw['y1'], H, M['brick'])
    lay = smart_layout(model)
    p = sw['panels']
    face = fx - cl
    for k, (ya, yb) in enumerate(lay['panels']):
        z0, z1 = p['bottom'], p['bottom'] + p['height']
        box(bpy, f'telaio_smart_{k+1}', face - 40, ya - 15, z0 - 15, face, yb + 15, z1 + 15, M['metal'])
        box(bpy, f'pannello_smart_{k+1}', face - 45, ya, z0, face - 40, yb, z1, M['panel'])
        title = sw['panel_titles'][k] if k < len(sw.get('panel_titles', [])) else ''
        label(bpy, title, (face - 47, (ya + yb) / 2, z1 - 70), '-x', 45, M['ink'])
        s = sw['shelf']
        box(bpy, f'mensola_smart_{k+1}', face - s['depth'], (ya + yb) / 2 - s['width'] / 2, s['z'] - 25,
            face, (ya + yb) / 2 + s['width'] / 2, s['z'], M['oak'])
        lb = sw['label']
        box(bpy, f'targhetta_smart_{k+1}', face - 8, (ya + yb) / 2 - lb['width'] / 2, lb['z'] - lb['height'],
            face, (ya + yb) / 2 + lb['width'] / 2, lb['z'], M['white'])

    # Ringhiera lungo la linea del modello (spessore non rilevato: ipotesi visiva)
    rail = next(z for z in model['room_features'] if z['id'] == 'RINGHIERA')
    rx = rail['start'][0]
    ry0, ry1 = sorted((rail['start'][1], rail['end'][1]))
    rh = V['railing_height']
    box(bpy, 'corrimano', rx - 20, ry0, rh - 40, rx + 20, ry1, rh, M['steel'])
    for k in range(int((ry1 - ry0) / 600) + 1):
        y = min(ry0 + k * 600, ry1 - 20)
        box(bpy, f'montante_{k}', rx - 15, y, -400, rx + 15, y + 20, rh - 40, M['steel'])

    # Mobili: fronte e altezza dal modello
    for f in model['furniture']:
        x0, y0, x1, y1 = bounds(f)
        h = f['height']
        fid = f['id']
        if fid == 'CASSA':
            box(bpy, fid, x0, y0, 60, x1, y1, h, M['cassa'])
            box(bpy, fid + '_zoccolo', x0 + 30, y0 + 30, 0, x1 - 30, y1 - 30, 60, M['metal'])
            box(bpy, fid + '_led', x0 + 30, y0 + 25, 50, x1 - 30, y0 + 35, 60, M['led'])
            box(bpy, fid + '_piano', x0 - 10, y0 - 10, h, x1 + 10, y1 + 10, h + 25, M['white'])
            lw = (x1 - x0) * 0.55
            plane(bpy, fid + '_marchio', ((x0 + x1) / 2, y0 - 1, h * 0.6), (lw, lw * 438 / 1380), '-y', M['logo'])
        elif fid == 'SCRIVANIA':
            box(bpy, fid + '_piano', x0, y0, h - 40, x1, y1, h, M['desk'])
            ped = V['desk_pedestal']
            box(bpy, fid + '_cassettiera', x0 + 40, y0 + 40, 0, x1 - 40, y0 + 40 + ped, h - 40, M['white'])
            box(bpy, fid + '_fianco', x0 + 40, y1 - 80, 0, x1 - 40, y1 - 40, h - 40, M['white'])
        elif fid == 'ISOLA_SMART':
            box(bpy, fid, x0, y0, 0, x1, y1, h - 30, M['island'])
            box(bpy, fid + '_piano', x0 - 10, y0 - 10, h - 30, x1 + 10, y1 + 10, h, M['white'])
        else:
            _, (u0, u1) = along(f)
            d = (y1 - y0) if f['front'] in ('-y', '+y') else (x1 - x0)  # profondità dal muro
            wall_box(bpy, fid, f, u0, u1, 0, d, 80, h, M['drawers'])
            wall_box(bpy, fid + '_zoccolo', f, u0 + (20 if u1 > u0 else -20), u1 - (20 if u1 > u0 else -20),
                     0, d - 30, 0, 80, M['metal'])
            for zz in (h * 0.36, h * 0.68):  # due linee LED sul fronte (S4)
                wall_box(bpy, fid + '_led', f, u_at(f, 0, 30), u_at(f, 1, -30), d, d + 6, zz, zz + 12, M['led'])

    # Proposta espositiva da S4 (stessi parametri dei prospetti)
    dp = model.get('display_proposal', {})
    for fid in dp.get('over', []):
        f = next(o for o in model['furniture'] if o['id'] == fid)
        D, TH, stg = dp['shelf_depth'], dp['shelf_thickness'], dp['stagger']
        for li, z in enumerate(dp['shelf_levels']):
            off = stg if li % 2 else 0
            a, b = u_at(f, 0, off), u_at(f, 1, off - stg)
            wall_box(bpy, f'{fid}_mensola_{li}', f, a, b, 0, D, z, z + TH, M['shelves'])
            wall_box(bpy, f'{fid}_led_mensola_{li}', f, u_at(f, 0, off + 20), u_at(f, 1, off - stg - 20),
                     20, D - 20, z - 6, z, M['led'])
            if li == 1:
                c = dp['cubby']
                ca = a + (b - a) * 0.62
                cb = ca + (c['size'] if b > a else -c['size'])
                zc = z + TH
                bd = c['board']
                sg = 1 if cb > ca else -1
                wall_box(bpy, f'{fid}_cubo_fondo', f, ca, cb, 0, bd, zc, zc + c['size'], M['oak'])
                wall_box(bpy, f'{fid}_cubo_sotto', f, ca, cb, 0, c['depth'], zc, zc + bd, M['oak'])
                wall_box(bpy, f'{fid}_cubo_sopra', f, ca, cb, 0, c['depth'], zc + c['size'] - bd, zc + c['size'], M['oak'])
                wall_box(bpy, f'{fid}_cubo_sx', f, ca, ca + sg * bd, 0, c['depth'], zc, zc + c['size'], M['oak'])
                wall_box(bpy, f'{fid}_cubo_dx', f, cb - sg * bd, cb, 0, c['depth'], zc, zc + c['size'], M['oak'])
                box_led = wall_box(bpy, f'{fid}_cubo_led', f, ca + sg * bd, cb - sg * bd, bd, c['depth'] - 20,
                                   zc + c['size'] - bd - 6, zc + c['size'] - bd, M['led'])
                box_led.name = f'{fid}_cubo_led'
    sm = dp.get('slat_mirror')
    for c in dp.get('slat_columns', []):
        x0, y0, x1, y1 = bounds(c)
        top = H - V['slat_top_gap']
        if c['width'] >= c['depth']:  # parete parallela a X, fronte verso -y
            k = x0
            while k + sm['slat'] <= x1 + 1:
                box(bpy, f"{c['id']}_listello", k, y0, 0, k + sm['slat'], y1, top, M['oak'])
                k += sm['slat'] + sm['slat_gap']
            mx = (x0 + x1) / 2
            box(bpy, f"{c['id']}_specchio", mx - sm['mirror_width'] / 2, y0 - 12, sm['mirror_bottom'],
                mx + sm['mirror_width'] / 2, y0 - 2, sm['mirror_bottom'] + sm['mirror_height'], M['mirror'])
            box(bpy, f"{c['id']}_cornice", mx - sm['mirror_width'] / 2 - 15, y0 - 2, sm['mirror_bottom'] - 15,
                mx + sm['mirror_width'] / 2 + 15, y0, sm['mirror_bottom'] + sm['mirror_height'] + 15, M['metal'])
        else:  # parete parallela a Y, fronte verso -x
            k = y0
            while k + sm['slat'] <= y1 + 1:
                box(bpy, f"{c['id']}_listello", x0, k, 0, x1, k + sm['slat'], top, M['oak'])
                k += sm['slat'] + sm['slat_gap']
            my = (y0 + y1) / 2
            box(bpy, f"{c['id']}_specchio", x0 - 12, my - sm['mirror_width'] / 2, sm['mirror_bottom'],
                x0 - 2, my + sm['mirror_width'] / 2, sm['mirror_bottom'] + sm['mirror_height'], M['mirror'])
            box(bpy, f"{c['id']}_cornice", x0 - 2, my - sm['mirror_width'] / 2 - 15, sm['mirror_bottom'] - 15,
                x0, my + sm['mirror_width'] / 2 + 15, sm['mirror_bottom'] + sm['mirror_height'] + 15, M['metal'])

    # Esterno minimo davanti alla vetrina
    street = material(bpy, 'strada', (0.35, 0.35, 0.36), 0.8)
    facade = material(bpy, 'facciata', (0.78, 0.74, 0.68), 0.9)
    box(bpy, 'marciapiede', X0 - 8000, Y0 - 14000, -60, X1 + 8000, Y0 - T, -40, street)
    box(bpy, 'facciata_fronte', X0 - 8000, Y0 - 14300, 0, X1 + 8000, Y0 - 14000, 15000, facade)

    # Luci: binari neri con faretti (ipotesi visiva) + plafoniere diffuse in griglia
    L = cfg['lighting']
    for k, ((ax, ay), (bx, by)) in enumerate(L['tracks']):
        box(bpy, f'binario_{k}', min(ax, bx) - 15, min(ay, by) - 15, H - 45, max(ax, bx) + 15, max(ay, by) + 15, H,
            M['metal'])
    nxl, nyl = max(2, round((X1 - X0) / 1800)), max(2, round((Y1 - Y0) / 1800))
    shop = floor_poly(model)
    from shapely.geometry import Point
    for i in range(nxl):
        for j in range(nyl):
            lx, ly = X0 + (X1 - X0) * (i + 0.5) / nxl, Y0 + (Y1 - Y0) * (j + 0.5) / nyl
            if not shop.contains(Point(lx, ly)):
                continue
            bpy.ops.object.light_add(type='AREA', location=(lx * MM, ly * MM, (H - 60) * MM))
            lo = bpy.context.active_object
            lo.data.energy = L['area_power_w']
            lo.data.size = 0.8
            lo.data.color = (1.0, 0.9, 0.78)
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 5))
    sun = bpy.context.active_object
    sun.data.energy = L['daylight']
    sun.rotation_euler = (math.radians(55), 0, math.radians(200))
    world = bpy.data.worlds.new('cielo')
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.75, 0.82, 0.92, 1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = L['daylight']
    sc.world = world
    return sc, ceil


def render(fast=False, only=None):
    bpy = _bpy()
    model = load()
    cfg = json.loads(RENDER_CFG.read_text(encoding='utf-8'))
    sc, ceil = build_scene(bpy, model, cfg)
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = 16 if fast else cfg['samples']
    sc.cycles.use_denoising = True
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Medium High Contrast'
    sc.view_settings.exposure = cfg.get('exposure', -0.6)
    rx, ry = cfg['resolution']
    sc.render.resolution_x = rx // (2 if fast else 1)
    sc.render.resolution_y = ry // (2 if fast else 1)
    sc.render.image_settings.file_format = 'PNG'
    folder = OUT / 'render'
    folder.mkdir(parents=True, exist_ok=True)
    done = []
    xs = [v[0] for v in model['envelope']['vertices']]
    ys = [v[1] for v in model['envelope']['vertices']]
    X0, X1, Y0, Y1 = min(xs), max(xs), min(ys), max(ys)

    def place(fr):
        # [frazione X, frazione Y, quota Z mm] del perimetro: le inquadrature seguono il modello
        return ((X0 + fr[0] * (X1 - X0)) * MM, (Y0 + fr[1] * (Y1 - Y0)) * MM, fr[2] * MM)

    for cam in cfg['cameras']:
        if only and cam['name'] not in only:
            continue
        top = cam.get('type') == 'top'
        ceil.hide_render = top
        if top:
            bpy.ops.object.camera_add(location=((X0 + X1) / 2 * MM, (Y0 + Y1) / 2 * MM - 0.15, 12))
            c = bpy.context.active_object
            c.data.type = 'ORTHO'
            c.data.ortho_scale = max(X1 - X0, (Y1 - Y0) * 1.2 * rx / ry) * 1.1 * MM
            c.rotation_euler = (0, 0, 0)
        else:
            bpy.ops.object.camera_add(location=place(cam['at']))
            c = bpy.context.active_object
            c.data.lens = cam['lens']
            look_at(c, place(cam['look']))
        c.data.clip_start = 0.05
        sc.camera = c
        path = folder / f"R01_{cam['name']}.png"
        sc.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        caption(path, model, cam.get('nota', ''))
        done.append(path)
    return done


def caption(path, model, note=''):
    """Fascia con la dicitura obbligatoria sull'immagine."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return
    im = Image.open(path).convert('RGB')
    d = ImageDraw.Draw(im)
    h = max(28, im.height // 28)
    try:
        font = ImageFont.truetype('DejaVuSans.ttf', int(h * 0.5))
    except OSError:
        font = ImageFont.load_default()
    d.rectangle([0, im.height - h, im.width, im.height], fill=(255, 255, 255))
    text = (f"ANTEPRIMA DAL MODELLO {model['revision']} - {note} - misure in ipotesi, non e' una fonte metrica "
            "- PRELIMINARE - NON PER CANTIERE")
    d.text((12, im.height - h + h * 0.22), text, fill=(180, 0, 0), font=font)
    im.save(path)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    for p in render(fast='--fast' in sys.argv, only=args or None):
        print(p)
