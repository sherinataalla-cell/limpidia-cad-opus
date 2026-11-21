"""Anteprima 3D fotorealistica dal modello parametrico (Blender/Cycles via `bpy`).

Uso:  python -m src.render            (tutte le inquadrature)
      python -m src.render --fast     (bozza veloce)

Geometria in pianta da config/geometry.json; altezze, finiture e camere da
config/render.json. È un'anteprima volumetrica: NON è una fonte metrica e
non sostituisce la vista approvata in assets/approved/.
"""
import json
import math
import sys
from pathlib import Path

from .model import load, bounds, ROOT, OUT

RENDER_CFG = ROOT / 'config' / 'render.json'
MM = 0.001


def _bpy():
    try:
        import bpy  # noqa: F401
        return bpy
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("Serve il modulo Blender: pip install bpy (Python 3.11-3.13)") from exc


def material(bpy, name, color, roughness=0.5, emission=None, transmission=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = roughness
    if transmission:
        p.inputs['Transmission Weight'].default_value = transmission
        p.inputs['IOR'].default_value = 1.45
    if emission:
        p.inputs['Emission Color'].default_value = (*emission[0], 1)
        p.inputs['Emission Strength'].default_value = emission[1]
    return m


def wood(bpy, name, color, roughness, scale=6.0, along_x=True):
    """Venatura procedurale semplice."""
    m = material(bpy, name, color, roughness)
    nt = m.node_tree
    p = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeNewGeometry')  # posizione in metri, non deformata dalla scala
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (0.6, 6, 0.6) if along_x else (6, 0.6, 0.6)
    wave = nt.nodes.new('ShaderNodeTexWave')
    wave.inputs['Scale'].default_value = scale
    wave.inputs['Distortion'].default_value = 2.5
    wave.inputs['Detail'].default_value = 4
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    c0 = [c * 0.82 for c in color]
    ramp.color_ramp.elements[0].color = (*c0, 1)
    ramp.color_ramp.elements[1].color = (*color, 1)
    nt.links.new(tc.outputs['Position'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], wave.inputs['Vector'])
    nt.links.new(wave.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], p.inputs['Base Color'])
    return m


def brick(bpy, name, color, mortar):
    m = material(bpy, name, color, 0.85)
    nt = m.node_tree
    p = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeNewGeometry')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    mp = nt.nodes.new('ShaderNodeCombineXYZ')  # mattoni sul piano Y-Z: (Y, Z, X)
    nt.links.new(tc.outputs['Position'], sep.inputs['Vector'])
    nt.links.new(sep.outputs['Y'], mp.inputs['X'])
    nt.links.new(sep.outputs['Z'], mp.inputs['Y'])
    nt.links.new(sep.outputs['X'], mp.inputs['Z'])
    b = nt.nodes.new('ShaderNodeTexBrick')
    b.inputs['Color1'].default_value = (*color, 1)
    b.inputs['Color2'].default_value = (*[c * 0.8 for c in color], 1)
    b.inputs['Mortar'].default_value = (*mortar, 1)
    b.inputs['Scale'].default_value = 1.0
    b.inputs['Mortar Size'].default_value = 0.012
    b.inputs['Brick Width'].default_value = 0.25
    b.inputs['Row Height'].default_value = 0.065
    nt.links.new(mp.outputs['Vector'], b.inputs['Vector'])
    nt.links.new(b.outputs['Color'], p.inputs['Base Color'])
    return m


def box(bpy, name, x0, y0, z0, x1, y1, z1, mat):
    """Parallelepipedo da coordinate in mm."""
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.active_object
    o.name = name
    o.scale = ((x1 - x0) * MM, (y1 - y0) * MM, (z1 - z0) * MM)
    o.location = ((x0 + x1) / 2 * MM, (y0 + y1) / 2 * MM, (z0 + z1) / 2 * MM)
    o.data.materials.append(mat)
    return o


