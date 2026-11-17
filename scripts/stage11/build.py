"""Build editable Stage 1.1 studies from a shared rig and authored SVG curves."""
import argparse
import copy
import json
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from stage1 import build as old

add, angle, canvas, elem, ellipse, layer, path, polar, tag, write, xy = (
    old.add, old.angle, old.canvas, old.elem, old.ellipse, old.layer,
    old.path, old.polar, old.tag, old.write, old.xy
)
ROOT = old.ROOT
SOURCE = ROOT / "source/stage11"
CONFIG = ROOT / "config/stage11/geometry.v1.json"
GENERATED = SOURCE / "generated"
ROOM = SOURCE / "shared/room.svg"
SHAPES = SOURCE / "refined/character.svg"
POSES = ("P1", "P2", "P3")
VARIANTS = ("", "_silhouette", "_rig", "_C")
DETAILS = {"collar", "shirt-folds", "hair-tie", "tail-fold", "hair-sweep",
           "ear", "ear-fold", "expression", "wardrobe", "props"}
FACE = {
    "P1": ("M 5 -47 Q 12 -51 19 -46", "M 5 -40 Q 13 -44 19 -39",
           (16, -40), "M 15 -21 Q 21 -18 25 -23"),
    "P2": ("M 5 -46 Q 11 -48 18 -45", "M 5 -39 Q 12 -42 19 -38",
           (16, -37.5), "M 17 -22 Q 21 -21 25 -22"),
    "P3": ("M 5 -47 Q 12 -50 19 -46", "M 5 -39 Q 12 -44 19 -38",
           (16, -38.5), "M 13 -22 Q 20 -19 25 -24 Q 23 -16 18 -17 Z"),
}
HAND = {
    "P1": "M -4 -7 C 4 -8 8 -7 12 -4 L 24 0 Q 26 3 21 4 L 13 3 L 22 7 Q 22 10 17 9 L 7 6 Q -1 7 -5 3 Z",
    "P2": "M -5 -7 Q 4 -9 8 -8 L 18 -13 Q 22 -13 21 -10 L 14 -4 L 23 -6 Q 28 -5 24 -1 L 14 4 Q 6 9 -4 6 Z",
    "P3": "M -4 -7 Q 4 -10 10 -8 L 22 -8 Q 26 -6 22 -3 L 15 -2 L 20 1 Q 22 6 16 6 L 8 5 Q 1 8 -4 6 Z",
}
SUPPORTS = {
    "P1": [(251, 548), (344, 610), (378, 613), (589, 626)],
    "P2": [(355, 612), (378, 613), (589, 626)],
    "P3": [(364, 613), (378, 613), (589, 626)],
}


def take(parent, source, identifier):
    item = copy.deepcopy(source.find(f"./*[@id='{identifier}']"))
    parent.append(item)
    return item


def rig(config, pose, leg):
    base = dict(config, leg_angles={side: leg[side] for side in ("near", "far")})
    points = old.rig(base, pose)
    points["head_top"] = polar(points["head_top"], -4, pose["head"]+90)
    for side in ("near", "far"):
        points[f"{side}_sock_tip"] = polar(points[f"{side}_ankle"], 34, leg["sock_angle"])
    return points


def pants_outline(start, knee, ankle):
    # Anatomical landmarks set the normals. Cubics carry thigh, soft knee and taper.
    a, b = angle(start, knee), angle(knee, ankle)

    def side(sign):
        return [polar(p, width, theta + sign * 90) for p, width, theta in [
            (start, 26, a), (polar(start, 33, a), 29, a),
            (polar(knee, -20, a), 21, a), (knee, 20, (a+b)/2),
            (polar(knee, 28, b), 20, b), (polar(ankle, -23, b), 14, b),
            (ankle, 12, b),
        ]]

    u, v = map(side, (-1, 1))
    return (f"M {xy(u[0])} C {' '.join(map(xy, u[1:4]))} C {' '.join(map(xy, u[4:]))} "
            f"Q {xy(polar(ankle, 4, b))} {xy(v[6])} "
            f"C {' '.join(map(xy, v[5:2:-1]))} C {' '.join(map(xy, v[2::-1]))} "
            f"Q {xy(polar(start, 28, a+180))} {xy(u[0])} Z")


