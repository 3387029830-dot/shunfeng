"""Build the isolated head/neck/shoulder review from authored SVG paths."""
import copy
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from stage1.build import canvas, elem, ellipse, label, path, stamp, write

STUDY = "head_neck_shoulder_study"
SRC = ROOT / "source/stage11" / STUDY
OUT = SRC / "generated"
INPUT = SRC / "refined/contours.svg"
CONFIG = ROOT / "config/stage11" / STUDY / "study.json"
POSE_COORDINATES = ROOT / "source/stage11/generated/pose_coordinates.json"
SILHOUETTE = {"back-hair", "head-neck", "top", "fringe"}
POSES = ("P1", "P2", "P3")


def artwork(source, key, mode, settings):
    root = canvas(248, 202)
    figure = copy.deepcopy(source.find(f"./*[@id='{key}']"))
    figure.set("data-character", settings["character"])
    root.append(figure)
    if mode == "silhouette":
        for part in list(figure):
            if part.get("id").removeprefix(f"{key}-") in SILHOUETTE:
                part.set("fill", "#000000")
            else:
                figure.remove(part)
    if mode == "landmarks":
        overlay = elem(root, "g", id="landmarks")
        offsets = [(-13, -10), (16, -6), (-18, 8), (-14, 18), (24, 11)]
        for i, ((x, y), (dx, dy)) in enumerate(zip(settings["landmarks"][key], offsets), 1):
            dest = x+dx, y+dy
            path(overlay, f"leader-{i}", f"M {x} {y} L {dest[0]} {dest[1]}",
                 stroke="#303030", width=.65)
            ellipse(overlay, f"point-{i}", (x, y), 1.85, 1.85, "#ffffff", "#303030")
            circle = ellipse(overlay, f"label-point-{i}", dest, 4.7, 4.7, "#ffffff", "#303030")
            circle.set("stroke-width", ".75")
            label(overlay, str(i), dest[0]-1.75, dest[1]+2.05, 5.8, "#202020", "bold")
    return root


def card(board, defs, image, prefix, dest, crop, scale):
    x, y = dest
    left, top, width, height = crop
    block = elem(board, "g", id=f"{prefix}-frame")
    elem(block, "rect", x=x, y=y, width=width*scale, height=height*scale, fill="#f5f5f5")
    clip = elem(defs, "clipPath", id=f"{prefix}-clip")
    elem(clip, "rect", x=x, y=y, width=width*scale, height=height*scale)
    interior = elem(block, "g", clip_path=f"url(#{prefix}-clip)")
    stamp(interior, image, prefix, x-left*scale, y-top*scale, scale)


def make_board(width, height, title, note):
    board = canvas(width, height)
    elem(board, "rect", id="paper", width="100%", height="100%", fill="#e5e5e5")
    label(board, title, 30, 38, 26, "#252525", "bold")
    label(board, note, 30, 64, 15, "#575757")
    return board, elem(board, "defs")


def closeups(source, cfg):
    crop, scale = cfg["head_neck_viewBox"], 1.9
    board, defs = make_board(1108, 1006, "Head, neck and shoulder",
                             "Six hand-drawn contours / same scale and crop")
    for row, pose in enumerate(POSES):
        for column, (version, mode) in enumerate([
            ("A", "values"), ("A", "silhouette"), ("B", "values"), ("B", "silhouette")
        ]):
            key = f"{pose}-{version}"
            x, y = 30+269*column, 111+299*row
            label(board, f"{key}  /  {mode}", x, y-8, 14)
            card(board, defs, artwork(source, key, mode, cfg), f"{key}-{mode}", (x, y), crop, scale)
    return board


def landmarks(source, cfg):
    crop, scale = cfg["head_neck_viewBox"], 1.82
    board, defs = make_board(836, 653, "Anatomical landmarks",
                             "  /  ".join(f"{i} {name}" for i, name in enumerate(cfg["markers"], 1)))
    for row, version in enumerate(("A", "B")):
        for column, pose in enumerate(POSES):
            key = f"{pose}-{version}"
            x, y = 30+268*column, 112+276*row
            label(board, key, x, y-9, 14)
            card(board, defs, artwork(source, key, "landmarks", cfg), f"{key}-guide", (x, y), crop, scale)
    return board


def thumbnails(source, cfg):
    crop, scale = cfg["upper_body_viewBox"], .50
    board, defs = make_board(759, 408, "Upper-body read at small size",
                             "Native preview scale 1:2 / grey and silhouette")
    for row, version in enumerate(("A", "B")):
        for column, pose in enumerate(POSES):
            key = f"{pose}-{version}"
            x, y = 30+248*column, 112+147*row
            label(board, key, x, y-9, 14)
            for i, mode in enumerate(("values", "silhouette")):
                xx = x+112*i
                card(board, defs, artwork(source, key, mode, cfg), f"{key}-small-{mode}",
                     (xx, y), crop, scale)
                label(board, mode, xx, y+113, 12, "#555555")
    return board


def main():
    cfg = json.loads(CONFIG.read_text())
    source = ET.parse(INPUT).getroot()
    coords = json.loads(POSE_COORDINATES.read_text())
    for pose in POSES:
        points = coords["poses"][pose]["positions"]
        origin = [round(v-a, 3) for v, a in zip(points["near_shoulder"], cfg["local_shoulder_anchor"])]
        for version in ("A", "B"):
            key = f"{pose}-{version}"
            figure = source.find(f"./*[@id='{key}']")
            assert figure is not None and figure.find(f"./*[@id='{key}-head-neck']") is not None, key
            assert len(cfg["landmarks"][key]) == len(cfg["markers"])
            # Local origin for subsequent rig placement. No global rotation of the head.
            figure.set("data-rig-origin", " ".join(map(str, origin)))
    for name, board in [
        (STUDY, closeups(source, cfg)),
        ("landmarks", landmarks(source, cfg)),
        ("upper_body_small", thumbnails(source, cfg)),
    ]:
        write(board, OUT / f"{name}.svg")


if __name__ == "__main__":
    main()
