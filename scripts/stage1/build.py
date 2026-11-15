"""Regenerate the Stage 1 roughs from the rig, authored shapes and shared sofa."""
import argparse
import copy
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "source/stage1"
CONFIG = ROOT / "config/stage1/geometry.v1.json"
CONTOURS = SOURCE / "refined/contours.json"
SVG = "http://www.w3.org/2000/svg"
INK = "http://www.inkscape.org/namespaces/inkscape"
ET.register_namespace("", SVG)
ET.register_namespace("inkscape", INK)


def tag(name):
    return f"{{{SVG}}}{name}"


def elem(parent, name, **attrs):
    return ET.SubElement(parent, tag(name), {k.replace("_", "-"): str(v) for k, v in attrs.items()})


def layer(parent, name, identifier, **attrs):
    group = elem(parent, "g", id=identifier, **attrs)
    group.set(f"{{{INK}}}groupmode", "layer")
    group.set(f"{{{INK}}}label", name)
    return group


def path(parent, identifier, d, fill="none", stroke="none", width=1):
    return elem(parent, "path", id=identifier, d=d, fill=fill, stroke=stroke,
                stroke_width=width, stroke_linecap="round", stroke_linejoin="round")


def polar(p, length, deg):
    a = math.radians(deg)
    return p[0] + length * math.cos(a), p[1] + length * math.sin(a)


def add(p, q):
    return p[0] + q[0], p[1] + q[1]


def xy(p):
    return " ".join(f"{x:.3f}" for x in p)


def angle(a, b):
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))


def ellipse(parent, identifier, p, rx, ry, fill, stroke="none"):
    return elem(parent, "ellipse", id=identifier, cx=f"{p[0]:.3f}", cy=f"{p[1]:.3f}",
                rx=rx, ry=ry, fill=fill, stroke=stroke, stroke_width=1.7)


def chain(start, lengths, angles):
    points = [start]
    for length, deg in zip(lengths, angles):
        points.append(polar(points[-1], length, deg))
    return points


def rig(config, pose):
    length = config["segment_lengths"]
    hip = tuple(config["pelvis"])
    torso = pose["torso"]
    waist, shoulder, neck = chain(hip, [length["pelvis_to_waist"],
        length["waist_to_shoulder"], length["shoulder_to_neck"]], [torso] * 3)[1:]
    joints = {"pelvis": hip, "waist": waist, "shoulder": shoulder, "neck": neck,
              "head_top": polar(neck, length["neck_to_head_top"], pose["head"])}
    for side in ("near", "far"):
        arm_root = shoulder if side == "near" else add(shoulder, config["far_shoulder_offset"])
        leg_root = hip if side == "near" else add(hip, config["far_hip_offset"])
        for names, start, lengths, angles in [
            (("shoulder", "elbow", "wrist"), arm_root,
             [length["upper_arm"], length["forearm"]], pose[f"{side}_arm"]),
            (("hip", "knee", "ankle"), leg_root,
             [length["thigh"], length["shin"]], config["leg_angles"][side]),
        ]:
            for name, p in zip(names, chain(start, lengths, angles)):
                joints[f"{side}_{name}"] = p
    return joints


def tube(start, end, first, last):
    """Rounded sleeve or short segment with tapered ends."""
    a = angle(start, end)
    u, v = polar(start, first, a + 90), polar(start, first, a - 90)
    x, y = polar(end, last, a + 90), polar(end, last, a - 90)
    return (f"M {xy(u)} Q {xy(polar(start, first * .8, a + 180))} {xy(v)} "
            f"L {xy(y)} Q {xy(polar(end, last * .22, a))} {xy(x)} Z")


def limb_profile(points, widths):
    """One continuous outline with a curved joint and narrower wrist or ankle."""
    p, j, q = points
    a, b = angle(p, j), angle(j, q)
    j_angle = a + ((b-a+180) % 360 - 180) / 2
    result = []
    for direction in (90, -90):
        result.append((polar(p, widths[0], a + direction),
            polar(polar(j, -17, a), widths[1], a + direction),
            polar(j, widths[1], j_angle + direction),
            polar(polar(j, 18, b), widths[1] * .9, b + direction),
            polar(q, widths[2], b + direction)))
    u, v = result
    return (f"M {xy(u[0])} Q {xy(polar(p, widths[0] * 1.16, a+180))} {xy(v[0])} "
            f"L {xy(v[1])} Q {xy(v[2])} {xy(v[3])} L {xy(v[4])} "
            f"Q {xy(polar(q, 3, b))} {xy(u[4])} "
            f"L {xy(u[3])} Q {xy(u[2])} {xy(u[1])} Z")