def leg_shape(parent, joints, side, leg, palette):
    group = elem(parent, "g", id=f"{side}-leg")
    start, knee, ankle = (joints[f"{side}_{key}"] for key in ("hip", "knee", "ankle"))
    suffix = "" if side == "near" else "_far"
    sock = elem(group, "g", id=f"{side}-foot", transform=f"translate({xy(ankle)}) rotate({leg['sock_angle']})")
    path(sock, f"{side}-sock", "M -15 -8 Q -7 -13 1 -10 C 10 -10 15 -5 25 -6 "
         "C 34 -7 38 -1 34 5 Q 31 11 14 12 L -7 14 Q -17 12 -17 4 Z",
         palette["sock" + suffix])
    path(group, f"{side}-pants", pants_outline(start, knee, ankle), palette["pants" + suffix])
    if side == "near":
        style = elem(group, "g", id="wardrobe")
        a = angle(start, knee)
        path(style, "knee-drape", f"M {xy(polar(knee, 15, a-140))} Q {xy(knee)} "
             f"{xy(polar(knee, 23, a+34))}", stroke=palette["pants_fold"], width=1.7)
        path(style, "sock-crease", f"M {xy(add(ankle, (7, 3)))} q 2 2 5 1",
             stroke=palette["pants_fold"], width=1.3)


def arm(parent, joints, side, name, palette):
    g = elem(parent, "g", id=f"{side}-arm")
    shoulder, elbow, wrist = (joints[f"{side}_{k}"] for k in ("shoulder", "elbow", "wrist"))
    a, b = angle(shoulder, elbow), angle(elbow, wrist)
    near = side == "near"
    skin = palette["skin" if near else "skin_far"]
    cuff = polar(wrist, -15, b)
    path(g, f"{side}-sleeve", old.limb_profile((shoulder, elbow, cuff), (18 if near else 16, 15, 10)),
         palette["top" if near else "top_far"], palette["top_edge"], 1.15)
    path(g, f"{side}-wrist", old.tube(polar(cuff, -1, b), polar(wrist, 5, b), 7.3, 6.6),
         skin, palette["skin_edge"], .8)
    hand = elem(g, "g", id=f"{side}-hand", transform=f"translate({xy(wrist)}) rotate({b:.3f})")
    grip = HAND[name]
    if name == "P3" and not near:
        grip = "M -4 -7 Q 3 -9 8 -8 L 12 -5 Q 14 0 10 3 Q 8 8 2 7 L -5 6 Z"
    path(hand, f"{side}-fingers", grip, skin, palette["skin_edge"], 1)
    path(g, f"{side}-cuff", f"M {xy(polar(cuff, 9, b+90))} L {xy(polar(cuff, 9, b-90))}",
         stroke=palette["top_fold"], width=1.1)
    return g


def props(parent, points, name, palette):
    g = elem(parent, "g", id="props")
    if name == "P2":
        wrist = points["far_wrist"]
        phone = elem(g, "g", id="phone", transform=f"translate({xy(add(wrist, (-7, -4)))}) rotate(-28)")
        elem(phone, "rect", id="phone-block", x=-6, y=-28, width=16, height=34, rx=3,
             fill=palette["ink"])
    if name == "P3":
        x, y = add(points["near_wrist"], (11, -8))
        plate = elem(g, "g", id="plate", transform=f"translate({x:.3f} {y:.3f})")
        path(plate, "plate-outline", "M -19 -3 Q 0 -7 31 -4 L 27 0 Q 5 4 -16 1 Z", "#888888")
        path(plate, "cake-block", "M -10 -6 L -8 -26 Q 2 -30 17 -20 L 21 -7 Q 6 -4 -10 -6 Z",
             "#c1c1c1", "#666666", 1)
        path(plate, "cake-edge", "M -8 -16 Q 5 -18 18 -13", stroke="#8d8d8d", width=1.3)
        end = add(points["far_wrist"], (7, -4))
        tip = add(end, (-20, -13))
        path(g, "fork", f"M {xy(end)} L {xy(tip)} l -6 -1 l 1 3 l 5 2",
             stroke="#5c5c5c", width=1.9)