def look_at(obj, target):
    from mathutils import Vector
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def build_scene(bpy, model, cfg):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    F = cfg['finishes']
    mats = {
        'walls': material(bpy, 'pareti', F['walls']['color'], F['walls']['roughness']),
        'floor': wood(bpy, 'pavimento', F['floor']['color'], F['floor']['roughness'], 3.0),
        'drawers': wood(bpy, 'noce_scuro', F['drawers']['color'], F['drawers']['roughness']),
        'shelves': material(bpy, 'mensole', F['shelves']['color'], F['shelves']['roughness']),
        'cubes': wood(bpy, 'rovere', F['cubes']['color'], F['cubes']['roughness']),
        'cassa': material(bpy, 'cassa', F['cassa']['color'], F['cassa']['roughness']),
        'desk': wood(bpy, 'scrivania', F['desk']['color'], F['desk']['roughness']),
        'island': material(bpy, 'isola', F['island']['color'], F['island']['roughness']),
        'brick': brick(bpy, 'mattoni', F['brick']['color'], F['brick']['mortar']),
        'ceiling': material(bpy, 'soffitto', F['ceiling']['color'], F['ceiling']['roughness']),
        'glass': material(bpy, 'vetro', (0.95, 0.98, 0.98), 0.0, transmission=1.0),
        'metal': material(bpy, 'metallo', (0.15, 0.15, 0.15), 0.35),
        'void': material(bpy, 'vano_scala', (0.02, 0.02, 0.02), 1.0),
        'led': material(bpy, 'led', (1, 1, 1), 0.5, emission=((1.0, 0.85, 0.65), 8)),
        'panel': material(bpy, 'pannello_smart', (0.05, 0.05, 0.06), 0.2, emission=((0.75, 0.82, 0.95), 1.5)),
    }
    H = cfg['ceiling_height']
    T = cfg['wall_thickness']
    verts = model['envelope']['vertices']
    xs = [v[0] for v in verts]
    ys = [v[1] for v in verts]
    X0, X1, Y0, Y1 = min(xs), max(xs), min(ys), max(ys)

    # Pavimento e soffitto (con vano scala)
    stair = next(z for z in model['room_features'] if z['id'] == 'SCALE')
    sx0, sy0, sx1, sy1 = bounds(stair)
    box(bpy, 'pavimento_a', X0, Y0, -40, X1, sy0, 0, mats['floor'])
    box(bpy, 'pavimento_b', sx1, sy0, -40, X1, sy1, 0, mats['floor'])
    box(bpy, 'pavimento_c', X0, sy1, -40, X1, Y1, 0, mats['floor'])
    box(bpy, 'vano_scala', sx0, sy0, -1200, sx1, sy1, -1100, mats['void'])
    box(bpy, 'soffitto', X0 - T, Y0 - T, H, X1 + T, Y1 + T, H + 50, mats['ceiling'])

    # Pareti perimetrali: ogni lato estruso verso l'esterno; il lato vetrina è vetro
    n = len(verts)
    for i in range(n):
        (ax, ay), (bx, by) = verts[i], verts[(i + 1) % n]
        if ay == by == Y1:  # vetrina
            box(bpy, 'zoccolo_vetrina', min(ax, bx), Y1, 0, max(ax, bx), Y1 + T, 300, mats['walls'])
            box(bpy, 'vetrina', min(ax, bx), Y1 + T / 2 - 10, 300, max(ax, bx), Y1 + T / 2 + 10, 2700, mats['glass'])
            box(bpy, 'architrave', min(ax, bx), Y1, 2700, max(ax, bx), Y1 + T, H, mats['walls'])
            continue
        if ay == by:
            out = -T if ay == Y0 or (ay < (Y0 + Y1) / 2) else T
            box(bpy, f'muro_{i}', min(ax, bx) - T, min(ay, ay + out), 0, max(ax, bx) + T, max(ay, ay + out), H, mats['walls'])
        else:
            out = -T if ax == X0 else T
            box(bpy, f'muro_{i}', min(ax, ax + out), min(ay, by), 0, max(ax, ax + out), max(ay, by), H, mats['walls'])

    # Saletta: pareti in cartongesso dentro la sua zona (porta non modellata: posizione da definire)
    sal = next(z for z in model['room_features'] if z['id'] == 'SALETTA')
    qx0, qy0, qx1, qy1 = bounds(sal)
    st = cfg['saletta_wall_thickness']
    box(bpy, 'saletta_fronte', qx0 - 20, qy1 - st, 0, qx1, qy1, H, mats['walls'])
    west_mat = mats['brick'] if cfg['brick_wall']['side'] == 'west' else mats['walls']
    box(bpy, 'saletta_ovest', qx0, qy0, 0, qx0 + st, qy1, H, mats['walls'])
    box(bpy, 'saletta_ovest_mattoni', qx0 - 20, qy0, 0, qx0, qy1, H, west_mat)

    # Pannelli smart sulla parete in mattoni (quattro telai)
    span = qy1 - qy0
    w = span / 4 - 80
    for k in range(4):
        y = qy0 + 40 + k * (span / 4)
        box(bpy, f'telaio_smart_{k+1}', qx0 - 45, y, 1100, qx0 - 20, y + w, 1100 + w * 1.3, mats['panel'])

    # Ringhiera
    rail = next(z for z in model['room_features'] if z['id'] == 'RINGHIERA')
    rx = rail['start'][0]
    ry0, ry1 = sorted((rail['start'][1], rail['end'][1]))
    rh = cfg['railing_height']
    box(bpy, 'corrimano', rx - 25, ry0, rh - 40, rx + 25, ry1, rh, mats['metal'])
    for k in range(int((ry1 - ry0) / 120) + 1):
        y = ry0 + k * 120
        box(bpy, f'montante_{k}', rx - 8, y - 8, 0, rx + 8, y + 8, rh - 40, mats['metal'])

    # Mobili
    heights = cfg['heights']
    for f in model['furniture']:
        x0, y0, x1, y1 = bounds(f)
        h = heights.get(f['id'], 800)
        fid = f['id']
        if fid == 'CASSA':
            box(bpy, fid, x0, y0, 0, x1, y1, h, mats['cassa'])
        elif fid == 'SCRIVANIA':
            box(bpy, fid + '_piano', x0, y0, h - 40, x1, y1, h, mats['desk'])
            box(bpy, fid + '_fianco_a', x0 + 30, y0 + 30, 0, x1 - 30, y0 + 70, h - 40, mats['desk'])
            box(bpy, fid + '_fianco_b', x0 + 30, y1 - 70, 0, x1 - 30, y1 - 30, h - 40, mats['desk'])
        elif fid == 'ISOLA_SMART':
            box(bpy, fid, x0, y0, 0, x1, y1, h, mats['island'])
        else:
            box(bpy, fid, x0, y0, 80, x1, y1, h, mats['drawers'])
            box(bpy, fid + '_zoccolo', x0 + 20, y0 + 20, 0, x1 - 20, y1 - 20, 80, mats['metal'])
            # due linee LED sul fronte (lato verso il negozio)
            for zz in (h * 0.38, h * 0.70):
                if f['width'] >= f['depth']:
                    yf = y1 if abs(y0 - Y0) < 50 or abs(y0 - qy1) < 50 else y0
                    box(bpy, fid + '_led', x0 + 30, yf - 5, zz, x1 - 30, yf + 5, zz + 12, mats['led'])
                else:
                    box(bpy, fid + '_led', x0 - 5, y0 + 30, zz, x0 + 5, y1 - 30, zz + 12, mats['led'])

    # Mensole sfalsate con cubi rovere sopra le cassettiere
    sh = cfg['shelves']
    for fid in sh['over']:
        f = next(o for o in model['furniture'] if o['id'] == fid)
        x0, y0, x1, y1 = bounds(f)
        for li, z in enumerate(sh['levels']):
            off = 120 if li % 2 else 0
            if f['width'] >= f['depth']:
                wall_y = y0 if abs(y0 - Y0) < 50 or abs(y0 - qy1) < 50 else y1
                d = sh['depth'] if wall_y == y0 else -sh['depth']
                ya, yb = sorted((wall_y, wall_y + d))
                box(bpy, f'{fid}_mensola_{li}', x0 + off, ya, z, x1 - 120 + off, yb, z + sh['thickness'], mats['shelves'])
                box(bpy, f'{fid}_led_mensola_{li}', x0 + off + 20, ya + 20, z - 6, x1 - 140 + off, ya + 40, z, mats['led'])
                cx = x0 + off + (x1 - x0) * (0.25 + 0.4 * (li % 2))
                box(bpy, f'{fid}_cubo_{li}', cx, ya + 30, z + sh['thickness'], cx + 180, ya + 210, z + sh['thickness'] + 180, mats['cubes'])
            else:
                wall_x = x1
                box(bpy, f'{fid}_mensola_{li}', wall_x - sh['depth'], y0 + off, z, wall_x, y1 - 120 + off, z + sh['thickness'], mats['shelves'])
                box(bpy, f'{fid}_led_mensola_{li}', wall_x - 40, y0 + off + 20, z - 6, wall_x - 20, y1 - 140 + off, z, mats['led'])
                cy = y0 + off + (y1 - y0) * (0.25 + 0.4 * (li % 2))
                box(bpy, f'{fid}_cubo_{li}', wall_x - 210, cy, z + sh['thickness'], wall_x - 30, cy + 180, z + sh['thickness'] + 180, mats['cubes'])

    # Contesto esterno minimo: marciapiede e facciata di fronte (solo per la luce in vetrina)
    street = material(bpy, 'strada', (0.35, 0.35, 0.36), 0.8)
    facade = material(bpy, 'facciata', (0.78, 0.74, 0.68), 0.9)
    box(bpy, 'marciapiede', X0 - 8000, Y1 + T, -60, X1 + 8000, Y1 + 14000, -40, street)
    box(bpy, 'facciata_fronte', X0 - 8000, Y1 + 14000, 0, X1 + 8000, Y1 + 14300, 15000, facade)

    # Luci: plafoniere a soffitto (ipotesi visiva) + cielo esterno dalla vetrina
    for i, (lx, ly) in enumerate([(1800, 1500), (1800, 3600), (3600, 3400), (5600, 3400), (2600, 600)]):
        bpy.ops.object.light_add(type='AREA', location=(lx * MM, ly * MM, (H - 20) * MM))
        L = bpy.context.active_object
        L.data.energy = cfg.get('light_power_w', 70)
        L.data.size = 0.6
        L.data.color = (1.0, 0.9, 0.78)
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 5))
    sun = bpy.context.active_object
    sun.data.energy = 1.2
    sun.rotation_euler = (math.radians(55), 0, math.radians(200))
    world = bpy.data.worlds.new('cielo')
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.75, 0.82, 0.92, 1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0
    sc.world = world
    return sc