def limb(parent, joints, side, kind, contours):
    arm = kind == "arm"
    names = ("shoulder", "elbow", "wrist") if arm else ("hip", "knee", "ankle")
    start, joint, end = [joints[f"{side}_{name}"] for name in names]
    a, b = angle(start, joint), angle(joint, end)
    group = elem(parent, "g", id=f"{side}-{kind}")
    near = side == "near"
    if arm:
        hand = elem(group, "g", id=f"{side}-hand", transform=f"translate({xy(end)}) rotate({b+90:.3f})")
        path(hand, f"{side}-hand-outline", contours["hand"],
             "#d6d6d6" if near else "#b5b5b5", "#343434", 2.2)
        path(group, f"{side}-arm-outline", limb_profile((start, joint, end), (20, 13, 8)),
             "#d6d6d6" if near else "#b5b5b5", "#343434", 2.1)
        path(group, f"{side}-sleeve", tube(start, polar(start, 30, a), 23, 17),
             "#535353" if near else "#767676", "#323232", 1.8)
    else:
        foot = elem(group, "g", id=f"{side}-foot", transform=f"translate({xy(end)}) rotate(10)")
        path(foot, f"{side}-sock",
             "M -14 -2 Q -10 -11 4 -10 Q 12 -2 24 -1 Q 38 -2 40 7 "
             "Q 40 14 27 17 L -3 19 Q -15 18 -16 10 Z",
             "#555555" if near else "#747474", "#383838", 2.1)
        path(group, f"{side}-leg-outline", limb_profile((start, joint, end), (32, 23, 12)),
             "#292929" if near else "#5a5a5a", "#282828", 2.2)
        if near:
            f = polar(joint, 9, a + 90)
            g = polar(joint, 21, a + 146)
            path(group, "near-knee-fold", f"M {xy(f)} Q {xy(polar(joint, 2, a))} {xy(g)}",
                 stroke="#626262", width=1.8)


def figure(parent, config, pose, contours):
    joints = rig(config, pose)
    hip, neck = joints["pelvis"], joints["neck"]
    body = layer(parent, "人体粗轮廓", "figure")
    limb(body, joints, "far", "leg", contours)
    limb(body, joints, "far", "arm", contours)
    ellipse(body, "pelvis", hip, 38, 34, "#313131", "#252525")
    limb(body, joints, "near", "leg", contours)

    top = elem(body, "g", id="upper-body", transform=f"translate({xy(hip)}) rotate({pose['torso']+90})")
    path(top, "neck", "M -19 -104 Q -15 -119 -16 -135 L 13 -142 L 21 -113 L 15 -100 Z",
         "#d6d6d6", "#343434", 2.2)
    path(top, "torso", contours["torso"], "#414141", "#292929", 2.5)
    path(top, "torso-hem", contours["torso_hem"], stroke="#646464", width=2)
    path(top, "torso-fold", contours["torso_fold"], stroke="#616161", width=1.8)

    h = elem(body, "g", id="head", transform=f"translate({xy(neck)}) rotate({pose['head']+90})")
    path(h, "head-profile", contours["head"], "#d6d6d6", "#363636", 2.1)
    path(h, "hair", contours["hair"], "#272727")
    path(h, "face-marks", contours["face_marks"], stroke="#454545", width=1.6)
    limb(body, joints, "near", "arm", contours)
    return joints