def figure(root, cfg, name, shapes, leg, hair):
    pose, palette = cfg["poses"][name], cfg["palette"]
    points = rig(cfg, pose, leg)
    hip, neck = points["pelvis"], points["neck"]
    g = layer(root, "Adult woman / figure", "figure")
    g.set("data-character", cfg["character"])
    leg_shape(g, points, "far", leg, palette)
    ellipse(g, "pelvis", hip, 31, 28, palette["pants"])
    leg_shape(g, points, "near", leg, palette)
    arm(g, points, "far", name, palette)
    rot = pose["torso"] + 90
    path(g, "neck", old.tube(polar(points["shoulder"], -6, pose["torso"]),
         polar(neck, 10, pose["head"]), 14, 13), palette["skin"], palette["skin_edge"], 1)
    top = elem(g, "g", id="upper-body", transform=f"translate({xy(hip)}) rotate({rot})")
    take(top, shapes, "shirt")
    head = elem(g, "g", id="head", transform=f"translate({xy(neck)}) rotate({pose['head']+90})")
    take(head, shapes, hair + "-back")
    take(head, shapes, "face-outline")
    take(head, shapes, "fringe")
    expr = elem(head, "g", id="expression")
    brow, eye, iris, lip = FACE[name]
    path(expr, "brow", brow, stroke=palette["ink"], width=1.65)
    path(expr, "eye", eye, stroke=palette["ink"], width=1.8)
    ellipse(expr, "iris", iris, 2.45, 2.55, palette["ink"])
    path(expr, "mouth", lip, palette["ink"] if name == "P3" else "none", palette["ink"], 1.35)
    if name == "P3":
        path(expr, "cheek-lift", "M 8 -26 Q 10 -25 11 -27", stroke="#8c8c8c", width=1.2)
    props(g, points, name, palette)
    arm(g, points, "near", name, palette)
    return points


def silhouette(g, keep=None):
    for child in list(g):
        if child.get("id") in DETAILS or (keep is not None and child.get("id") not in keep):
            g.remove(child)
        else:
            silhouette(child)
    if g.get("fill", "none") != "none":
        g.set("fill", "#363636")
    if g.get("stroke") is not None:
        g.set("stroke", "none")


def new_canvas():
    root = canvas(700, 990)
    elem(root, "rect", id="paper", width=700, height=990, fill="#f5f5f5")
    return root


def scene(root, room, sofa, full):
    bg = layer(root, "Room", "setting")
    if full:
        take(bg, room, "background")
    take(bg, room, sofa).set("id", "sofa")


def cues(root, cfg, kind):
    g = layer(root, "Clock / " + kind, "clock")
    if kind == "A":
        return
    c, origin = cfg["clock"], cfg["pelvis"]
    radius = c["radius"]
    if kind == "B":
        a, b = (polar(origin, radius, t) for t in c["arc"])
        path(g, "open-arc", f"M {xy(a)} A {radius} {radius} 0 0 1 {xy(b)}",
             stroke="#a5a5a5", width=2)
    for i, t in enumerate(c[kind]):
        r = c["foot_tick_radius"] if t == c[kind][-1] else radius
        a, b = polar(origin, r-5, t), polar(origin, r+5, t)
        path(g, f"tick-{i}", f"M {xy(a)} L {xy(b)}", stroke="#828282", width=2.25)


def diagnostic(root, points, cfg, name, contact):
    old.skeleton(root, points, dict(cfg, safe_y=[155, 825]))
    g = root.find("./*[@id='rig']")
    if contact:
        for i, p in enumerate(SUPPORTS[name]):
            ellipse(g, f"support-{i}", p, 4.5, 4.5, "#414141", "#ffffff")
        path(g, "hip-load-direction", "M 364 594 V 609 M 361 606 L 364 610 L 367 606",
             stroke="#393939", width=1.25)


