#!/usr/bin/env python3
"""Export the editable Gate 3 boards and review images using Inkscape."""
import argparse
import base64
import hashlib
import json
import re
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source/stage3"
PREVIEWS = ROOT / "previews/stage3"
SVG = "http://www.w3.org/2000/svg"
INKSCAPE = "http://www.inkscape.org/namespaces/inkscape"
BOARDS = (
    ("g3-b", "G3-B", "一座城市装进一个包裹", "delivery-threshold"),
    ("g3-c", "G3-C", "折叠城市", "fold-bearing"),
    ("g3-c05", "G3-C05", "包裹成为城市连接器", "connecting-parcel"),
)
VARIANTS = (
    ("silhouette", "纯黑剪影", 176),
    ("grayscale", "灰阶", 176),
    ("thumbnail", "缩略图 · 128 × 160", 128),
    ("no-headline", "去掉标题", 176),
    ("no-identity", "去掉标题和品牌", 176),
    ("no-part", "移除交付构件", 176),
)
ET.register_namespace("", SVG)
ET.register_namespace("inkscape", INKSCAPE)


def read_source(path, part):
    tree = ET.parse(path)
    root = tree.getroot()
    assert root.tag == f"{{{SVG}}}svg" and root.attrib["viewBox"] == "0 0 640 800", path.name
    assert (root.attrib["width"], root.attrib["height"]) == ("640", "800"), path.name
    elements = list(root.iter())
    assert all(element.tag.rsplit("}", 1)[-1] not in {"image", "script", "foreignObject"}
               for element in elements), path.name
    assert all("href" not in key.rsplit("}", 1)[-1] for element in elements
               for key in element.attrib), path.name
    ids = [element.attrib["id"] for element in elements if "id" in element.attrib]
    assert len(ids) == len(set(ids)), path.name
    required = {"paper", "scene", "headline", "auxiliary", "brand-name", part}
    assert required.issubset(ids), path.name
    assert len(root.findall(f".//{{{SVG}}}path")) > 12, path.name
    brand = root.find(".//*[@id='brand-name']")
    assert "".join(brand.itertext()).strip() == "顺丰同城", path.name
    return tree


def remove_groups(root, ids):
    for parent in root.iter():
        for child in list(parent):
            if child.get("id") in ids:
                parent.remove(child)


def grayscale(color):
    rgb = [int(color[i:i + 2], 16) for i in (1, 3, 5)]
    value = round(sum(c * coefficient for c, coefficient in zip(rgb, (0.2126, 0.7152, 0.0722))))
    return "#" + f"{value:02x}" * 3


def variant_source(source, path, mode, part):
    tree = read_source(source, part)
    root = tree.getroot()
    if mode in {"silhouette", "no-headline", "no-identity", "no-part"}:
        remove_groups(root, {"headline", "auxiliary"})
    if mode in {"silhouette", "no-identity", "no-part"}:
        remove_groups(root, {"brand-name"})
    if mode == "no-part":
        remove_groups(root, {part})
    if mode == "silhouette":
        root.find(".//*[@id='paper']")[0].set("fill", "#ffffff")
        for element in root.find(".//*[@id='scene']").iter():
            for attr in ("fill", "stroke"):
                if element.get(attr, "none") != "none":
                    element.set(attr, "#000000")
    if mode == "grayscale":
        for element in root.iter():
            for attr in ("fill", "stroke"):
                paint = element.get(attr, "")
                if re.fullmatch(r"#[0-9a-fA-F]{6}", paint):
                    element.set(attr, grayscale(paint))
    tree.write(path, encoding="utf-8", xml_declaration=True)


def png_metrics(path):
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", path.name
    width, height = struct.unpack(">II", data[16:24])
    return width, height, data


