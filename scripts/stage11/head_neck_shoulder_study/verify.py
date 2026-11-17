"""Verify and export only the Stage 1.1 local character study."""
import hashlib
import json
import os
import re
import struct
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import build

INKSCAPE = os.getenv("SF_INKSCAPE", "/Applications/Inkscape.app/Contents/MacOS/inkscape")
PREVIEWS = build.ROOT / "previews/stage11" / build.STUDY
REPORT = build.ROOT / "reports/stage11" / build.STUDY
SCRIPT = "scripts/stage11/head_neck_shoulder_study/build.py"
COMMANDS = []


def run(*args, documented=None):
    p = subprocess.run(args, cwd=build.ROOT, text=True, capture_output=True)
    COMMANDS.append({"command": documented or " ".join(map(str, args)), "exit": p.returncode})
    p.check_returncode()
    return p.stdout.strip()


def sha(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()


def rel(file):
    return str(file.relative_to(build.ROOT))


def validate_svg(file):
    root = ET.parse(file).getroot()
    ids = [n.get("id") for n in root.iter() if n.get("id")]
    assert len(set(ids)) == len(ids), file
    for node in root.iter():
        assert node.tag.split("}")[-1] in {"svg", "g", "path", "ellipse", "text", "rect", "defs", "clipPath"}
        for key, value in node.attrib.items():
            assert not key.endswith("href")
            if key in ("fill", "stroke") and value != "none":
                assert re.fullmatch(r"#([0-9a-f]{2})\1\1", value), value
            if value.startswith("url("):
                assert value.startswith("url(#") and value[5:-1] in ids, value
    return root


def main():
    setup = json.loads(build.CONFIG.read_text())
    version = run(INKSCAPE, "--version", documented="inkscape --version")
    src = validate_svg(build.INPUT)
    assert {node.get("id") for node in src} == set(setup["landmarks"])
    run("python3", SCRIPT)
    files = sorted(build.OUT.glob("*.svg"))
    original = {rel(f): sha(f) for f in files}
    run("python3", SCRIPT)
    assert original == {rel(f): sha(f) for f in files}
    exports = {}
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="stage11-local-study-") as folder:
        for file in files:
            root = validate_svg(file)
            silhouettes = [n for n in root.iter()
                           if n.get("data-character") and "silhouette" in n.get("id", "")]
            assert len(silhouettes) == (0 if file.stem == "landmarks" else 6)
            for group in silhouettes:
                assert len(group) == 4
                assert all(n.get("fill") == "#000000" and not n.get("stroke") for n in group)
            dst = PREVIEWS / (file.stem + ".png")
            repeat = Path(folder) / dst.name
            for target, shown in [(dst, rel(dst)), (repeat, f"<scratch>/{dst.name}")]:
                run(INKSCAPE, rel(file), f"--export-filename={target}",
                    documented=f"inkscape {rel(file)} --export-filename={shown}")
            pixels = dst.read_bytes()
            assert pixels[:8] == b"\x89PNG\r\n\x1a\n" and sha(dst) == sha(repeat)
            exports[rel(dst)] = {"svg": rel(file), "pixels": struct.unpack(">II", pixels[16:24]),
                                 "sha256": sha(dst), "repeat_sha256_equal": True}
    previous = setup["reviewed_commit"]
    protected = ("source/stage11/generated", "source/stage11/refined", "source/stage11/shared",
                 "config/stage11/geometry.v1.json", "scripts/stage11/build.py",
                 "scripts/stage11/verify.py", "reports/stage11/REVIEW.md",
                 "reports/stage11/VALIDATION.json", "reports/stage11/MANIFEST.md")
    assert not run("git", "diff", "--name-only", previous, "--", *protected)
    old_pngs = run("git", "ls-tree", "-r", "--name-only", previous, "previews/stage11").splitlines()
    assert old_pngs and not run("git", "diff", "--name-only", previous, "--", *old_pngs)
    REPORT.mkdir(parents=True, exist_ok=True)
    record = {
        "reviewed_commit": previous, "inkscape": version, "status": "LOCAL TECHNICAL PASS",
        "candidates": sorted(setup["landmarks"]), "source_sha256": sha(build.INPUT),
        "inputs_sha256": {rel(f): sha(f) for f in (build.CONFIG, build.POSE_COORDINATES)},
        "boards_sha256": original, "exports": exports, "commands": COMMANDS,
        "art_selection": "PENDING", "external_blind_test": "NOT TESTED",
    }
    (REPORT / "VALIDATION.json").write_text(json.dumps(record, indent=2) + "\n")
    print(f"PASS: {len(files)} isolated SVG boards and PNG exports, six candidates. Original triptych untouched.")


if __name__ == "__main__":
    main()
