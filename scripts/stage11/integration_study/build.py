"""Assemble the mixed local selection with an authored torso and gestures."""
import copy
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from stage11 import build as stage11

STUDY = "integration_study"
SRC = ROOT / "source/stage11" / STUDY
OUT = SRC / "generated"
CONFIG = ROOT / "config/stage11" / STUDY / "selection.json"
LOCAL = ROOT / "source/stage11/head_neck_shoulder_study/refined/contours.svg"
ANCHORS = ROOT / "config/stage11/head_neck_shoulder_study/study.json"
BODY = SRC / "refined/upper_body.svg"
P1_SUPPORT = SRC / "refined/p1_support.svg"


def selected_head(parent, source, key, name):
    head = stage11.elem(parent, "g", id="head", data_candidate=key)
    parts = source.find(f"./*[@id='{key}']")
    for node in parts:
        part = node.get("id").removeprefix(key + "-")
        if part == "lip-plane":
            continue
        child = copy.deepcopy(node)
        child.set("id", "neck" if part == "head-neck" else f"head-{part}")
        if name == "P3" and part == "features":
            # Keep the eye and ear lines. Replace the smile and broad grey patch.
            child.set("d", child.get("d").rsplit(" M ", 1)[0])
        head.append(child)
    if name == "P3":
        stage11.path(head, "mouth-opening", "M 141 89 Q 145 89 149 86 Q 149 89 145 90 Q 142 91 141 89 Z",
                     "#6a6a6a")
        stage11.path(head, "mouth-corner", "M 140.6 89 Q 142 89.7 143.5 89.5", stroke="#6a6a6a", width=.85)


def upper_body(parent, source, heads, key, name, origin):
    g = stage11.elem(parent, "g", id="upper-body", transform=f"translate({stage11.xy(origin)})")
    selected_head(g, heads, key, name)
    pose = source.find(f"./*[@id='{name}']")
    # The clothing crosses the lower edge of the broad skin path at the neckline.
    for child in pose:
        part = child.get("data-part")
        item = copy.deepcopy(child)
        item.set("id", part)
        g.append(item)
    return g


def black_figure(group):
    detail = {
        "props", "head-neck-plane", "head-features", "head-pupil", "head-ear", "head-hair-plane",
        "wardrobe", "mouth-opening", "mouth-corner", "P2-far-fingers",
    }
    for node in list(group):
        ident = node.get("id", "")
        if (ident in detail or ident.endswith(("-plane", "-collar", "-light"))
                or node.tag == stage11.tag("path") and node.get("fill") == "none"):
            group.remove(node)
        else:
            black_figure(node)
    if group.get("fill", "none") != "none":
        group.set("fill", "#000000")
    group.attrib.pop("stroke", None)


def pose_drawing(cfg, variant, room, name, origin, inputs, silhouette=False):
    source, heads, key = inputs
    root = stage11.new_canvas()
    if not silhouette:
        stage11.scene(root, room, "S0", True)
        stage11.cues(root, cfg, variant)
    points = stage11.rig(cfg, cfg["poses"][name], cfg["leg_trials"][cfg["selected_leg"]])
    g = stage11.layer(root, "Adult woman / integrated pose", "figure", data_character=cfg["character"])
    stage11.leg_shape(g, points, "far", cfg["leg_trials"][cfg["selected_leg"]], cfg["palette"])
    stage11.ellipse(g, "pelvis", points["pelvis"], 31, 28, cfg["palette"]["pants"])
    stage11.leg_shape(g, points, "near", cfg["leg_trials"][cfg["selected_leg"]], cfg["palette"])
    upper_body(g, source, heads, key, name, origin)
    if silhouette:
        black_figure(g)
    return root


def annotate(drawing, positions, names, offset):
    root = copy.deepcopy(drawing)
    g = stage11.elem(root, "g", id="gesture-marks")
    for i, key in enumerate(names, 1):
        p = tuple(v+a for v, a in zip(positions[key], offset))
        stage11.ellipse(g, f"contact-{i}", p, 2.7, 2.7, "#ffffff", "#545454")
    return root


def main():
    settings = json.loads(CONFIG.read_text())
    cfg = json.loads(stage11.CONFIG.read_text())
    anchors = json.loads(ANCHORS.read_text())["local_shoulder_anchor"]
    room = ET.parse(stage11.ROOM).getroot()
    heads = ET.parse(LOCAL).getroot()
    body = ET.parse(BODY).getroot()
    support_fit = ET.parse(P1_SUPPORT).getroot()
    normal, black, detail, origins = {}, {}, {}, {}
    for name, key in settings["selected"].items():
        points = stage11.rig(cfg, cfg["poses"][name], cfg["leg_trials"][cfg["selected_leg"]])
        origin = tuple(v-a for v, a in zip(points["near_shoulder"], anchors))
        origins[name] = origin
        source = support_fit if name == "P1" else heads
        args = (cfg, settings["clock_variant"], room, name, origin, (body, source, key))
        normal[name] = pose_drawing(*args)
        black[name] = pose_drawing(*args, silhouette=True)
        dx, dy, w, h = settings["head_neck_crop"]
        detail[name] = stage11.sheet(f"{name} / head, neck and shoulder", [[("", normal[name])]],
                                      (origin[0]+dx, origin[1]+dy, w, h), 2)
        for suffix, drawing in [("", normal[name]), ("_silhouette", black[name]), ("_detail", detail[name])]:
            stage11.write(drawing, OUT / f"{name}{suffix}.svg")
    positions = settings["gesture_landmarks"]
    annotated_p1 = annotate(normal["P1"], positions["P1"], ("hair-pad", "upper-back-pad"), (0, 0))
    p1 = stage11.sheet("P1 / hair and upper-back contacts", [[("S0 support / clean", normal["P1"]),
                           ("Two visual contact marks", annotated_p1)]],
                       tuple(settings["p1_support_crop"]), 2.25)
    p23 = []
    for name, keys in [("P2", ("pupil", "screen", "tap", "grip")),
                       ("P3", ("pupil", "mouth", "bite", "grip", "plate"))]:
        x, y = origins[name]
        marked = annotate(normal[name], positions[name], keys, (x, y))
        p23.append([(f"{name} clean", normal[name]), (f"{name} gesture landmarks", marked)])
    x, y = origins["P2"]
    # Crop windows translate with the joint anchors; both rows retain the same zoom.
    # Convert world scenes to the same comparison framing without changing the source canvases.
    diff = (x-origins["P3"][0], y-origins["P3"][1])
    p23[1] = [(label, shifted(drawing, diff)) for label, drawing in p23[1]]
    gestures = stage11.sheet("P2 and P3 / gaze and hand contacts", p23, (x+87, y+47, 155, 135), 2)
    small = stage11.sheet("Integrated triptych / 1:2", [
        [(name, view[name]) for name in normal] for view in (normal, black)
    ], scale=.5)
    for name, drawing in (("p1_support", p1), ("gestures", gestures), ("triptych_half", small)):
        stage11.write(drawing, OUT / f"{name}.svg")


def shifted(source, offset):
    root = stage11.new_canvas()
    stage11.old.stamp(root, source, "shifted", *offset, 1)
    return root


if __name__ == "__main__":
    main()