def render(inkscape, svg, png, width, height):
    subprocess.run([inkscape, str(svg), f"--export-filename={png}", f"--export-width={width}"],
                   check=True, stdout=subprocess.DEVNULL)
    actual_width, actual_height, data = png_metrics(png)
    assert (actual_width, actual_height) == (width, height), png.name
    return {"width": width, "height": height, "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest()}


def embedded_image(png, x, y, width, height):
    _, _, data = png_metrics(png)
    encoded = base64.b64encode(data).decode("ascii")
    return (f'<image x="{x}" y="{y}" width="{width}" height="{height}" '
            f'xlink:href="data:image/png;base64,{encoded}"/>')


def label(x, y, text, size, weight=400):
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}">'
            f'{escape(text)}</text>')


def sheet(path, width, height, elements):
    items = "\n".join(elements)
    path.write_text(f'''<svg xmlns="{SVG}" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="#e6e9e5"/>
  <g font-family="PingFang SC, Heiti SC, sans-serif" fill="#263331">
{items}
  </g>
</svg>
''', encoding="utf-8")


def comparison_sheet(directory, boards):
    items = [label(48, 58, "顺丰同城 · Gate 3 方向对照", 31, 600),
             label(48, 91, "低保真构图 · 统一 4:5 临时画幅 · 品牌资产待核验", 16)]
    for index, (slug, code, caption, _) in enumerate(BOARDS):
        x = 48 + index * 424
        items.append(label(x, 143, f"{code}  {caption}", 21, 600))
        items.append(embedded_image(boards[slug], x, 163, 384, 480))
    path = directory / "comparison.svg"
    sheet(path, 1328, 687, items)
    return path


def diagnostic_sheet(directory, slug, code, caption, files):
    items = [label(46, 51, f"{code}  {caption}", 26, 600),
             label(46, 80, "剪影保留外轮廓 · 缩略图按原生像素排入 · 移除构件保留其余结构", 15)]
    for index, (mode, title, width) in enumerate(VARIANTS):
        x = 46 + index % 3 * 240
        y = 126 + index // 3 * 283
        items.append(label(x, y, title, 17, 600))
        items.append(embedded_image(files[mode], x, y + 13, width, width * 5 // 4))
    path = directory / f"{slug}-checks.svg"
    sheet(path, 748, 680, items)
    return path


def main():
    default = shutil.which("inkscape") or "/Applications/Inkscape.app/Contents/MacOS/inkscape"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inkscape", default=default, help="path to the Inkscape executable")
    args = parser.parse_args()
    version = subprocess.check_output([args.inkscape, "--version"], text=True).strip()
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    outputs, board_images, checks = {}, {}, {}
    with tempfile.TemporaryDirectory(prefix="sf-stage3-") as temp:
        directory = Path(temp)
        for slug, code, caption, part in BOARDS:
            source = SOURCE / f"{slug}.svg"
            read_source(source, part)
            queried = subprocess.check_output([args.inkscape, str(source), "--query-all"], text=True)
            objects = {line.split(",", 1)[0] for line in queried.splitlines()}
            assert {"scene", "headline", "brand-name", part}.issubset(objects), slug
            board_images[slug] = PREVIEWS / f"{slug}.png"
            outputs[board_images[slug].name] = render(args.inkscape, source, board_images[slug], 640, 800)
            files = {}
            checks[slug] = {}
            for mode, _, width in VARIANTS:
                path = directory / f"{slug}-{mode}.svg"
                variant_source(source, path, mode, part)
                files[mode] = path.with_suffix(".png")
                checks[slug][mode] = render(args.inkscape, path, files[mode], width, width * 5 // 4)
            png = PREVIEWS / f"{slug}-checks.png"
            diagram = diagnostic_sheet(directory, slug, code, caption, files)
            outputs[png.name] = render(args.inkscape, diagram, png, 748, 680)
        png = PREVIEWS / "comparison.png"
        outputs[png.name] = render(args.inkscape, comparison_sheet(directory, board_images), png, 1328, 687)

    print(json.dumps({"engine": version, "source_checks": "PASS for all 3",
                      "previews": outputs, "embedded_diagnostic_tiles": checks}, indent=2))


if __name__ == "__main__":
    main()
