"""Assemble the isolated portrait direction and acting boards in editable SVG."""
import copy
import json
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from stage1.build import canvas, elem, ellipse, label, path, stamp, write

STUDY = "face_study"
SOURCE = ROOT / "source/stage11" / STUDY
DIRECTIONS = SOURCE / "refined/directions.svg"
ACTING = SOURCE / "refined/acting.svg"
OUTPUT = SOURCE / "generated"
CONFIG = ROOT / "config/stage11" / STUDY / "study.json"
POSES = ("P1", "P2", "P3")
# Preserve the original brow, nose and cheek outline and articulate only the lower jaw.
A_P3_LOWER_FACE = (
    "C 181 143 183 145 184 146 C 185 147 185 149 183 150 "
    "C 180 151 178 153 175 155 C 176 158 181 158 182 160 "
    "C 186 167 181 177 172 181 C 162 185 150 181 142 174 "
    "C 130 168 125 159 116 153 C 101 145 92 132 88 114 Z"
)


def get(root, ident):
    return root.find(f"./*[@id='{ident}']")


def direction(source, key, black=False):
    root = canvas(260, 245)
    figure = copy.deepcopy(get(source, key))
    root.append(figure)
    if black:
        for element in list(figure):
            if element.get("data-outline") == "true":
                element.set("fill", "#000000")
            else:
                figure.remove(element)
    return root


def rotation(point, pivot, degrees):
    x, y = (v-a for v, a in zip(point, pivot))
    t = math.radians(degrees)
    return (pivot[0] + x*math.cos(t) - y*math.sin(t),
            pivot[1] + x*math.sin(t) + y*math.cos(t))


def acting_profile(source, expressions, cfg, pose, guides=False):
    root = direction(source, cfg["principal_candidate"])
    head = root[0]
    pivot = tuple(cfg["head_pivot"])
    angle = cfg["pose_rotation_degrees"][pose]
    head.set("transform", f"rotate({angle} {pivot[0]} {pivot[1]})")
    head.remove(get(head, "A-neutral"))
    head.append(copy.deepcopy(get(expressions, pose)))
    if pose == "P3":
        face = get(head, "A-face")
        face.set("d", face.get("d").split("C 181 143", 1)[0] + A_P3_LOWER_FACE)
    if pose in ("P2", "P3"):
        root.append(copy.deepcopy(get(expressions, "phone" if pose == "P2" else "fork")))
    if guides:
        points = geometry(cfg, expressions)
        if pose == "P2":
            start, target = points["P2"]["eye"], points["P2"]["screen"]
            end = points["P2"]["gaze_at_screen_x"]
            guide = path(root, "gaze-ray", f"M {start[0]} {start[1]} L {end[0]} {end[1]}",
                         stroke="#484848", width=.8)
            guide.set("stroke-dasharray", "3 2")
        else:
            start, target = points["P3"]["mouth"], points["P3"]["bite"]
            guide = path(root, "approach", f"M {start[0]} {start[1]} L {target[0]} {target[1]}",
                         stroke="#444444", width=.8)
            guide.set("stroke-dasharray", "2 1.5")
        ellipse(root, "action-start", start, 1.9, 1.9, "#f5f5f5", "#414141")
        ellipse(root, "action-target", target, 1.9, 1.9, "#f5f5f5", "#414141")
    return root


def geometry(cfg, expressions):
    pivot = cfg["head_pivot"]
    angles = cfg["pose_rotation_degrees"]
    eye = rotation(cfg["p2_eye_center"], pivot, angles["P2"])
    pupil_center = get(get(expressions, "P2"), "P2-pupil").get("data-center").split()
    pupil = rotation(tuple(map(float, pupil_center)), pivot, angles["P2"])
    screen = cfg["p2_target_screen"]
    slope = (pupil[1]-eye[1]) / (pupil[0]-eye[0])
    intercept = eye[1] + slope*(screen[0]-eye[0])
    lip = rotation(cfg["p3_lip_opening"], pivot, angles["P3"])
    bite = cfg["p3_target_bite"]
    return {
        "P2": {"eye": eye, "pupil": pupil, "screen": screen, "gaze_at_screen_x": [screen[0], intercept],
               "gaze_distance_from_screen_center": abs(intercept-screen[1])},
        "P3": {"mouth": lip, "bite": bite, "approach_distance": math.dist(lip, bite)},
    }