def skeleton(parent, joints, config):
    debug = layer(parent, "关节与主方向", "rig")
    connections = [("pelvis", "waist", "shoulder", "neck", "head_top")]
    for side in ("near", "far"):
        connections.extend(tuple(f"{side}_{k}" for k in limb_names) for limb_names in
                           [("shoulder", "elbow", "wrist"), ("hip", "knee", "ankle")])
    for index, names in enumerate(connections):
        path(debug, f"bone-chain-{index}", "M " + " L ".join(xy(joints[n]) for n in names),
             stroke="#414141" if index < 3 else "#898989", width=2.6)
    for name, p in joints.items():
        ellipse(debug, f"joint-{name}", p, 4.4 if name != "pelvis" else 8,
                4.4 if name != "pelvis" else 8, "#ffffff", "#2b2b2b")
    hip = joints["pelvis"]
    for end, name in [(joints["shoulder"], "torso"), (joints["near_ankle"], "legs")]:
        q = polar(hip, 260, angle(hip, end))
        guide = path(debug, f"axis-{name}", f"M {xy(hip)} L {xy(q)}", stroke="#525252", width=1.1)
        guide.set("stroke-dasharray", "6 7")
    top, bottom = config["safe_y"]
    p = path(debug, "safety-lines", f"M 39 {top} H 661 M 39 {bottom} H 661",
             stroke="#999999", width=1)
    p.set("stroke-dasharray", "4 8")


def clock(parent, config, variant):
    overlay = layer(parent, "时钟辅助 " + variant, "clock")
    if variant == "A":
        return
    cfg = config["clock"]
    origin, radius = config["pelvis"], cfg["radius"]
    if variant == "B":
        a, b = cfg["clock_B_arc"]
        path(overlay, "clock_arc", f"M {xy(polar(origin,radius,a))} "
             f"A {radius} {radius} 0 0 1 {xy(polar(origin,radius,b))}",
             stroke="#aaaaaa", width=2)
    ticks = elem(overlay, "g", id="clock_ticks")
    for i, a in enumerate(cfg[f"clock_{variant}_ticks"]):
        line = f"M {xy(polar(origin, radius-7, a))} L {xy(polar(origin, radius+5, a))}"
        path(ticks, f"tick-{i}", line, stroke="#818181" if variant == "B" else "#a1a1a1",
             width=2.1 if variant == "B" else 1.7)


def canvas(width, height):
    return ET.Element(tag("svg"), {"width": str(width), "height": str(height),
                                 "viewBox": f"0 0 {width} {height}", "version": "1.1"})


def write(root, file):
    ET.indent(root, "  ")
    file.parent.mkdir(parents=True, exist_ok=True)
    content = ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"
    if not file.exists() or file.read_bytes() != content:
        file.write_bytes(content)


def child_without_layer(element):
    c = copy.deepcopy(element)
    for element in c.iter():
        element.attrib.pop(f"{{{INK}}}groupmode", None)
        element.attrib.pop(f"{{{INK}}}label", None)
    return c


def scene(config, pose, contours, sofa, variant="A", furniture=True, debug=False):
    _, _, w, h = config["viewBox"]
    root = canvas(w, h)
    elem(root, "rect", id="paper", x=0, y=0, width=w, height=h, fill="#ffffff")
    clock(root, config, variant)
    if furniture:
        layer(root, "共享沙发", "setting").append(copy.deepcopy(sofa))
    joints = figure(root, config, pose, contours)
    if debug:
        root.find(f"./{tag('g')}[@id='figure']").set("opacity", ".23")
        skeleton(root, joints, config)
    return root


def stamp(parent, scene, prefix, x, y, scale):
    g = elem(parent, "g", id=prefix, transform=f"translate({x} {y}) scale({scale})")
    for child in scene:
        c = child_without_layer(child)
        for node in c.iter():
            if node.get("id"):
                node.set("id", prefix + "-" + node.get("id"))
        g.append(c)


def label(parent, text, x, y, size=19, fill="#303030", weight="normal"):
    elem(parent, "text", x=x, y=y, fill=fill, font_family="sans-serif",
         font_size=size, font_weight=weight).text = text


def board(config, rows, title):
    # Explicit common transform. Captions sit in the gutter outside each artboard.
    scale, width, height, gap, margin, cap = .57, 399, 564.3, 22, 34, 28
    sheet = canvas(2*margin+3*width+2*gap, math.ceil(104+len(rows)*(height+cap+gap)))
    elem(sheet, "rect", id="board-paper", width="100%", height="100%", fill="#eeeeee")
    label(sheet, title, margin, 48, 25, weight="bold")
    for i, row in enumerate(rows):
        for j, (name, root) in enumerate(row):
            x, y = margin+j*(width+gap), 104+i*(height+cap+gap)
            label(sheet, name, x, y-11)
            stamp(sheet, root, f"cell-{i+1}-{j+1}", x, y, scale)
    return sheet


