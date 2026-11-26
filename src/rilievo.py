"""V5b sul rilievo del 26 novembre. Un solo modello alimenta tavola, render e calcolo degli spazi."""

import json

from shapely.geometry import box
from shapely.ops import unary_union

from . import model as cad
from .components import all_components, union_bounds

SURVEY = cad.ROOT / "config" / "rilievo_2026-11-26.json"
DEST = cad.OUT / "rilievo_V5b"


def by_id(items):
    return {item["id"]: item for item in items}


def measured_model():
    base = cad.load()
    m = cad.apply_overrides(base, by_id(base["layout_proposals"])["V5b"])
    s = json.loads(SURVEY.read_text(encoding="utf-8"))
    m["survey"] = s
    m["revision"], m["revision_date"] = s["revision"], s["date"]
    m["layout_proposals"] = []
    m["sources"]["RIL"] = s["source"]
    m["facade"] = []
    x = 0
    for name, kind, length in s["facade"]:
        m["facade"].append(dict(id=name, type=kind, x0=x, x1=x + length, status="verified", source="RIL"))
        x += length
    w, h, r, t = x, s["left"], s["right"], s["rear_left"]
    m["envelope"].update(
        vertices=[[0, 0], [w, 0], [w, r], [t, r], [t, h], [0, h]],
        status="assumed",
        source="RIL. Chiusura ortogonale provvisoria su facciata, sinistra, destra e fondo sinistro; fondo destro e salto sono derivati.",
    )
    m["coordinate_system_note"] = "Strada in basso. Origine al filo interno della facciata, angolo sinistro."
    entrance = by_id(m["facade"])["P_ING"]
    door = by_id(m["openings"])["P_ING"]
    door.update(
        x0=entrance["x0"],
        x1=entrance["x1"],
        hinge=[entrance["x0"], 0],
        opening_width=entrance["x1"] - entrance["x0"],
        leaf=entrance["x1"] - entrance["x0"],
        source="RIL: modulo porta 900 mm. Anta, cerniera, verso e luce netta conservano le ipotesi V5b.",
    )
    walls = by_id(m["walls"])
    smart = walls["W_SAL_O"]
    smart.update(depth=h - smart["y"], source="Posizione V5b; raccordo al fondo aggiornato al rilievo.")
    jamb = walls["W_SAL_S2"]
    jamb.update(
        width=w - jamb["x"],
        source="Porta della saletta in posizione V5b; spalla ricavata fino alla parete destra.",
    )
    m["rooms"][0]["source"] = "Netto calcolato dai tramezzi di progetto V5b e dal contorno RIL provvisorio."
    f = by_id(m["furniture"])
    for fid in ("CASSA", "C1"):
        f[fid]["y"] = h - f[fid]["depth"]
    f["C4"]["x"] = w - f["C4"]["width"]
    feats = by_id(m["room_features"])
    stair = feats["SCALE"]
    stair.update(
        y=s["stair_from_facade"],
        depth=s["stair_length"],
        source="RIL: distanza dalla facciata e lunghezza; larghezza da S1, da rilevare.",
        dimensions_status={"y": "verified", "depth": "verified", "width": "assumed"},
    )
    sx, sy, ex, ey = cad.bounds(stair)
    feats["RINGHIERA"].update(start=[ex, sy], end=[ex, ey])
    feats["RINGHIERA_TESTATA"].update(start=[sx, ey], end=[ex, ey])
    cols = by_id(m["display_proposal"]["slat_columns"])
    cols["LS2"]["x"] = w - cols["LS2"]["width"]
    cols["LS3"]["y"] = h - cols["LS3"]["depth"]
    points = by_id(m["electrical_points"])
    for key in ("E01", "E02"):
        points[key]["y"] = h
    points["E03C"]["x"] = w
    points["E04"]["y"] = smart["y"] + smart["depth"] // 2
    points["E06"]["support"] = "Sotto il piano o dalla parete C4; punto e percorso da verificare."
    return m


def space_metrics(m):
    f = by_id(m["furniture"])
    rects = {k: box(*cad.bounds(v)) for k, v in f.items()}
    shop = cad.shop_poly(m)
    pieces = all_components(m)
    # Full plan footprint of each closed mobile, including a table's top and the
    # entire width of each slat panel. Wall cladding at floor level also takes space.
    fixtures = [box(*cad.bounds(col)) for col in m["display_proposal"]["slat_columns"]]
    for c in pieces:
        a, b, z, d, e, _ = c["box"]
        if c["kind"] == "cladding" and z == 0:
            fixtures.append(box(a, b, d, e))
    furniture = unary_union([*rects.values(), *fixtures]).intersection(shop)
    desk, c1, c4 = (rects[k] for k in ("SCRIVANIA", "C1", "C4"))
    cabinets = rects["C2"].union(rects["C3"])
    stair = cad.stair_poly(m)
    drawer = m["use_assumptions"]["drawer_extension"]["value"]
    table = {k: v for k, v in cad.areas(m).items()}
    cassa_bounds = union_bounds([c for c in pieces if c["owner"] == "CASSA"])
    cassa = box(cassa_bounds[0], cassa_bounds[1], cassa_bounds[3], cassa_bounds[4])
    island = rects["ISOLA_SMART"]
    smart = by_id(m["walls"])["W_SAL_O"]
    # Consider all Smart display pieces that overlap the island longitudinally and at its accessible front.
    smart_parts = [
        box(a, b, d, e)
        for c in pieces
        if c["owner"] == "SMART"
        for a, b, z, d, e, Z in [c["box"]]
        if b < island.bounds[3] and e > island.bounds[1]
    ]
    entrance = by_id(m["openings"])["P_ING"]
    return dict(
        shop=shop.area / 1e6,
        furniture=furniture.area / 1e6,
        free=shop.difference(furniture).area / 1e6,
        room=table["saletta netta (facce interne dei tramezzi)"],
        stair=stair.area / 1e6,
        operator=desk.bounds[1],
        client=desk.distance(cabinets),
        client_open=desk.distance(cabinets) - drawer,
        lateral=desk.distance(c4),
        lateral_open=desk.distance(c4) - drawer,
        stair_c1=c1.distance(stair),
        stair_c1_open=c1.distance(stair) - drawer,
        stair_cassa=stair.distance(cassa),
        island_wall=smart["x"] - island.bounds[2],
        island_smart=min(
            (p.bounds[0] - island.bounds[2] for p in smart_parts), default=smart["x"] - island.bounds[2]
        ),
        entrance_island=island.bounds[1] - (entrance["hinge"][1] + entrance["leaf"]),
    )


def generate():
    from . import generate as gen
    from .checks import write_report
    from .tavola_rilievo import make_sheet

    m = measured_model()
    DEST.mkdir(parents=True, exist_ok=True)
    sheet = gen.build_a01(
        m,
        "A01-RIL",
        ["Pianta arredi V5b", "Rilievo 26 novembre", "Piano terra"],
        [
            "Chiusura ortogonale provvisoria.",
            "Fondo dx: 2020 disegno / 2000 rilievo.",
            "Salto: 490 disegno / 460 rilievo.",
        ],
    )
    sheet.saveas(DEST / "A01_arredi.dxf")
    gen.export_pdf(sheet, "A01-RIL", DEST / "A01_arredi.pdf")
    write_report(m, DEST / "criticita.md")
    make_sheet(m, space_metrics(m), DEST / "spazi_liberi.pdf")
    return DEST


if __name__ == "__main__":
    print(generate())
