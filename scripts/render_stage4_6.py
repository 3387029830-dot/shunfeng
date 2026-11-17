#!/usr/bin/env python3
"""Render the two original Gate 4.6 previsualizations and art direction boards."""
import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape

from render_stage3 import embedded_image, render

ROOT = Path(__file__).resolve().parents[1]
SCENE = ROOT / "source/stage4_6/lighting.cpp"
PREVIEWS = ROOT / "previews/stage4_6"
WIDTH, HEIGHT, SAMPLES = 720, 900, 64
ROUTES = {
    "a": {
        "name": "超现实高级静物",
        "crop": (185, 471, 354, 192),
        "detail": "主箱、微缩建筑、内外接触影",
        "criteria": [
            ("材质", "粗面纸箱与矿物质感建筑分层。"),
            ("光线", "左前大面光，暗面保留反光。"),
            ("连接", "同一地面支撑街面、短门槛和落件。"),
        ],
        "note": "小比例搭景、真实表面和镜头仍待实拍验证。",
    },
    "b": {
        "name": "高级纸艺雕塑",
        "crop": (164, 330, 369, 200),
        "detail": "层叠台面、立起的纸片和开槽",
        "criteria": [
            ("材料", "同色纸材，用厚度与截面区分。"),
            ("光线", "左前侧光拉出切口与折边。"),
            ("连接", "一片纸板出箱，接住沿线的封箱件。"),
        ],
        "note": "折片承重、装配顺序与阴影仍待实物纸样。",
    },
}


def text(x, y, content, size, color="#242623", weight=400):
    return (f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}">'
            f'{escape(content)}</text>')


def svg(path, width, height, items, background="#f6f3ec"):
    body = "\n".join(items)
    path.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
 width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="{width}" height="{height}" fill="{background}"/>