def render(fast=False):
    bpy = _bpy()
    model = load()
    cfg = json.loads(RENDER_CFG.read_text(encoding='utf-8'))
    sc = build_scene(bpy, model, cfg)
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = 16 if fast else cfg['samples']
    sc.cycles.use_denoising = True
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Medium High Contrast'
    rx, ry = cfg['resolution']
    sc.render.resolution_x = rx // (2 if fast else 1)
    sc.render.resolution_y = ry // (2 if fast else 1)
    sc.render.image_settings.file_format = 'PNG'
    folder = OUT / 'render'
    folder.mkdir(parents=True, exist_ok=True)
    done = []
    for cam in cfg['cameras']:
        bpy.ops.object.camera_add(location=tuple(c * MM for c in cam['location']))
        c = bpy.context.active_object
        c.data.lens = cam['lens']
        c.data.clip_start = 0.05
        look_at(c, tuple(t * MM for t in cam['target']))
        sc.camera = c
        path = folder / f"R01_{cam['name']}.png"
        sc.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        caption(path, model)
        done.append(path)
    return done


def caption(path, model):
    """Fascia con la dicitura obbligatoria sull'immagine."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return
    im = Image.open(path).convert('RGB')
    d = ImageDraw.Draw(im)
    h = max(28, im.height // 28)
    try:
        font = ImageFont.truetype('DejaVuSans.ttf', int(h * 0.55))
    except OSError:
        font = ImageFont.load_default()
    d.rectangle([0, im.height - h, im.width, im.height], fill=(255, 255, 255))
    text = (f"ANTEPRIMA DAL MODELLO {model['revision']} - misure ipotetiche, non e' una fonte metrica "
            "e non sostituisce la vista approvata - PRELIMINARE - NON PER CANTIERE")
    d.text((12, im.height - h + h * 0.2), text, fill=(180, 0, 0), font=font)
    im.save(path)


if __name__ == '__main__':
    for p in render(fast='--fast' in sys.argv):
        print(p)
