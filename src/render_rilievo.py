"""Quattro viste V5b del rilievo, con la scena, le finiture e le camere del progetto originale."""

import hashlib
import json

from . import render as base
from .rilievo import DEST, measured_model, by_id
from .model import bounds


def publish_view(png, model):
    from PIL import Image, ImageDraw, ImageFont

    with Image.open(png) as source:
        im = source.convert("RGB")
    band = max(28, im.height // 28)
    draw = ImageDraw.Draw(im)
    draw.rectangle((0, im.height - band, im.width, im.height), fill="white")
    font = ImageFont.truetype(str(base.ROOT / "assets/fonts/OpenSans-Regular.ttf"), max(12, band // 2))
    text = f"Limpidia  |  {model['revision']}  |  Rilievo del 26 novembre e arredi di progetto  |  PRELIMINARE - NON PER CANTIERE"
    draw.text((14, im.height - band + 4), text, font=font, fill=(37, 62, 54))
    im.save(png.with_suffix(".jpg"), quality=92, subsampling=0, optimize=True)
    png.unlink()


def render():
    bpy = base._bpy()
    model = measured_model()
    cfg = json.loads(base.RENDER_CFG.read_text(encoding="utf-8"))
    scene, ceiling = base.build_scene(bpy, model, cfg)
    # Nell'anteprima precedente la discesa era mostrata dal fondo. Specchiare i gradini
    # e i loro LED rispetto alla mezzeria del vano porta il primo gradino lato strada.
    stair = by_id(model["room_features"])["SCALE"]
    _, y0, _, y1 = bounds(stair)
    for obj in scene.objects:
        if obj.name.startswith("gradino_"):
            obj.location.y = (y0 + y1) * base.MM - obj.location.y
    # Segnalare il limite vetro fisso / porta anche nella vista dall'alto.
    # Il telaio è illustrativo, la sezione del serramento non è stata rilevata.
    fixed = by_id(model["facade"])["VET_FISSO_ING"]
    depth = cfg["wall_thickness"]
    frame_z = cfg["visual_assumptions"]["glazing_top"]
    for x in (fixed["x1"], by_id(model["facade"])["P_ING"]["x1"]):
        base.box(
            bpy,
            f"montante_ingresso_{x}",
            x - 15,
            -depth / 2 - 15,
            0,
            x + 15,
            -depth / 2 + 15,
            frame_z,
            bpy.data.materials["metallo"],
        )
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = cfg["samples"]
    import _cycles

    scene.cycles.use_denoising = _cycles.with_openimagedenoise
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = cfg["exposure"]
    rx, ry = cfg["resolution"]
    scene.render.resolution_x, scene.render.resolution_y = rx, ry
    scene.render.resolution_percentage = 100
    xs, ys = zip(*model["envelope"]["vertices"])
    w, h = max(xs), max(ys)

    def position(fr):
        return fr[0] * w * base.MM, fr[1] * h * base.MM, fr[2] * base.MM

    folder = DEST / "render"
    folder.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.camera_add()
    camera = bpy.context.active_object
    scene.camera = camera
    camera.data.clip_start = 0.05
    for cam in cfg["cameras"]:
        top = cam.get("type") == "top"
        for obj in scene.objects:
            if obj == ceiling or obj.name.endswith("_architrave") or obj.name.startswith("binario_"):
                obj.hide_render = top
        if top:
            camera.location = (w * 0.0005, h * 0.0005 - 0.15, 12)
            camera.rotation_euler = (0, 0, 0)
            camera.data.type = "ORTHO"
            camera.data.ortho_scale = max(w, h * 1.2 * rx / ry) * 1.1 * base.MM
        else:
            camera.data.type = "PERSP"
            camera.location = position(cam["at"])
            camera.data.lens = cam["lens"]
            base.look_at(camera, position(cam["look"]))
        name = cam["name"] + ".png"
        path = folder / name
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        publish_view(path, model)
    record_meta(folder, model, bpy.app.version_string, scene.cycles.use_denoising)


def record_meta(folder, model, blender_version, denoised):
    cfg = json.loads(base.RENDER_CFG.read_text(encoding="utf-8"))
    inputs = [
        "config/geometry.json",
        "config/rilievo_2026-11-26.json",
        "config/render.json",
        "src/model.py",
        "src/components.py",
        "src/render.py",
        "src/rilievo.py",
        "src/render_rilievo.py",
    ]
    manifest = {
        "revision": model["revision"],
        "blender": blender_version,
        "resolution": cfg["resolution"],
        "samples": cfg["samples"],
        "denoising": bool(denoised),
        "inputs": {name: hashlib.sha256((base.ROOT / name).read_bytes()).hexdigest() for name in inputs},
        "images": {
            cam["name"] + ".jpg": hashlib.sha256((folder / (cam["name"] + ".jpg")).read_bytes()).hexdigest()
            for cam in cfg["cameras"]
        },
    }
    (folder / "render_meta.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    render()
