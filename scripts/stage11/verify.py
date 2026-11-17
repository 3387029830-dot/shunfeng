"""Export Stage 1.1 in Inkscape and record deterministic, isolation and vector checks."""
import hashlib
import json
import math
import os
import platform
import re
import shlex
import struct
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import build as art

BASELINE = "3defbec20df88b3d1151dbb793e810010756a2dd"
FROZEN = ("config/stage1", "source/stage1", "scripts/stage1", "reports/stage1", "previews/stage1")
INKSCAPE = os.environ.get("SF_INKSCAPE", "/Applications/Inkscape.app/Contents/MacOS/inkscape")
PREVIEW = art.ROOT / "previews/stage11"
REPORT = art.ROOT / "reports/stage11/VALIDATION.json"
BUILD = ("python3", "scripts/stage11/build.py")
COMMANDS = []


def cmd(args, display=None):
    process = subprocess.run(args, cwd=art.ROOT, capture_output=True, text=True)
    COMMANDS.append({"command": display or shlex.join(str(arg) for arg in args),
                     "exit": process.returncode})
    if process.returncode:
        raise RuntimeError(f"{COMMANDS[-1]}\n{process.stderr}")
    return process.stdout.strip()


def sha(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()


def hashes(directory):
    return {f.name: sha(f) for f in sorted(directory.iterdir()) if f.is_file()}


def state(directory):
    return {f.name: (sha(f), f.stat().st_mtime_ns) for f in directory.iterdir() if f.is_file()}


def node(root, identifier):
    return root.find(f".//*[@id='{identifier}']")


def data(root, identifier):
    found = node(root, identifier)
    assert found is not None, identifier
    return ET.tostring(found)


def open_svg(file):
    return ET.parse(file).getroot()


def inspect_vector(svg):
    ids = [n.get("id") for n in svg.iter() if n.get("id")]
    assert len(ids) == len(set(ids)), "duplicate IDs"
    for n in svg.iter():
        assert n.tag in {art.tag(t) for t in
                         ("svg", "g", "rect", "ellipse", "path", "text", "defs", "clipPath")}, n.tag
        for key, value in n.attrib.items():
            if key in {"fill", "stroke"} and value != "none":
                assert re.fullmatch(r"#[0-9a-f]{6}", value) and value[1:3] == value[3:5] == value[5:7], value
            if value.startswith("url("):
                assert value.startswith("url(#") and value[5:-1] in ids, value
            assert not key.endswith("href"), key


def inspect_geometry(out):
    coords = json.loads((out / "pose_coordinates.json").read_text())
    cfg = json.loads(art.CONFIG.read_text())
    assert coords["viewBox"] == [0, 0, 700, 990] and coords["pelvis"] == [364, 585]
    limits = {"L0": (0, 10), "L1": (10, 15)}
    for trial, legs in coords["legs"].items():
        low, high = limits[trial]
        assert all(low <= leg["knee_deflection_deg"] <= high for leg in legs.values())
    angles = []
    for p, pose in coords["poses"].items():
        points = {k: tuple(v) for k, v in pose["positions"].items()}
        assert points["pelvis"] == (364, 585), p
        angles.append(pose["pelvis_to_crown_deg"])
        for a, b, segment in [
            ("pelvis", "waist", "pelvis_to_waist"),
            ("waist", "shoulder", "waist_to_shoulder"),
            ("shoulder", "neck", "shoulder_to_neck"),
            *[(f"{side}_{a}", f"{side}_{b}", key)
              for side in ("near", "far") for a, b, key in [
                  ("shoulder", "elbow", "upper_arm"), ("elbow", "wrist", "forearm"),
                  ("hip", "knee", "thigh"), ("knee", "ankle", "shin")]],
        ]:
            expected = cfg["segment_lengths"][segment]
            assert math.isclose(math.dist(points[a], points[b]), expected, abs_tol=.002), (p, a, b)
    assert angles == sorted(set(angles))


def inspect_canvases(out):
    canonical = open_svg(out / "P1.svg")
    bounds = {}
    for name in art.POSES:
        for suffix in art.VARIANTS:
            file = out / f"{name}{suffix}.svg"
            root = open_svg(file)
            assert root.get("viewBox") == "0 0 700 990", file.name
            assert not root.findall(".//" + art.tag("text")), file.name
            assert node(root, "figure").get("data-character") == "adult-woman-01", file.name
            for key in ("pelvis", "torso", "neck", "head", "near-leg", "far-leg", "near-arm", "far-arm"):
                assert node(root, key) is not None, (file.name, key)
            pelvis = node(root, "pelvis")
            assert (float(pelvis.get("cx")), float(pelvis.get("cy"))) == (364, 585)
        normal = open_svg(out / f"{name}.svg")
        for key in ("setting", "shirt", "head-profile", "hair-cap", "near-leg", "far-leg"):
            assert data(normal, key) == data(canonical, key), (name, key)
        for key in ("setting", "figure"):
            assert data(normal, key) == data(open_svg(out / f"{name}_C.svg"), key), (name, key)
        silhouette = open_svg(out / f"{name}_silhouette.svg")
        assert all(node(silhouette, key) is None for key in ("setting", "clock", "props", "expression"))
        query = cmd([INKSCAPE, f"source/stage11/generated/{name}.svg", "--query-all"],
                    f"inkscape source/stage11/generated/{name}.svg --query-all")
        bound = next(line for line in query.splitlines() if line.startswith("figure,")).split(",")[1:]
        x, y, w, h = map(float, bound)
        assert 35 < x and x+w < 665 and 155 < y and y+h < 825, (name, bound)
        bounds[name] = [x, y, w, h]
    return bounds


def regressions(original):
    with tempfile.TemporaryDirectory(prefix="stage11-") as folder:
        tmp = Path(folder)
        out = tmp / "generated"
        cmd([*BUILD, "--out", out], "python3 scripts/stage11/build.py --out <scratch>/generated")
        assert hashes(out) == hashes(original), "full rebuild differs"
        initial = state(out)
        cfg = json.loads(art.CONFIG.read_text())
        cfg["poses"]["P2"]["torso"] += 4
        edit = tmp / "p2-config.json"
        edit.write_text(json.dumps(cfg))
        cmd([*BUILD, "--pose", "P2", "--config", edit, "--out", out],
            "python3 scripts/stage11/build.py --pose P2 --config <scratch>/p2-config.json --out <scratch>/generated")
        now = state(out)
        changed = [f"P2{v}.svg" for v in art.VARIANTS]
        assert set(now) == set(initial) and {f for f in now if now[f] != initial[f]} == set(changed)
        assert all(now[f][0] != initial[f][0] for f in changed)
        p2 = open_svg(out / "P2.svg")
        assert data(p2, "setting") == data(open_svg(original / "P2.svg"), "setting")
        p2_original = open_svg(original / "P2.svg")
        assert data(p2, "near-leg") == data(p2_original, "near-leg")
        scene = tmp / "room.svg"
        scene_doc = open_svg(art.ROOM)
        node(scene_doc, "wall").set("fill", "#f0f0f0")
        node(scene_doc, "lumbar-cushion").set("fill", "#bdbdbd")
        ET.ElementTree(scene_doc).write(scene, encoding="utf-8")
        cmd([*BUILD, "--room", scene, "--out", out],
            "python3 scripts/stage11/build.py --room <scratch>/room.svg --out <scratch>/generated")
        for name in art.POSES:
            new, old = (open_svg(p / f"{name}.svg") for p in (out, original))
            assert data(new, "setting") != data(old, "setting")
            assert node(new, "wall").get("fill") == "#f0f0f0"
            assert node(new, "lumbar-cushion").get("fill") == "#bdbdbd"
            assert data(new, "figure") == data(old, "figure")
        return {"p2_torso_delta_deg": 4, "changed": changed, "non_target_mtime_preserved": True,
                "before_sha256": {n: p[0] for n, p in sorted(initial.items())},
                "after_sha256": {n: p[0] for n, p in sorted(now.items())},
                "shared_test": "wall and sofa each updated in all 3; figure groups byte-identical"}


def export(file, target):
    src = file.relative_to(art.ROOT)
    dst = target.relative_to(art.ROOT) if target.is_relative_to(art.ROOT) else f"<scratch>/{target.name}"
    cmd([INKSCAPE, str(src), f"--export-filename={target}"], f"inkscape {src} --export-filename={dst}")
    buf = target.read_bytes()
    assert buf[:8] == b"\x89PNG\r\n\x1a\n" and len(buf) > 100
    return {"input": str(src), "pixels": struct.unpack(">II", buf[16:24]), "sha256": sha(target)}


def main():
    version = cmd([INKSCAPE, "--version"], "inkscape --version")
    cmd(BUILD)
    for file in sorted(art.GENERATED.glob("*.svg")):
        inspect_vector(open_svg(file))
    inspect_geometry(art.GENERATED)
    bounds = inspect_canvases(art.GENERATED)
    isolation = regressions(art.GENERATED)
    frozen = cmd(["git", "diff", "--name-only", BASELINE, "--", *FROZEN])
    assert frozen == "", frozen
    diff_args = ["git", "diff", "--no-index", "--numstat", "--",
                 "source/stage1/generated/P2.svg", "source/stage11/generated/P2.svg"]
    comparison = subprocess.run(diff_args, cwd=art.ROOT, capture_output=True, text=True)
    assert comparison.returncode == 1 and comparison.stdout.strip()
    COMMANDS.append({"command": shlex.join(diff_args), "exit": 1, "meaning": "files differ as expected"})
    PREVIEW.mkdir(parents=True, exist_ok=True)
    exports = {}
    repeats = {}
    with tempfile.TemporaryDirectory(prefix="stage11-png-") as folder:
        for file in sorted(art.GENERATED.glob("*.svg")):
            if file.stem.endswith("_C"):
                continue  # C is exported in the matched comparison board.
            target = PREVIEW / (file.stem + ".png")
            exports[str(target.relative_to(art.ROOT))] = export(file, target)
            redo = export(file, Path(folder) / target.name)
            assert redo == exports[str(target.relative_to(art.ROOT))], target.name
            repeats[target.name] = redo["sha256"]
    report = {
        "technical_status": "PASS",
        "environment": {"inkscape": version, "python": platform.python_version(),
                        "os": platform.system(), "arch": platform.machine()},
        "geometry_and_source_checks": [
            "unique IDs, grayscale colors, local clip references and editable vector elements",
            "constant 700 × 990 viewBox and pelvis (364,585); no text in the single boards",
            "shared character form, wardrobe, legs and room in P1/P2/P3",
            "both L0/L1 angular bands, segment lengths and progressive effective crown angle",
            "no graphics cues, furniture, prop or face details in standalone silhouettes",
            "identical figure and room between single B and C variants",
            "all generated files byte-identical on clean rebuild",
            "P2 update changes only its SVGs; shared scene edit updates all without touching figures",
            "repeat native Inkscape export byte-identical for each delivered PNG",
            "historical Stage 1 directories equal frozen commit",
        ],
        "figure_bounds_svg_units": bounds, "p2_isolation": isolation,
        "historical_baseline_sha": BASELINE, "old_new_p2_svg_numstat": comparison.stdout.strip(),
        "inputs_sha256": {str(p.relative_to(art.ROOT)): sha(p) for p in
                          (art.CONFIG, art.SHAPES, art.ROOM, art.old.CONFIG, art.old.CONTOURS)},
        "generated_sha256": hashes(art.GENERATED), "exports": exports,
        "repeat_png_sha256": repeats, "commands": COMMANDS,
        "external_blind_test": "NOT TESTED", "independent_art_review": "PENDING",
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(f"PASS: {len(report['generated_sha256'])} generated files; {len(exports)} Inkscape PNGs x2")


if __name__ == "__main__":
    main()
