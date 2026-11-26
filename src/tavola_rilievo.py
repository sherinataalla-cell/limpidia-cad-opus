"""Pianta di lettura degli spazi. La stessa scala grafica vale su X e Y."""

import math

import fitz

from .model import bounds
from .rilievo import by_id


def make_sheet(m, metrics, path):
    doc = fitz.open()
    p = doc.new_page(width=760, height=909)
    green = (0.08, 0.36, 0.31)
    ink = (0.13, 0.19, 0.18)
    grey = (0.34, 0.40, 0.38)
    pale = (0.86, 0.90, 0.87)
    wood = (0.84, 0.75, 0.63)
    paper = (0.97, 0.97, 0.95)
    aqua = (0.23, 0.60, 0.61)
    light = (0.92, 0.95, 0.91)
    for alias, system in [("RilRegular", "helv"), ("RilBold", "hebo")]:
        p.insert_font(fontname=alias, fontbuffer=fitz.Font(system).buffer)

    def text(x, y, value, size=11, color=ink, bold=False):
        p.insert_text((x, y), value, fontsize=size, fontname="RilBold" if bold else "RilRegular", color=color)

    def line(a, b, col=ink, wd=1):
        p.draw_line(a, b, color=col, width=wd)

    def shape(points, fill, stroke=None, width=1):
        q = p.new_shape()
        q.draw_polyline(points + [points[0]])
        q.finish(color=stroke, fill=fill, width=width, closePath=True)
        q.commit()

    def point(x, y):
        return (80 + x * 0.073, 524 - y * 0.073)

    def rect(r, fill, outline=None):
        x0, y0, x1, y1 = r
        a, b = point(x0, y1), point(x1, y0)
        p.draw_rect(fitz.Rect(a, b), color=outline, fill=fill, width=0.7)

    def dim(a, b, value, offset=(0, 0)):
        A, B = point(*a), point(*b)
        line(A, B, green, 0.85)
        for P in (A, B):
            line((P[0] - 2.8, P[1] + 2.8), (P[0] + 2.8, P[1] - 2.8), green, 1)
        x = (A[0] + B[0]) / 2 + offset[0]
        y = (A[1] + B[1]) / 2 + offset[1]
        text(x, y, str(value), 11, green, True)

    def num(x):
        return f"{x:.1f}".replace(".", ",")

    def cm(key):
        return str(round(metrics[key] / 10))

    text(33, 38, "LIMPIDIA   /   VIA ANDREA SOLARI 3", 12, green, True)
    text(568, 38, "26 NOVEMBRE 2026  /  V5b", 11, grey)
    line((33, 49), (727, 49), pale)
    text(33, 83, "Quanto spazio rimane con gli arredi", 27, ink, True)
    text(
        33,
        108,
        f"Zona vendita {num(metrics['shop'])} m²   /   Arredi e rivestimenti {num(metrics['furniture'])} m²   /   Pavimento libero {num(metrics['free'])} m²",
        15,
        green,
        True,
    )
    text(
        33, 130, "Quote in centimetri. Cassetti chiusi, sedie escluse. Ingresso e vetrine in basso.", 12, grey
    )
    shape([point(*v) for v in m["envelope"]["vertices"]], paper, ink, 2)
    from .model import room

    shape([point(*v) for v in room(m, "SALETTA")["outer"]], light)
    # Exterior wall segments; facade drawn piece by piece to show the entrance.
    vv = m["envelope"]["vertices"]
    for a, b in zip(vv[1:], vv[2:] + vv[:1]):
        line(point(*a), point(*b), ink, 2)
    for w in m["walls"]:
        rect(bounds(w), grey)
    F = by_id(m["furniture"])
    stair = by_id(m["room_features"])["SCALE"]
    sx, sy, ex, ey = bounds(stair)
    rect((sx, sy, ex, ey), (0.84, 0.90, 0.9), grey)
    for i in range(1, 11):
        y = sy + (ey - sy) * i / 11
        line(point(sx, y), point(ex, y), (0.65, 0.73, 0.71), 0.45)
    labels = {
        "C1": "C1",
        "C2": "C2",
        "C3": "C3",
        "C4": "C4",
        "ISOLA_SMART": "Isola",
        "CASSA": "Cassa",
        "SCRIVANIA": "Consulenza",
    }
    for key, f in F.items():
        x0, y0, x1, y1 = bounds(f)
        rect((x0, y0, x1, y1), wood, grey)
        label = labels[key]
        xx, yy = point((x0 + x1) / 2, (y0 + y1) / 2)
        text(xx - fitz.get_text_length(label, fontsize=10) / 2, yy + 3, label, 10)
    for seg in m["facade"]:
        if seg["type"] != "door":
            line(point(seg["x0"], 0), point(seg["x1"], 0), ink if seg["type"] == "pier" else aqua, 3)
    for op in m["openings"]:
        hx, hy = op["hinge"]
        dx, dy = op["swing_quadrant"]
        leaf = op["leaf"]
        line(point(hx, hy), point(hx, hy + dy * leaf), grey, 0.8)
        arc = [
            point(hx + dx * leaf * math.cos(i * math.pi / 40), hy + dy * leaf * math.sin(i * math.pi / 40))
            for i in range(21)
        ]
        p.draw_polyline(arc, color=grey, width=0.55)
    text(*point(160, 2670), "Scala", 11, ink, True)
    text(*point(3970, 3600), "Saletta di refrazione", 13, grey)
    text(*point(1410, -250), "Ingresso", 11, grey)
    text(*point(2500, -250), "Vetrina 1", 11, grey)
    text(*point(5080, -250), "Vetrina 2", 11, grey)
    d = bounds(F["SCRIVANIA"])
    c2 = bounds(F["C2"])
    c4 = bounds(F["C4"])
    c1 = bounds(F["C1"])
    dim((4810, d[3]), (4810, c2[1]), cm("client"), (5, 4))
    dim((4810, 0), (4810, d[1]), cm("operator"), (5, 4))
    dim((d[2], 930), (c4[0], 930), cm("lateral"), (-9, -6))
    dim((580, ey), (580, c1[1]), cm("stair_c1"), (4, 4))
    island = bounds(F["ISOLA_SMART"])
    from .components import all_components

    shelves = [c["box"] for c in all_components(m) if c["owner"] == "SMART" and c["kind"] == "shelf"]
    for a, b, z, d, e, _ in shelves:
        rect((a, b, d, e), (0.77, 0.79, 0.70), grey)
    facing = next(s for s in shelves if s[1] < island[3] and s[4] > island[1])
    section = (max(facing[1], island[1]) + min(facing[4], island[3])) / 2
    dim((island[2], section), (facing[0], section), cm("island_smart"), (-9, -6))
    text(33, 583, "Passaggi con cassetti chiusi e aperti", 18, ink, True)
    text(
        33,
        606,
        "Distanze tra gli ingombri del modello. Per la prova di apertura si ipotizzano 35 cm di estrazione.",
        11,
        grey,
    )
    table = [
        ("Scrivania e cassettiere davanti alla saletta (C2/C3)", "client", "client_open"),
        ("Scrivania e cassettiera laterale (C4)", "lateral", "lateral_open"),
        ("Cassettiera sul fondo (C1) e bordo del vano scala", "stair_c1", "stair_c1_open"),
    ]
    for x, t in [(33, "Tratto"), (510, "Cassetti chiusi"), (623, "Un cassetto aperto")]:
        text(x, 634, t, 11, green, True)
    for i, (label, closed, opened) in enumerate(table):
        y = 659 + 24 * i
        line((33, y - 17), (727, y - 17), pale, 0.7)
        text(33, y, label)
        text(510, y, cm(closed) + " cm", 12, ink, True)
        text(623, y, cm(opened) + " cm", 12)
    text(33, 741, "Isola smart e ingresso", 13, ink, True)
    text(
        33,
        762,
        f"Tra isola e muro Smart ci sono {cm('island_wall')} cm. In corrispondenza dei pannelli e delle mensole restano {cm('island_smart')} cm in proiezione.",
        11,
    )
    text(
        33,
        780,
        f"Con la porta di ingresso aperta a 90°, la punta dell'anta dista {cm('entrance_island')} cm dall'isola nella disposizione ipotizzata.",
        11,
    )
    text(33, 813, "Lettura del rilievo", 13, ink, True)
    text(
        33,
        833,
        "Nel render ortogonale la facciata è 749 cm, i laterali 494 e 445 cm. Il raccordo sul fondo è provvisorio:",
        11,
    )
    text(
        33,
        849,
        "il modello chiude con 202 e 49 cm nei due tratti rilevati di 200 e 46 cm. La saletta e gli arredi seguono la V5b.",
        11,
    )
    text(
        33,
        871,
        "La superficie libera comprende i passaggi e gli spazi per sedersi e aprire i mobili. Il corrimano resta da misurare.",
        11,
        grey,
    )
    text(33, 893, "PRELIMINARE  /  NON PER CANTIERE", 9, green, True)
    doc.subset_fonts()
    doc.save(path, garbage=4, deflate=True, no_new_id=True)
    doc.close()
