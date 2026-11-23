"""Anteprima 3D dal modello parametrico (Blender/Cycles via `bpy`).

Uso:  python -m src.render            (tutte le inquadrature)
      python -m src.render --fast     (bozza veloce)

Tutta la geometria viene da config/geometry.json, la stessa fonte delle tavole:
involucro, facciata, tramezzi e porte dal modello; mobili, mensole, cubotti, LED,
colonne listelli e parete smart dagli stessi componenti 3D di src/components.py
usati da prospetti, abaco e controlli. render_meta.json registra la revisione
del modello di ogni immagine. config/render.json
contiene solo parametri visivi (colori, luci, camere) e ipotesi grafiche che le
tavole non usano. È un'anteprima: NON è una fonte metrica.
"""
import json
import math
import sys

from .model import (apply_overrides, guards, load, bounds, rect_cells, floor_poly, envelope_edges, outward, faces, model_fingerprint, ROOT, OUT)
from .components import all_components

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

    # Ringhiera lungo la linea del modello (spessore non rilevato: ipotesi visiva)
    # Tutte le protezioni della scala lungo le linee del modello (spessore non rilevato: ipotesi visiva)
    rh = V['railing_height']
    for g in guards(model):
        (ax, ay), (bx, by) = g['start'], g['end']
        L = math.hypot(bx - ax, by - ay)
        ux, uy = (bx - ax) / L, (by - ay) / L
        x0_, x1_ = sorted((ax, bx))
        y0_, y1_ = sorted((ay, by))
        hx, hy = (20 if ux == 0 else 0), (20 if uy == 0 else 0)
        box(bpy, f"{g['id']}_corrimano", x0_ - hx, y0_ - hy, rh - 40, x1_ + hx, y1_ + hy, rh, M['steel'])
        for k in range(int(L / 600) + 1):
            t = min(k * 600, L - 20)
            px, py = ax + ux * t, ay + uy * t
            box(bpy, f"{g['id']}_montante_{k}", px - (15 if ux == 0 else 0), py - (15 if uy == 0 else 0), -400,
                px + (15 if ux == 0 else 20 * abs(ux)), py + (15 if uy == 0 else 20 * abs(uy)), rh - 40, M['steel'])

    # Mobili, proposta espositiva e parete smart: gli STESSI componenti di tavole, abaco e controlli
    # (src/components.py). Nessuna quota propria del render.
    fs = faces(model)
    NORM = {(0, -1): '-y', (0, 1): '+y', (-1, 0): '-x', (1, 0): '+x'}
    for c in all_components(model):
        x0, y0, z0, x1, y1, z1 = c['box']
        hf = fs.get(c['host']) if c.get('host') else None
        nrm = NORM.get(tuple(hf['n'])) if hf else None
        if c['kind'] == 'logo' and nrm:
            # marchio ufficiale applicato sul fronte (riquadro del componente)
            w = (x1 - x0) if nrm in ('-y', '+y') else (y1 - y0)
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            ox, oy = {'-y': (0, -1), '+y': (0, 1), '-x': (-1, 0), '+x': (1, 0)}[nrm]
            px = (x0 if ox < 0 else x1) if ox else cx
            py = (y0 if oy < 0 else y1) if oy else cy
            plane(bpy, c['id'], (px + ox, py + oy, (z0 + z1) / 2), (w, z1 - z0), nrm, M['logo'])
            continue
        box(bpy, c['id'], x0, y0, z0, x1, y1, z1, M[c['mat']])
        txt = c.get('title') if c['kind'] == 'frame' else c.get('text') if c['kind'] == 'label' else None
        if txt and nrm:
            ox, oy = {'-y': (0, -1), '+y': (0, 1), '-x': (-1, 0), '+x': (1, 0)}[nrm]
            px = ((x0 if ox < 0 else x1) + 2 * ox) if ox else (x0 + x1) / 2
            py = ((y0 if oy < 0 else y1) + 2 * oy) if oy else (y0 + y1) / 2
            if c['kind'] == 'frame':   # titolo sull'immagine, davanti al pannello
                label(bpy, txt, (px, py, z1 - 70), nrm, 45, M['ink'])
            else:                      # testo del cartellino
                label(bpy, txt, (px, py, (z0 + z1) / 2), nrm, 20, M['ink_dark'])

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


def render(fast=False, only=None, variant=None):
    """Render della base o di una variante (stessa geometria della tavola A01-<variante>)."""
    bpy = _bpy()
    model = load()
    if variant:
        model = apply_overrides(model, next(v for v in model['layout_proposals'] if v['id'] == variant))
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
    folder = OUT / 'render' / variant if variant else OUT / 'render'
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
        # vista dall'alto = sezione orizzontale: via soffitto, architravi e binari luce
        for o in sc.objects:
            if o is ceil or o.name.endswith('_architrave') or o.name.startswith('binario_'):
                o.hide_render = top
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
        meta_path = folder / 'render_meta.json'
        try:
            meta = json.loads(meta_path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            meta = {}
        meta[path.name] = {'revision': model['revision'], 'fingerprint': model_fingerprint()}
        meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
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
    var = next((a.split('=', 1)[1] for a in sys.argv[1:] if a.startswith('--variante=')), None)
    for p in render(fast='--fast' in sys.argv, only=args or None, variant=var):
        print(p)
