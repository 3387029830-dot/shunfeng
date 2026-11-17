"""Export the integration study and check isolation from previously reviewed work."""
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
SCRIPT = "scripts/stage11/integration_study/build.py"
PREVIEWS = ROOT / "previews/stage11" / build.STUDY
REPORT = ROOT / "reports/stage11" / build.STUDY
INK = os.getenv("SF_INKSCAPE", "/Applications/Inkscape.app/Contents/MacOS/inkscape")
COMMANDS = []
NAMES = ("P1", "P2", "P3")


def run(*args, display=None):
    process = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    COMMANDS.append({"command": display or shlex.join(map(str, args)), "exit": process.returncode})
    process.check_returncode()
    return process.stdout.strip()


def sha(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()


def rel(file):
    return str(file.relative_to(ROOT))


def by_id(root, ident):
    return root.find(f".//*[@id='{ident}']")


def read_vector(filename):
    root = ET.parse(filename).getroot()
    ids = [node.get("id") for node in root.iter() if node.get("id")]
    assert len(set(ids)) == len(ids), filename
    for node in root.iter():
        assert node.tag.split("}")[-1] in {"svg", "g", "path", "rect", "ellipse", "text", "defs", "clipPath"}
        for key, value in node.attrib.items():
            assert not key.endswith("href"), (filename, key)
            if key in ("fill", "stroke") and value != "none":
                assert re.fullmatch(r"#([0-9a-f]{2})\1\1", value), (filename, value)
            if value.startswith("url("):
                assert value.startswith("url(#") and value[5:-1] in ids, (filename, value)
    return root


def verify_structure(inputs):
    common = ("setting", "near-leg", "far-leg", "clock", "pelvis")
    for name in NAMES:
        svg = read_vector(build.OUT / (name + ".svg"))
        prior = read_vector(ROOT / f"source/stage11/generated/{name}.svg")
        assert svg.get("viewBox") == "0 0 700 990"
        assert by_id(svg, "head").get("data-candidate") == inputs["selected"][name]
        assert all(by_id(svg, ident) is not None for ident in ("head", "neck", "torso", "near-arm", "upper-body"))
        for ident in common:
            before, after = (by_id(root, ident) for root in (prior, svg))
            before.tail = after.tail = None
            assert ET.tostring(before) == ET.tostring(after), (name, ident)
        pelvis = by_id(svg, "pelvis")
        assert (pelvis.get("cx"), pelvis.get("cy")) == ("364.000", "585.000")
        black = read_vector(build.OUT / f"{name}_silhouette.svg")
        assert black.get("viewBox") == svg.get("viewBox")
        assert all(by_id(black, name) is None for name in ("setting", "clock", "props", "head-features"))
        assert all(node.get("fill", "#000000") == "#000000" and "stroke" not in node.attrib
                   for node in by_id(black, "figure").iter())
        if name == "P3":
            assert by_id(svg, "mouth-opening") is not None and by_id(svg, "head-lip-plane") is None


def main():
    data = json.loads(build.CONFIG.read_text())
    version = run(INK, "--version", display="inkscape --version")
    for file in (build.BODY, build.LOCAL, build.P1_SUPPORT):
        read_vector(file)
    run("python3", SCRIPT)
    files = sorted(build.OUT.glob("*.svg"))
    assert len(files) == 12
    first = {rel(f): sha(f) for f in files}
    run("python3", SCRIPT)
    assert first == {rel(f): sha(f) for f in files}
    verify_structure(data)
    baseline = data["reviewed_local_study"]
    original_changes = run("git", "diff", "--name-only", baseline, "--", ".",
                           ":(exclude,glob)**/integration_study/**")
    assert original_changes == "", original_changes
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    exports = {}
    with tempfile.TemporaryDirectory(prefix="stage11-integrated-") as folder:
        for source in files:
            read_vector(source)
            png = PREVIEWS / (source.stem + ".png")
            repeat = Path(folder) / png.name
            for target, label in [(png, rel(png)), (repeat, f"<scratch>/{png.name}")]:
                run(INK, rel(source), f"--export-filename={target}",
                    display=f"inkscape {rel(source)} --export-filename={label}")
            pixels = png.read_bytes()
            assert pixels.startswith(b"\x89PNG\r\n\x1a\n") and sha(png) == sha(repeat)
            size = struct.unpack(">II", pixels[16:24])
            if source.stem in NAMES or source.stem.endswith("_silhouette"):
                assert size == (700, 990)
            exports[rel(png)] = {"pixels": size, "sha256": sha(png), "repeat_sha256_equal": True}
    record = {
        "stage": "Stage 1.1 integration study", "inkscape": version, "technical_status": "PASS",
        "reviewed_local_study": baseline, "reviewed_original_triptych": data["reviewed_original_triptych"],
        "selected": data["selected"],
        "inputs_sha256": {rel(f): sha(f) for f in
                          (build.CONFIG, build.LOCAL, build.ANCHORS, build.BODY, build.P1_SUPPORT,
                           build.stage11.ROOM, build.stage11.CONFIG)},
        "svg_sha256": first, "exports": exports, "commands": COMMANDS,
        "visual_review": "PENDING; production-side observations in REVIEW.md",
        "blind_test": "NOT TESTED",
    }
    REPORT.mkdir(parents=True, exist_ok=True)
    (REPORT / "VALIDATION.json").write_text(json.dumps(record, indent=2) + "\n")
    print("PASS: 12 SVGs, 12 byte-identical repeated PNG exports, S0/legs/pelvis and frozen files unchanged")


if __name__ == "__main__":
    main()