def drawing(cfg, shapes, room, name, *, leg=None, hair=None, sofa=None, setting="room",
            variant="A", mode="normal"):
    root = new_canvas()
    if setting != "none":
        scene(root, room, sofa or cfg["selected_scene"], setting == "room")
    cues(root, cfg, variant)
    points = figure(root, cfg, name, shapes,
                    cfg["leg_trials"][leg or cfg["selected_leg"]], hair or cfg["selected_hair"])
    fig = root.find("./*[@id='figure']")
    if mode == "silhouette":
        root.remove(root.find("./*[@id='clock']"))
        silhouette(fig)
    if mode == "rig":
        fig.set("opacity", ".28")
        diagnostic(root, points, cfg, name, setting != "none")
    return root


def sheet(title, rows, crop=(0, 0, 700, 990), scale=.57):
    """Stamp equal viewports in every row. Captions stay outside the crop."""
    x0, y0, w, h = crop
    gap, margin, row_top, row_gap = 20, 26, 81, 40
    cell_w, cell_h = w*scale, h*scale
    cols = max(map(len, rows))
    root = canvas(math.ceil(2*margin + cols*cell_w + (cols-1)*gap),
                  math.ceil(row_top + len(rows)*(cell_h+row_gap)-row_gap+margin))
    elem(root, "rect", id="sheet-paper", width="100%", height="100%", fill="#d6d6d6")
    old.label(root, title, margin, 34, 23, weight="bold")
    defs = elem(root, "defs")
    for r, row in enumerate(rows):
        for c, (caption, drawing) in enumerate(row):
            x, y = margin+c*(cell_w+gap), row_top+r*(cell_h+row_gap)
            if caption:
                old.label(root, caption, x, y-10, 15)
            prefix = f"row-{r+1}-cell-{c+1}"
            clip = elem(defs, "clipPath", id=prefix+"-clip")
            elem(clip, "rect", x=x, y=y, width=cell_w, height=cell_h)
            viewport = elem(root, "g", clip_path=f"url(#{prefix}-clip)")
            old.stamp(viewport, drawing, prefix, x-x0*scale, y-y0*scale, scale)
    return root


def structural_boards(cfg, shapes):
    # Read the frozen reference source, never write into Stage 1.
    leg = json.loads(old.CONFIG.read_text())
    contours = json.loads(old.CONTOURS.read_text())
    prior = new_canvas()
    points = old.figure(prior, leg, leg["poses"]["P2"], contours)
    fig = prior.find("./*[@id='figure']")
    silhouette(fig, {"far-leg", "pelvis", "near-leg"})
    prior_axes = copy.deepcopy(prior)
    old.skeleton(prior_axes, points, leg)
    for node in list(prior_axes[-1]):
        if node.get("id") not in {"bone-chain-2", "bone-chain-4", "axis-legs",
                                 "joint-pelvis", "joint-near_knee", "joint-far_knee",
                                 "joint-near_ankle", "joint-far_ankle"}:
            prior_axes[-1].remove(node)
    prior_axes[1].set("opacity", ".27")
    rows = [[("Stage 1 / 41° + 43°", prior)],
            [("Old joints", prior_axes)]]
    for trial in ("L0", "L1"):
        d = drawing(cfg, shapes, None, "P2", leg=trial, setting="none", mode="silhouette")
        silhouette(d[-1], {"far-leg", "pelvis", "near-leg"})
        angles = cfg["leg_trials"][trial]
        deflections = [abs(a-b) for a, b in (angles["near"], angles["far"])]
        rows[0].append((f"{trial} / {deflections[0]}° + {deflections[1]}°", d))
        axes = copy.deepcopy(d)
        axes[-1].set("opacity", ".27")
        current_rig = rig(cfg, cfg["poses"]["P2"], cfg["leg_trials"][trial])
        g = elem(axes, "g", id="leg-axes")
        for side in ("near", "far"):
            pts = [current_rig[f"{side}_{k}"] for k in ("hip", "knee", "ankle", "sock_tip")]
            path(g, f"{side}-chain", "M " + " L ".join(map(xy, pts)),
                 stroke="#393939" if side == "near" else "#757575", width=1.6)
            for index, p in enumerate(pts):
                ellipse(g, f"{side}-joint-{index}", p, 3.2, 3.2, "#f5f5f5", "#484848")
        rows[1].append((f"{trial} joints", axes))

    hair = [[(f"{n} / {h}", drawing(cfg, shapes, None, n, hair=h, setting="none"))
             for n in POSES] for h in ("H0", "H1")]
    expression = [[(label, drawing(cfg, shapes, None, name, setting="none"))
                   for label, name in zip(("P1 / anticipation", "P2 / attention", "P3 / about to taste"), POSES)]]
    bodies = [[(f"{n} / silhouette", drawing(cfg, shapes, None, n, setting="none", mode="silhouette"))
               for n in POSES],
              [(f"{n} / body and joints", drawing(cfg, shapes, None, n, setting="none", mode="rig"))
               for n in POSES]]
    darker = copy.deepcopy(cfg)
    darker["palette"].update(sock=cfg["palette"]["pants"], sock_far=cfg["palette"]["pants_far"])
    points = rig(cfg, cfg["poses"]["P2"], cfg["leg_trials"][cfg["selected_leg"]])
    toe_length = round(math.dist(points["pelvis"], points["near_sock_tip"]))
    crown_length = round(math.dist(points["pelvis"], points["head_top"]))
    reach = [(f"{label} / {toe_length} u", drawing(current, shapes, None, "P2", setting="none"))
             for label, current in [("Continuous dark", darker), ("Lighter socks", cfg)]]
    return {
        "leg_comparison": sheet("Lower-body axis / same scale and pelvis", rows, (310, 535, 340, 145), 1.06),
        "female_identity": sheet("Head identity / low tie and shoulder-length trial", hair, (174, 365, 283, 194), 1.22),
        "expression_study": sheet("Gaze to gesture / same camera", expression, (174, 365, 315, 247), 1.28),
        "reach_comparison": sheet(f"Optical ends / fixed {crown_length} u crown reach", [reach], (222, 367, 403, 267), 1.04),
        "body_study": sheet("Structure first / silhouettes and joints", bodies, (150, 342, 512, 314), .78),
    }


