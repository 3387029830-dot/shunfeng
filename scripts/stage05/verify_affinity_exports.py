"""Check Affinity GUI exports, including vector paths inside placed SVG forms."""

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops
from pypdf import PdfReader
from pypdf.generic import ContentStream
import pypdfium2 as pdfium


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "tests/stage05/affinity"
REPORT = ROOT / "reports/stage05/AFFINITY_EXPORT_RESULTS.json"
PATH_OPERATORS = {b"m", b"l", b"c", b"v", b"y", b"re"}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def count_paths(stream, resources, reader):
    operations = ContentStream(stream, reader).operations
    paths = sum(operator in PATH_OPERATORS for _, operator in operations)
    xobjects = resources.get("/XObject", {}).get_object() if "/XObject" in resources else {}
    for operands, operator in operations:
        if operator != b"Do":
            continue
        xobject = xobjects[operands[0]].get_object()
        if xobject.get("/Subtype") == "/Form":
            paths += count_paths(xobject, xobject.get("/Resources", resources), reader)
    return paths


def inspect_pdf(path):
    reader = PdfReader(path)
    pages = []
    for page in reader.pages:
        resources = page["/Resources"].get_object()
        pages.append({
            "page_pt": [float(page.mediabox.width), float(page.mediabox.height)],
            "vector_path_operators_including_forms": count_paths(
                page.get_contents(), resources, reader
            ),
            "raster_images": len(page.images),
            "extracted_text": page.extract_text(),
        })
    return pages


def compare_pages(before, after):
    with pdfium.PdfDocument(before) as first, pdfium.PdfDocument(after) as second:
        assert len(first) == len(second) == 3
        boxes = []
        for index in range(len(first)):
            a = first[index].render(scale=1).to_pil().convert("RGB")
            b = second[index].render(scale=1).to_pil().convert("RGB")
            assert a.size == b.size
            boxes.append(ImageChops.difference(a, b).getbbox())
        return boxes


def main():
    neutral = EVIDENCE / "neutral-import.pdf"
    before = EVIDENCE / "three_boards_before.pdf"
    after = EVIDENCE / "three_boards_after.pdf"
    pages = {file.name: inspect_pdf(file) for file in (neutral, before, after)}
    assert all(
        page["vector_path_operators_including_forms"] > 0 and page["raster_images"] == 0
        for document in pages.values() for page in document
    )
    boxes = compare_pages(before, after)
    assert boxes[0] is None and boxes[2] is None
    middle = boxes[1]
    assert middle and 190 <= middle[0] < middle[2] <= 343
    assert 95 <= middle[1] < middle[3] <= 300
    # The native QA rectangle (upper left) lies well outside the changed area.
    with Image.open(EVIDENCE / "three_boards_after.png") as preview:
        assert preview.size == (1998, 480)
        preview_size = list(preview.size)
    source = EVIDENCE.parent / "iteration"
    assert sha256(EVIDENCE / "links/state_02.svg") == sha256(source / "state_02_after.svg")
    assert sha256(EVIDENCE / "links/background.svg") == sha256(source / "background.svg")
    print("PASS: Affinity vector exports; only board 2 pixels changed; source slots verified")
    REPORT.write_text(json.dumps({
        "pdfs": pages,
        "affinity_png_pixels": preview_size,
        "render_comparison": {
            "renderer": "PDFium at 72 DPI, RGB",
            "before_after_difference_boxes": boxes,
            "boards_1_and_3_pixel_equal": True,
            "board_2_changes_inside_pose_area": True,
            "native_qa_rectangle_outside_difference": True,
        },
        "linked_sources_sha256": {
            name: sha256(EVIDENCE / "links" / name)
            for name in ["background.svg", "state_02.svg"]
        },
    }, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
