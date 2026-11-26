import pytest

from src import model as cad
from src.rilievo import measured_model, space_metrics, by_id


def test_facade_and_entry_use_seven_contiguous_segments():
    m = measured_model()
    spans = [(s["x0"], s["x1"]) for s in m["facade"]]
    assert spans == [
        (0, 850),
        (850, 1180),
        (1180, 2080),
        (2080, 3320),
        (3320, 4220),
        (4220, 6720),
        (6720, 7490),
    ]
    door = by_id(m["openings"])["P_ING"]
    assert (door["hinge"], door["x0"], door["x1"]) == ([1180, 0], 1180, 2080)
    assert door["clear_width"] is None
    survey = m["survey"]
    assert spans[-1][1] - survey["rear_left"] - survey["rear_right"] == 20
    assert survey["left"] - survey["right"] - survey["step"] == 30


def test_stair_furniture_and_available_space():
    m = measured_model()
    features = by_id(m["room_features"])
    assert cad.bounds(features["SCALE"]) == (0, 1500, 850, 3820)
    assert features["RINGHIERA_TESTATA"]["end"] == [850, 3820]
    assert features["SCALE"]["dimensions_status"]["width"] == "assumed"
    metrics = space_metrics(m)
    assert [
        metrics[k]
        for k in ("stair_c1", "stair_c1_open", "operator", "client", "client_open", "lateral", "lateral_open")
    ] == [720, 370, 600, 980, 630, 1540, 1190]
    assert metrics["shop"] == pytest.approx(25.7626)
    assert metrics["shop"] == pytest.approx(metrics["free"] + metrics["furniture"])
    assert round(metrics["free"], 1) == 21.1
    assert metrics["island_smart"] == 1930
    assert metrics["entrance_island"] == 600
    original = cad.load()
    assert cad.bounds(by_id(original["room_features"])["SCALE"]) == (0, 1500, 850, 3900)


def test_four_furnished_views_match_the_geometry_and_files():
    import hashlib
    import json
    from PIL import Image
    from src.rilievo import DEST

    cfg = json.loads((cad.ROOT / "config/render.json").read_text())
    manifest = json.loads((DEST / "render/render_meta.json").read_text())
    assert manifest["revision"] == measured_model()["revision"]
    assert set(manifest["images"]) == {cam["name"] + ".jpg" for cam in cfg["cameras"]}
    for path, digest in manifest["inputs"].items():
        assert hashlib.sha256((cad.ROOT / path).read_bytes()).hexdigest() == digest
    for name, digest in manifest["images"].items():
        image = DEST / "render" / name
        assert hashlib.sha256(image.read_bytes()).hexdigest() == digest
        with Image.open(image) as view:
            assert list(view.size) == cfg["resolution"]