<g font-family="PingFang SC, Heiti SC, sans-serif">
{body}
</g>
</svg>
''', encoding="utf-8")


def png_from_ppm(ppm, png):
    subprocess.run(["sips", "-s", "format", "png", str(ppm), "--out", str(png)], check=True,
                   stdout=subprocess.DEVNULL)


def gray_ppm(source, output):
    data = source.read_bytes()
    kind, dimensions, depth, rgb = data.split(b"\n", 3)
    assert kind == b"P6" and depth == b"255" and len(rgb) == WIDTH * HEIGHT * 3
    gray = bytearray(rgb)
    for i in range(0, len(rgb), 3):
        tone = (54*rgb[i]+183*rgb[i+1]+19*rgb[i+2]+128)//256
        gray[i:i+3] = bytes((tone, tone, tone))
    output.write_bytes(b"\n".join((kind, dimensions, depth, gray)))


def frame(directory, key, backdrop, anchors, monochrome=False, show_brand=True):
    (x, y), (x1, y1), (x2, y2) = anchors
    matrix = ((x1-x)/91, (y1-y)/91, (x-x2)/19, (y-y2)/19, x, y)
    transform = " ".join(f"{n:.6f}" for n in matrix)
    ink = "#202020" if monochrome else "#241b17"
    headline = "#f5f5f5" if monochrome else "#f8f5ec"
    brand = (f'<text font-size="20" font-weight="500" transform="matrix({transform})" '
             f'fill="{ink}">顺丰同城</text>')
    path = directory / f"{key}.svg"
    items = [embedded_image(backdrop, 0, 0, WIDTH, HEIGHT),
             text(49, 64, "概念文案", 17, headline),
             text(48, 127, "一座城，装进包裹", 52, headline, 600)]
    if show_brand:
        items.append(brand)
    svg(path, WIDTH, HEIGHT, items)
    return path


def detail(directory, route, scene_png, crop):
    x, y, w, h = crop
    path = directory / f"{route}-detail.svg"
    image = embedded_image(scene_png, 0, 0, WIDTH, HEIGHT)
    nested = f'<svg width="520" height="282" viewBox="{x} {y} {w} {h}">{image}</svg>'
    svg(path, 520, 282, [nested])
    return path


def board(directory, key, route):
    tone = "#64574b"
    items = [
        text(47, 52, "顺丰同城 / Gate 4.6", 18, tone, 500),
        text(46, 108, f'{key.upper()}  {route["name"]}', 43, "#252823", 600),
        embedded_image(PREVIEWS / f"style-{key}-frame.png", 48, 140, 609.6, 762),
        text(697, 152, "材料、光线与承托", 24, "#252823", 600),
        embedded_image(PREVIEWS / f"style-{key}-detail.png", 697, 171, 520, 282),
        text(697, 479, route["detail"], 16, tone),
    ]
    for i, (tag, note) in enumerate(route["criteria"]):
        y = 520+i*38
        items += [text(697, y, tag, 17, "#252823", 600), text(773, y, note, 17, tone)]
    items.append(text(697, 655, "缩略与主体层级检查", 22, "#252823", 600))
    for i, (suffix, caption) in enumerate((("thumbnail","128 × 160"), ("grayscale","灰阶"), ("silhouette","主体轮廓"))):
        x = 697+i*184
        items += [embedded_image(PREVIEWS / f"style-{key}-{suffix}.png", x, 679, 128, 160),
                  text(x, 864, caption, 17, tone)]
    items += [text(48, 936, "原创三维预演 · 4:5 临时画幅 · 品牌文字为占位", 16, tone),
              text(697, 936, route["note"], 16, tone)]
    path = directory / f"style-{key}-board.svg"
    svg(path, 1265, 970, items)
    return path


def comparison(directory, frames, hide_brand=False):
    title = "只隐藏品牌文字 · A/B 对照" if hide_brand else "同一创意，两种材质语言"
    items = [text(48, 52, "顺丰同城 / Gate 4.6", 17, "#64574b", 500),
             text(47, 104, title, 39, "#242623", 600),
             text(48, 144, "4:5 临时画幅 · 同一信息层级 · 原创三维预演", 17, "#64574b")]
    for index, (key, route) in enumerate(ROUTES.items()):
        x = 48 + index*532
        items += [text(x, 199, f'{key.upper()}  {route["name"]}', 23, "#242623", 600),
                  embedded_image(frames[key], x, 217, 480, 600)]
    footer = ("纸箱、城市、交付、标题与光线保留，单独比较品牌字样隐藏后的认读。"
              if hide_brand else "品牌字样为普通文字占位，拍摄、纸样与印刷待独立确认。")
    items.append(text(48, 861, footer, 17, "#64574b"))
    path = directory / ("no-brand-comparison.svg" if hide_brand else "comparison.svg")
    svg(path, 1110, 900, items)
    return path


def main():
    default = shutil.which("inkscape") or "/Applications/Inkscape.app/Contents/MacOS/inkscape"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inkscape", default=default)
    args = parser.parse_args()
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    outputs = {}
    with tempfile.TemporaryDirectory(prefix="sf-stage46-") as tmp:
        directory = Path(tmp)
        executable = directory / "lighting"
        flags = ["-std=c++17", "-O3", "-pthread", "-Wall", "-Wextra"]
        subprocess.run(["clang++", *flags, str(SCENE), "-o", str(executable)], check=True)
        def export(name, path, w, h):
            outputs[name] = render(args.inkscape, path, PREVIEWS / name, w, h)

        unmarked = {}
        for key, route in ROUTES.items():
            stem = directory / f"scene-{key}"
            coords = subprocess.check_output([str(executable), key, str(WIDTH), str(HEIGHT),
                                              str(SAMPLES), str(stem)], text=True)
            marks = [tuple(map(float,line.split())) for line in coords.splitlines()]
            ppm = stem.with_suffix(".ppm")
            beauty = stem.with_suffix(".png")
            png_from_ppm(ppm, beauty)
            gray = directory / f"{key}-gray.ppm"
            gray_ppm(ppm, gray)
            png_from_ppm(gray, gray.with_suffix(".png"))
            full = frame(directory, key, beauty, marks)
            mono = frame(directory, key+"-mono", gray.with_suffix(".png"), marks, monochrome=True)
            export(f"style-{key}-frame.png", full, WIDTH, HEIGHT)
            proof = frame(directory, key+"-no-brand", beauty, marks, show_brand=False)
            unmarked[key] = proof.with_suffix(".png")
            render(args.inkscape, proof, unmarked[key], WIDTH, HEIGHT)
            export(f"style-{key}-grayscale.png", mono, WIDTH, HEIGHT)
            export(f"style-{key}-thumbnail.png", full, 128, 160)
            black = directory / f"{key}-black.png"
            png_from_ppm(directory / f"scene-{key}-mask.ppm", black)
            outline = directory / f"{key}-outline.svg"
            svg(outline, WIDTH, HEIGHT, [embedded_image(black, 0, 0, WIDTH, HEIGHT)], "#ffffff")
            export(f"style-{key}-silhouette.png", outline, WIDTH, HEIGHT)
            export(f"style-{key}-detail.png", detail(directory, key, beauty, route["crop"]), 520, 282)
            export(f"style-{key}-board.png", board(directory, key, route), 1265, 970)
        full_frames = {key: PREVIEWS / f"style-{key}-frame.png" for key in ROUTES}
        export("comparison.png", comparison(directory, full_frames), 1110, 900)
        export("no-brand-comparison.png", comparison(directory, unmarked, hide_brand=True), 1110, 900)

    print(json.dumps({
        "inkscape": subprocess.check_output([args.inkscape, "--version"], text=True).strip(),
        "compiler": subprocess.check_output(["clang++", "--version"], text=True).splitlines()[0],
        "method": "Original geometry, CPU ray casting, area sampling and ambient occlusion",
        "samples_per_pixel": SAMPLES, "frame_size": [WIDTH, HEIGHT], "previews": outputs
    }, indent=2))


if __name__ == "__main__":
    main()