def coordinates(cfg):
    out = {"viewBox": cfg["viewBox"], "pelvis": cfg["pelvis"], "character": cfg["character"],
           "selected_leg": cfg["selected_leg"], "legs": {}, "poses": {}}
    rnd = lambda point: [round(n, 3) for n in point]
    leg = cfg["leg_trials"][cfg["selected_leg"]]
    for trial, spec in cfg["leg_trials"].items():
        points = rig(cfg, cfg["poses"]["P2"], spec)
        out["legs"][trial] = {}
        for side in ("near", "far"):
            labels = ("hip", "knee", "ankle", "sock_tip")
            p, k, a, t = [points[f"{side}_{key}"] for key in labels]
            out["legs"][trial][side] = {
                "positions": {key: rnd(pt) for key, pt in zip(labels, (p, k, a, t))},
                "segment_angles_deg": spec[side],
                "knee_deflection_deg": abs(spec[side][1]-spec[side][0]),
                "pelvis_to_tip_deg": round(angle(points["pelvis"], t), 3),
                "pelvis_to_tip_length": round(math.dist(points["pelvis"], t), 3),
            }
    for name in POSES:
        joints = rig(cfg, cfg["poses"][name], leg)
        origin, crown = joints["pelvis"], joints["head_top"]
        out["poses"][name] = {
            "pose_angles_deg": cfg["poses"][name],
            "positions": {key: rnd(p) for key, p in joints.items()},
            "pelvis_to_crown_deg": round(angle(origin, crown), 3),
            "pelvis_to_crown_length": round(math.dist(origin, crown), 3),
            "illustrated_support_points": SUPPORTS[name],
        }
    return out



