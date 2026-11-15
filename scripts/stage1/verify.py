"""Export review PNGs and verify the shared rig, isolation, SVGs and rendering."""

import hashlib
import json
import math
import os
import re
import struct
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from build import CONFIG, ROOT, SOURCE, angle, rig, tag


GENERATED = SOURCE / "generated"
PREVIEWS = ROOT / "previews/stage1"
REPORT = ROOT / "reports/stage1/VALIDATION.json"
INKSCAPE = os.environ.get("SF_INKSCAPE", "/Applications/Inkscape.app/Contents/MacOS/inkscape")
POSES = ("P1", "P2", "P3")
BOARDS = ("triptych", "body_study", "clock_comparison", "pelvis_alignment", "arm_assist")
EXPORTS = {name: 700 for pose in POSES for name in (pose, f"{pose}_rig")}
EXPORTS.update(dict.fromkeys(BOARDS, 1320))
EXPORTS["pelvis_alignment"] = 700
BUILD_COMMAND = [sys.executable, "scripts/stage1/build.py"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command):
    return subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True).stdout.strip()


def object_by_id(root, identifier):
    result = root.find(f".//*[@id='{identifier}']")
    assert result is not None, identifier
    return result


def fragment(root, identifier):
    # Strip indentation inherited from the fragment's enclosing document.
    node = object_by_id(root, identifier)
    node.tail = None
    return ET.tostring(node)


def png_size(path):
    with path.open("rb") as file:
        data = file.read(26)
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    return (*struct.unpack(">II", data[16:24]), data[25])


def export_png(source, dest, width):
    command = [
        INKSCAPE,
        str(source.relative_to(ROOT)) if source.is_relative_to(ROOT) else str(source),
        f"--export-width={width}",
        f"--export-filename={dest.relative_to(ROOT) if dest.is_relative_to(ROOT) else dest}",
    ]
    run(command)


def query_bounds(path, identifier):
    result = run([INKSCAPE, str(path.relative_to(ROOT)), "--query-all"])
    record = next(line for line in result.splitlines() if line.split(",")[0] == identifier)
    return [round(float(number), 3) for number in record.split(",")[1:]]


def file_hashes(folder):
    return {p.name: sha(p) for p in sorted(folder.glob("*.svg"))}


