"""Verify vector-only face studies, pose guides and deterministic Inkscape exports."""
import hashlib
import json
import os
import re
import shlex
import struct
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import build

ROOT = build.ROOT
PREVIEWS = ROOT / "previews/stage11" / build.STUDY
REPORT = ROOT / "reports/stage11" / build.STUDY / "VALIDATION.json"
SCRIPT = "scripts/stage11/face_study/build.py"
INKSCAPE = os.getenv("SF_INKSCAPE", "/Applications/Inkscape.app/Contents/MacOS/inkscape")
COMMANDS = []


def run(*args, display=None):
    process = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    COMMANDS.append({"command": display or shlex.join(map(str, args)), "exit": process.returncode})
    process.check_returncode()
    return process.stdout.strip()


def rel(file):
    return str(file.relative_to(ROOT))


def sha(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()


def read_svg(file):
    root = ET.parse(file).getroot()
    ids = [node.get("id") for node in root.iter() if node.get("id")]
    assert len(ids) == len(set(ids)), file
    for node in root.iter():
        assert node.tag.split("}")[-1] in {"svg", "path", "g", "rect", "ellipse", "text", "defs", "clipPath"}
        for key, value in node.attrib.items():
            assert not key.endswith("href"), (file, key)
            if key in ("fill", "stroke") and value != "none":
                assert re.fullmatch(r"#([0-9a-f]{2})\1\1", value), (file, value)
            if value.startswith("url("):
                assert value.startswith("url(#") and value[5:-1] in ids, (file, value)
    return root


def inside_quad(point, vertices):
    x, y = point
    sides = []
    for (ax, ay), (bx, by) in zip(vertices, vertices[1:] + vertices[:1]):
        sides.append((bx-ax)*(y-ay) - (by-ay)*(x-ax))
    return all(v > 0 for v in sides) or all(v < 0 for v in sides)


def check_portraits(cfg, directions, expressions):
    assert {node.get("id") for node in directions} == {"A", "B", "C"}
    front_paths = set()
    for candidate in ("A", "B", "C"):
        source = build.get(directions, candidate)
        front_paths.add(build.get(source, f"{candidate}-face").get("d"))
        black = build.direction(directions, candidate, black=True)[0]
        assert len(black) == 4 and all(n.get("fill") == "#000000" and not n.get("stroke") for n in black)
    assert len(front_paths) == 3
    assert cfg["principal_candidate"] == "A"
    distinct_components = {name: set() for name in ("brow", "eye", "lid")}
    common = ("A-fringe", "A-ear", "A-neck", "A-ponytail")
    base = build.get(directions, "A")
    for pose in build.POSES:
        rendered = build.acting_profile(directions, expressions, cfg, pose)[0]
        for ident in common:
            assert build.get(rendered, ident).attrib == build.get(base, ident).attrib
        for ident, values in distinct_components.items():
            values.add(build.get(build.get(rendered, pose), f"{pose}-{ident}").get("d"))
        face = build.get(rendered, "A-face").get("d")
        original = build.get(base, "A-face").get("d")
        assert face.split("C 181 143", 1)[0] == original.split("C 181 143", 1)[0]
        assert (face == original) == (pose != "P3")
    assert all(len(values) == 3 for values in distinct_components.values())
    measures = build.geometry(cfg, expressions)
    points = build.get(build.get(expressions, "phone"), "phone-plane").get("d").split()
    polygon = [tuple(map(float, points[i+1:i+3])) for i in (0, 3, 6, 9)]
    assert inside_quad(measures["P2"]["gaze_at_screen_x"], polygon)
    assert 0 < measures["P3"]["approach_distance"] < 20
    return measures


def main():
    cfg = json.loads(build.CONFIG.read_text())
    ink = run(INKSCAPE, "--version", display="inkscape --version")
    geometry = check_portraits(cfg, read_svg(build.DIRECTIONS), read_svg(build.ACTING))
    run("python3", SCRIPT)
    files = sorted(build.OUTPUT.glob("*.svg"))
    assert {f.stem for f in files} == {"face_directions", "expressions", "gaze_bite"}
    source_hashes = {rel(f): sha(f) for f in files}
    run("python3", SCRIPT)
    assert source_hashes == {rel(f): sha(f) for f in files}
    legacy = run("git", "diff", "--name-only", cfg["baseline"], "--", ".", ":(exclude,glob)**/face_study/**")
    assert legacy == "", legacy
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    outputs = {}
    with tempfile.TemporaryDirectory(prefix="stage11-faces-") as folder:
        for file in files:
            read_svg(file)
            png = PREVIEWS / (file.stem + ".png")
            repeat = Path(folder) / png.name
            for target, shown in [(png, rel(png)), (repeat, f"<scratch>/{png.name}")]:
                run(INKSCAPE, rel(file), f"--export-filename={target}",
                    display=f"inkscape {rel(file)} --export-filename={shown}")
            raw = png.read_bytes()
            assert raw.startswith(b"\x89PNG\r\n\x1a\n") and sha(png) == sha(repeat)
            outputs[rel(png)] = {"pixels": struct.unpack(">II", raw[16:24]), "sha256": sha(png),
                                 "repeat_sha256_equal": True}
    record = {
        "baseline": cfg["baseline"], "technical_status": "PASS", "inkscape": ink,
        "direction_candidates": ["A", "B", "C"], "acting_prototype": cfg["principal_candidate"],
        "local_geometry": geometry, "inputs_sha256": {rel(f): sha(f) for f in
                                                      (build.DIRECTIONS, build.ACTING, build.CONFIG)},
        "svg_sha256": source_hashes, "exports": outputs, "commands": COMMANDS,
        "art_status": "PENDING", "triptych_integration": "NOT EXECUTED",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(record, indent=2) + "\n")
    print("PASS: three SVG boards and three repeatable PNGs; gaze enters the screen; frozen evidence unchanged")


if __name__ == "__main__":
    main()