def overlay(config, contours, sofa):
    _, _, width, height = config["viewBox"]
    root = canvas(width, height)
    elem(root, "g", id="setting").append(copy.deepcopy(sofa))
    for i, (name, pose) in enumerate(config["poses"].items()):
        fig = canvas(width, height)
        figure(fig, config, pose, contours)
        fig[0].set("opacity", str([.31, .27, .23][i]))
        stamp(root, fig, name.lower(), 0, 0, 1)
    hip = config["pelvis"]
    ellipse(root, "fixed-pelvis", hip, 7, 7, "#ffffff", "#111111")
    return root


def angles_table(config):
    positions = {}
    for name, pose in config["poses"].items():
        joints = rig(config, pose)
        hip, head, ankle = (joints[k] for k in ("pelvis", "head_top", "near_ankle"))
        positions[name] = {
            "candidate_angles_deg": pose,
            "positions": {k: [round(n, 3) for n in p] for k, p in joints.items()},
            "effective_directions_deg": {
                "pelvis_to_head_top": round(angle(hip, head), 2),
                "pelvis_to_near_ankle": round(angle(hip, ankle), 2),
            },
            "reach": {
                "pelvis_to_head_top": round(math.dist(hip, head), 2),
                "pelvis_to_near_ankle": round(math.dist(hip, ankle), 2),
                "pelvis_to_near_sock_tip": round(math.dist(hip, polar(ankle, 40, 10)), 2),
            }
        }
    return positions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=CONFIG)
    parser.add_argument("--sofa", type=Path, default=SOURCE / "shared/sofa.svg")
    parser.add_argument("--out", type=Path, default=SOURCE / "generated")
    parser.add_argument("--pose", choices=["P1", "P2", "P3"],
                        help="Update only the selected pose, omitting composite boards.")
    parser.add_argument("--phase", choices=["body", "all"], default="all")
    args = parser.parse_args()
    c = json.loads(args.config.read_text())
    contours = json.loads(CONTOURS.read_text())
    sofa = ET.parse(args.sofa).getroot().find(tag("g"))
    poses = [args.pose] if args.pose else list(c["poses"])

    for name in poses:
        p = c["poses"][name]
        for suffix, furniture, debug in [("", True, False), ("_body", False, False),
                                         ("_rig", True, True)]:
            write(scene(c, p, contours, sofa, furniture=furniture, debug=debug),
                  args.out / f"{name}{suffix}.svg")
        if args.phase == "all":
            for variant in ("B", "C"):
                write(scene(c, p, contours, sofa, variant=variant),
                      args.out / f"{name}_{variant}.svg")

    if args.pose:
        return
    (args.out / "pose_coordinates.json").write_text(
        json.dumps(angles_table(c), ensure_ascii=False, indent=2) + "\n")
    if args.phase == "body":
        return
    for prep, stem, title in [("", "triptych", "Three poses / no clock marks"),
                               ("_body", "body_study", "Body blocks / sofa hidden")]:
        row = [(name, ET.parse(args.out / f"{name}{prep}.svg").getroot()) for name in poses]
        write(board(c, [row], title), args.out / f"{stem}.svg")
    compare = []
    for variant, description in [("A", "no marks"), ("B", "open arc + ticks"), ("C", "four ticks")]:
        suffix = "" if variant == "A" else f"_{variant}"
        compare.append([(f"{variant}  /  {name}  ·  {description}",
                         ET.parse(args.out / f"{name}{suffix}.svg").getroot()) for name in poses])
    write(board(c, compare, "Human clock / cue comparison"), args.out / "clock_comparison.svg")
    write(overlay(c, contours, sofa), args.out / "pelvis_alignment.svg")
    p2 = c["poses"]["P2"]
    raised = dict(p2, near_arm=c["arm_assist_trial"]["near_arm"])
    write(board(c, [[("P2 / compact hands", scene(c, p2, contours, sofa)),
                     ("P2 / raised arm trial", scene(c, raised, contours, sofa)),
                     ("P2 / compact hands + ticks", scene(c, p2, contours, sofa, "C"))]],
                "Arm extension / matched torso and legs"), args.out / "arm_assist.svg")


if __name__ == "__main__":
    main()