def main():
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    config = json.loads(CONFIG.read_text())
    sofa = ET.parse(SOURCE / "shared/sofa.svg").getroot().find(tag("g"))
    # Normalize indentation at the same nesting depth as a generated layer.
    sofa_holder = ET.Element("test")
    ET.SubElement(sofa_holder, "setting").append(sofa)
    ET.indent(sofa_holder, "  ")
    shared_sofa = fragment(sofa_holder, "sofa")
    snapshots, geometry = {}, {}

    for file in sorted(GENERATED.glob("*.svg")):
        root = ET.parse(file).getroot()
        ids = [el.get("id") for el in root.iter() if el.get("id")]
        assert len(ids) == len(set(ids)), file
        assert not list(root.iter(tag("image"))), file
        for el in root.iter():
            for key in ("fill", "stroke"):
                paint = el.get(key, "none")
                assert paint == "none" or re.fullmatch(r"#([a-f0-9]{2})\1\1", paint), (file, paint)

    for name in POSES:
        roots = {v: ET.parse(GENERATED / f"{name}{v}.svg").getroot()
                 for v in ("", "_B", "_C", "_rig", "_body")}
        original = roots[""]
        for variant, doc in roots.items():
            assert doc.get("viewBox") == "0 0 700 990"
            assert not list(doc.iter(tag("text")))
            pelvis = object_by_id(doc, "pelvis")
            assert [float(pelvis.get("cx")), float(pelvis.get("cy"))] == config["pelvis"]
            if variant != "_body":
                assert fragment(doc, "sofa") == shared_sofa
        assert not list(object_by_id(original, "clock"))
        assert object_by_id(roots["_B"], "clock_arc") is not None
        assert len(object_by_id(roots["_C"], "clock_ticks")) == 4
        expected_body = fragment(original, "figure")
        assert all(fragment(roots[v], "figure") == expected_body for v in ("_body", "_B", "_C"))
        assert len(list(object_by_id(original, "figure").iter(tag("path")))) >= 15
        bounds = query_bounds(GENERATED / f"{name}.svg", "figure")
        x, y, w, h = bounds
        assert 36 <= x < x+w <= 664
        assert config["safe_y"][0] <= y < y+h <= config["safe_y"][1]
        p = config["poses"][name]
        joints = rig(config, p)
        assert math.isclose(
            math.dist(joints["near_knee"], joints["near_ankle"]), config["segment_lengths"]["shin"])
        geometry[name] = {"figure_bounds_svg_units": bounds,
                          "leg_axis_deg": round(angle(joints["pelvis"], joints["near_ankle"]), 4)}
        snapshots[name] = fragment(original, "near-leg") + fragment(original, "far-leg")
    assert len(set(snapshots.values())) == 1
    record = {
        "inkscape": run([INKSCAPE, "--version"]),
        "svg_count": len(list(GENERATED.glob("*.svg"))),
        "pose_geometry": geometry,
        "checks": [
            "unique IDs, grayscale and vector-only SVG",
            "matching 700x990 viewBox and nontext individual canvases",
            "identical pelvis, sofa and leg SVGs",
            "body geometry identical across A/B/C",
            "subject bounds within stage safety margins",
        ],
    }

    with tempfile.TemporaryDirectory(prefix="sf-stage1-") as tmp:
        temp = Path(tmp)
        outputs = temp / "generated"
        run(BUILD_COMMAND + ["--out", str(outputs)])
        before = file_hashes(outputs)
        assert before == file_hashes(GENERATED)
        assert (outputs / "pose_coordinates.json").read_bytes() == (
            GENERATED / "pose_coordinates.json").read_bytes()
        config["poses"]["P2"]["torso"] += 6
        changed_config = temp / "changed.json"
        changed_config.write_text(json.dumps(config))
        mtime_before = {p.name: p.stat().st_mtime_ns for p in outputs.iterdir()}
        run(BUILD_COMMAND + ["--out", str(outputs), "--config", str(changed_config), "--pose", "P2"])
        after = file_hashes(outputs)
        changed = sorted(name for name in before if before[name] != after[name])
        assert changed == ["P2.svg", "P2_B.svg", "P2_C.svg", "P2_body.svg", "P2_rig.svg"]
        assert all(p.stat().st_mtime_ns == mtime_before[p.name] for p in outputs.iterdir()
                   if p.name not in changed)
        assert all(fragment(ET.parse(outputs / pose).getroot(), "sofa") == shared_sofa
                   for pose in ("P1.svg", "P2.svg", "P3.svg"))
        record["isolation_test"] = {
            "p2_delta_deg": 6,
            "changed_svg_files": changed,
            "p1_and_p3_before_sha256": {k: v for k, v in before.items() if k.startswith(("P1", "P3"))},
            "p1_and_p3_after_sha256": {k: v for k, v in after.items() if k.startswith(("P1", "P3"))},
            "shared_sofa_sha256": sha(SOURCE / "shared/sofa.svg"),
            "non_target_files_mtime_preserved": True,
        }
        # Perturb only the shared source in a scratch copy and prove propagation.
        altered_sofa = temp / "sofa.svg"
        altered_sofa.write_text((SOURCE / "shared/sofa.svg").read_text().replace("#d8d8d8", "#cecece"))
        alternate = temp / "different-sofa"
        run(BUILD_COMMAND + ["--out", str(alternate), "--sofa", str(altered_sofa)])
        sofa_fragments = [fragment(ET.parse(alternate / f"{pose}.svg").getroot(), "sofa")
                          for pose in POSES]
        assert len(set(sofa_fragments)) == 1 and sofa_fragments[0] != shared_sofa
        assert all(fragment(ET.parse(alternate / f"{pose}.svg").getroot(), "figure") ==
                   fragment(ET.parse(GENERATED / f"{pose}.svg").getroot(), "figure")
                   for pose in POSES)
        record["checks"].extend(["byte-identical full SVG rebuild",
                                 "one shared sofa change propagates to all poses",
                                 "P2-only edit leaves P1/P3/sofa and all other files intact"])
        record["exports"] = {}
        for name, width in EXPORTS.items():
            src, out = GENERATED / f"{name}.svg", PREVIEWS / f"{name}.png"
            export_png(src, out, width)
            w, h, color_type = png_size(out)
            assert w == width and h > 0
            if name in POSES or name.endswith("_rig") or name == "pelvis_alignment":
                assert (w, h) == (700, 990)
            if name == "pelvis_alignment":
                assert color_type in (4, 6)
            record["exports"][str(out.relative_to(ROOT))] = {
                "pixels": [w, h], "sha256": sha(out), "source": str(src.relative_to(ROOT)),
                "command": f"inkscape {src.relative_to(ROOT)} --export-width={width} "
                           f"--export-filename={out.relative_to(ROOT)}",
            }
        for name in POSES + ("clock_comparison",):
            repeat = temp / f"{name}.png"
            export_png(GENERATED / f"{name}.svg", repeat, EXPORTS[name])
            assert sha(repeat) == sha(PREVIEWS / f"{name}.png")
        record["checks"].append("byte-identical repeat PNG renders for P1/P2/P3 and comparison")

    REPORT.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(f"PASS: {len(record['checks'])} structural/render checks, {len(EXPORTS)} PNGs")


if __name__ == "__main__":
    main()
