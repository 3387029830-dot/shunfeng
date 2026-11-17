#!/usr/bin/env python3
"""Export the Gate 4.5 boards, independent checks, and comparison PNGs."""
import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from render_stage3 import (
    embedded_image, label, read_source, remove_groups, render, sheet, variant_source,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source/stage4_5"
PREVIEWS = ROOT / "previews/stage4_5"
DELIVERY = "delivery-assembly"
BOARDS = {
    "b4-a": "稳健修正｜短门槛与落地包裹",
    "b4-b": "品牌嵌入｜箱壁翻片与封合带",
    "b4-c": "同城叙事｜街面连续到接收湾",
}
CHECKS = {
    "silhouette": "纯黑剪影",
    "grayscale": "灰阶",
    "thumbnail": "缩略图 · 128 × 160",
    "no-headline": "去标题",
    "no-brand": "只去品牌文字",
    "no-delivery": "移除连接和交付包裹",
}


def prepare_variant(source, variant, check):
    if check in {"no-brand", "no-delivery"}:
        tree = read_source(source, DELIVERY)
        group = "brand-name" if check == "no-brand" else DELIVERY
        remove_groups(tree.getroot(), {group})
        tree.write(variant, encoding="utf-8", xml_declaration=True)
    else:
        variant_source(source, variant, check, DELIVERY)


def render_checks(inkscape, source, directory, slug, caption, outputs):
    files = {}
    for check in CHECKS:
        svg = directory / f"{slug}-{check}.svg"
        prepare_variant(source, svg, check)
        png = PREVIEWS / svg.with_suffix(".png").name
        width = 128 if check == "thumbnail" else 640
        outputs[png.name] = render(inkscape, svg, png, width, width * 5 // 4)
        files[check] = png

    items = [label(44, 53, f"{slug.upper()}  {caption}", 25, 600),
             label(44, 82, "独立诊断 · 缩略图按原生像素排入 · 去品牌仅隐藏文字", 15)]
    for index, (check, caption) in enumerate(CHECKS.items()):
        x, y = 44 + (index % 3) * 241, 128 + (index // 3) * 278
        width = 128 if check == "thumbnail" else 176
        items.extend((label(x, y, caption, 17, 600),
                      embedded_image(files[check], x, y + 14, width, width * 5 // 4)))
    svg = directory / f"{slug}-checks.svg"
    sheet(svg, 748, 675, items)
    png = PREVIEWS / svg.with_suffix(".png").name
    outputs[png.name] = render(inkscape, svg, png, 748, 675)


def render_comparison(inkscape, directory, outputs):
    items = [label(48, 58, "顺丰同城 · Gate 4.5 结构对照", 31, 600),
             label(48, 91, "同一包裹城市 · 4:5 临时画幅 · 品牌资产待核验", 16)]
    for index, (slug, caption) in enumerate(BOARDS.items()):
        x = 48 + index * 424
        items.extend((label(x, 143, f"{slug.upper()}  {caption}", 20, 600),
                      embedded_image(PREVIEWS / f"{slug}.png", x, 163, 384, 480)))
    svg = directory / "comparison.svg"
    sheet(svg, 1328, 687, items)
    png = PREVIEWS / "comparison.png"
    outputs[png.name] = render(inkscape, svg, png, 1328, 687)


def main():
    default = shutil.which("inkscape") or "/Applications/Inkscape.app/Contents/MacOS/inkscape"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inkscape", default=default, help="path to the Inkscape executable")
    args = parser.parse_args()
    version = subprocess.check_output([args.inkscape, "--version"], text=True).strip()
    if not version.startswith("Inkscape 1.4.4 "):
        parser.error(f"Gate 4.5 requires Inkscape 1.4.4; found {version}")

    PREVIEWS.mkdir(parents=True, exist_ok=True)
    outputs = {}
    with tempfile.TemporaryDirectory(prefix="sf-stage45-") as tmp:
        directory = Path(tmp)
        for slug, caption in BOARDS.items():
            source = SOURCE / f"{slug}.svg"
            read_source(source, DELIVERY)
            query = subprocess.check_output([args.inkscape, str(source), "--query-all"], text=True)
            objects = {line.split(",", 1)[0] for line in query.splitlines()}
            required = {"scene", "headline", "brand-name", "carton-back", "inside-city",
                        "inside-street", "outside-landing", DELIVERY, "exit-connection", "delivered-parcel"}
            if not required.issubset(objects):
                raise ValueError(f"{slug}: missing editable objects {sorted(required - objects)}")
            png = PREVIEWS / f"{slug}.png"
            outputs[png.name] = render(args.inkscape, source, png, 640, 800)
            render_checks(args.inkscape, source, directory, slug, caption, outputs)
        render_comparison(args.inkscape, directory, outputs)
    print(json.dumps({"engine": version, "source_checks": "PASS for all 3",
                      "previews": outputs}, indent=2))


if __name__ == "__main__":
    main()