def room_boards(cfg, shapes, room):
    def art(name, **kwargs):
        return drawing(cfg, shapes, room, name, **kwargs)

    study = (62, 302, 610, 505)
    layers = [[(f"{n} / {label}", art(n, setting=setting))
               for n in POSES] for setting, label in
              (("none", "figure only"), ("sofa", "shared seat"), ("room", "light room"))]
    sofas = [[(f"{n} / {sofa}", art(n, sofa=sofa, setting="sofa"))
              for n in POSES] for sofa in ("S0", "S1")]
    clock = [[(f"{n} / {v}", art(n, variant=v)) for n in POSES] for v in ("A", "B", "C")]
    overlay = new_canvas()
    scene(overlay, room, cfg["selected_scene"], True)
    for i, n in enumerate(POSES):
        fresh = new_canvas()
        figure(fresh, cfg, n, shapes, cfg["leg_trials"][cfg["selected_leg"]], cfg["selected_hair"])
        g = fresh[-1]
        silhouette(g, {"upper-body", "neck", "head", "near-leg", "far-leg", "pelvis"})
        fresh.remove(fresh[0])
        g.set("opacity", str(.24 + i*.07))
        old.stamp(overlay, fresh, n.lower(), 0, 0, 1)
    ellipse(overlay, "fixed-pelvis", cfg["pelvis"], 6.5, 6.5, "#ffffff", "#363636")
    leg = rig(cfg, cfg["poses"]["P2"], cfg["leg_trials"][cfg["selected_leg"]])
    path(overlay, "shared-leg-axis", "M " + " L ".join(
         xy(leg[key]) for key in ("pelvis", "near_knee", "near_ankle", "near_sock_tip")),
         stroke="#f5f5f5", width=1.4)
    zoom = [("P1 / B: backrest", art("P1", variant="B")),
            ("P2 / B: crown", art("P2", variant="B")),
            ("P3 / B: crown", art("P3", variant="B")),
            ("P3 / C: sock-side tick", art("P3", variant="C"))]
    for name, index in [("P2", 1), ("P3", 2)]:
        points = rig(cfg, cfg["poses"][name], cfg["leg_trials"][cfg["selected_leg"]])
        a = angle(points["pelvis"], points["head_top"])
        ray = path(zoom[index][1], "crown-direction",
                   f"M {xy(points['pelvis'])} L {xy(polar(points['pelvis'], 258, a))}",
                   stroke="#595959", width=1.35)
        ray.set("stroke-dasharray", "3 6")
    return {
        "triptych": sheet("Human clock / Stage 1.1", [[("", art(n, variant="B")) for n in POSES]]),
        "scene_layers": sheet("Three poses / figure, seat and room", layers, study, .62),
        "sofa_scene_comparison": sheet("Support study / rounded sofa and extended seat", sofas, study, .62),
        "clock_comparison": sheet("Human clock / no marks, open arc and four ticks", clock, study, .62),
        "pelvis_alignment": overlay,
        "clock_detail": sheet("Cue geometry / matched crop, original positions",
                              [zoom[:2], zoom[2:]], (134, 330, 534, 333), .99),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=CONFIG)
    parser.add_argument("--room", type=Path, default=ROOM)
    parser.add_argument("--out", type=Path, default=GENERATED)
    parser.add_argument("--pose", choices=POSES)
    parser.add_argument("--structure", action="store_true")
    args = parser.parse_args()
    out = args.out.resolve()
    if ROOT in out.parents and out != GENERATED and not out.is_relative_to(ROOT / "work"):
        parser.error("--out inside the repository must be the Stage 1.1 generated area or work/")
    if out == ROOT:
        parser.error("--out cannot be the repository root")
    cfg = json.loads(args.config.read_text())
    shapes = ET.parse(SHAPES).getroot()
    if args.structure:
        for name, image in structural_boards(cfg, shapes).items():
            write(image, args.out / f"{name}.svg")
        return
    room = ET.parse(args.room).getroot()
    for name in (args.pose,) if args.pose else POSES:
        for variant, kwargs in [
            ("", {"variant": "B"}),
            ("_silhouette", {"setting": "none", "mode": "silhouette"}),
            ("_rig", {"mode": "rig", "setting": "sofa"}),
            ("_C", {"variant": "C"}),
        ]:
            write(drawing(cfg, shapes, room, name, **kwargs), args.out / f"{name}{variant}.svg")
    if args.pose:
        return
    boards = structural_boards(cfg, shapes)
    boards.update(room_boards(cfg, shapes, room))
    for name, image in boards.items():
        write(image, args.out / f"{name}.svg")
    data = json.dumps(coordinates(cfg), indent=2, ensure_ascii=False) + "\n"
    table = args.out / "pose_coordinates.json"
    if not table.exists() or table.read_text() != data:
        table.write_text(data)


if __name__ == "__main__":
    main()