def board(width, height, title, subtitle):
    root = canvas(width, height)
    elem(root, "rect", id="paper", width=width, height=height, fill="#dddddd")
    label(root, title, 32, 41, 27, "#303030", "bold")
    label(root, subtitle, 32, 66, 15, "#575757")
    return root, elem(root, "defs")


def card(root, defs, portrait, key, pos, crop, scale):
    x, y = pos
    left, top, width, height = crop
    aperture = {"x": x, "y": y, "width": width*scale, "height": height*scale}
    elem(root, "rect", **aperture, fill="#f3f3f3")
    clip = elem(defs, "clipPath", id=f"{key}-clip")
    elem(clip, "rect", **aperture)
    mask = elem(root, "g", clip_path=f"url(#{key}-clip)")
    stamp(mask, portrait, key, x-left*scale, y-top*scale, scale)


def direction_board(source, cfg):
    root, defs = board(965, 645, "Face directions", "Three right profiles / fixed viewport and scale")
    crop = cfg["profile_window"]
    for i, (key, caption) in enumerate([("A", "Soft editorial"), ("B", "Rounded modern"), ("C", "Quiet sculptural")]):
        x = 32 + i*310
        face = direction(source, key)
        label(root, f"{key}  {caption}", x, 111, 17, "#353535", "bold")
        card(root, defs, face, f"portrait-{key}", (x, 126), crop, 1.7)
        label(root, "Pure silhouette", x, 518, 13)
        card(root, defs, direction(source, key, black=True), f"black-{key}", (x, 531), crop, .43)
        label(root, "Triptych 1:2", x+118, 518, 13)
        card(root, defs, face, f"small-{key}", (x+118, 531), crop, cfg["actual_half_scale"])
    return root


def acting_board(source, expressions, cfg):
    root, defs = board(1198, 637, "A / three expressions",
                       "Shared skull, ear and hair geometry / local performance tests")
    crop = cfg["acting_window"]
    for i, (pose, caption) in enumerate(zip(POSES, ("Relax", "Focus on screen", "Anticipate the bite"))):
        x = 32+i*387
        portrait = acting_profile(source, expressions, cfg, pose)
        label(root, f"{pose}  {caption}", x, 111, 17, "#353535", "bold")
        card(root, defs, portrait, f"{pose}-profile", (x, 126), crop, 1.53)
        label(root, "Triptych 1:2", x, 540, 13)
        card(root, defs, portrait, f"{pose}-small", (x, 551), crop, cfg["actual_half_scale"])
    return root


def guide_board(source, expressions, cfg):
    root, defs = board(829, 554, "Gaze and bite checks", "Screen intersection / space from open lips to fork tip")
    for i, pose in enumerate(("P2", "P3")):
        x = 32+i*401
        label(root, pose, x, 108, 16, "#353535", "bold")
        drawing = acting_profile(source, expressions, cfg, pose, guides=True)
        card(root, defs, drawing, f"guide-{pose}", (x, 126), cfg["acting_window"], 1.65)
    return root


def main():
    cfg = json.loads(CONFIG.read_text())
    source = ET.parse(DIRECTIONS).getroot()
    expressions = ET.parse(ACTING).getroot()
    for key, art in [
        ("face_directions", direction_board(source, cfg)),
        ("expressions", acting_board(source, expressions, cfg)),
        ("gaze_bite", guide_board(source, expressions, cfg)),
    ]:
        write(art, OUTPUT / f"{key}.svg")


if __name__ == "__main__":
    main()
