#!/usr/bin/env python3
"""Render editor-authorised Hiragino drafts for this note's native 4D dialogs."""

import argparse
import hashlib
import io
import json
import plistlib
from collections import Counter
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import PIL
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, PngImagePlugin, features

from render_demo_screenshots import (
    FigureFitError, changed_pixels, erase_text, load_fonts, write_new_bytes,
)

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = Path("figures/localisation/native-hiragino")
CAPTURES = Path("figures/localisation/captures/captures.json")
METHOD = "Internal Components/development.4dbase/Resources/ja.lproj/MethodEditorJA.xlf"
COMMON = "ja.lproj/CommonJA.xlf"
EXECUTE = "ja.lproj/4DClientJA.xlf"
TOOLBAR = "ja.lproj/ToolBarJA.xlf"


def region(resource, name, source, box, donor, size, x, baseline, fit,
           *, align="left", weight=3, wrap=None):
    return dict(resource=resource, resname=name, source=source, erase=box, donor=donor,
                size=size, x=x, baseline=baseline, fit=fit, align=align,
                weight=weight, wrap=wrap)


REGIONS = {
    "fig-01": [
        region(METHOD, "Proc_info_windowTitle", "Method Properties",
               (315, 55, 468, 78), 590, 18, 392, 74, (130, 53, 654, 79), align="center", weight=6),
        region(METHOD, "Proc_info_Name", "Name:",
               (232, 111, 283, 130), 220, 16, 281, 126, (170, 108, 283, 132), align="right"),
        region(METHOD, "Proc_info_invisible", "Invisible",
               (316, 158, 380, 177), 650, 16, 318, 174, (316, 156, 680, 179)),
        region(METHOD, "Proc_info_sharedByComponentsAndHostDatabase",
               "Shared by components and host project",
               (316, 190, 622, 212), 650, 16, 318, 206, (316, 188, 680, 213)),
        region(METHOD, "Proc_info_executeOnServer", "Execute on Server",
               (316, 226, 456, 245), 650, 16, 318, 242, (316, 223, 680, 248)),
        region(METHOD, "preemptiveMode_comment", "Only used in compiled projects",
               (294, 271, 501, 291), 650, 14, 397, 288, (190, 268, 680, 293), align="center"),
        region(METHOD, "preemptiveMode", "Execution mode:",
               (155, 297, 283, 316), 120, 16, 281, 313, (130, 294, 283, 319), align="right"),
        region(METHOD, "br_preemptive_2", "Can be run in preemptive processes",
               (317, 297, 557, 317), 650, 16, 319, 313, (317, 294, 680, 320)),
        region(METHOD, "br_preemptive_3", "Cannot be run in preemptive processes",
               (317, 328, 579, 348), 650, 16, 319, 345, (317, 326, 680, 352)),
        region(METHOD, "br_preemptive_1", "Indifferent",
               (316, 359, 388, 379), 650, 16, 318, 376, (316, 357, 680, 383)),
        region(METHOD, "availableTrough", "Available through:",
               (145, 418, 283, 440), 120, 16, 281, 434, (128, 415, 283, 442), align="right"),
        region(METHOD, "cb_webServices", "Web Services",
               (315, 417, 421, 437), 650, 16, 317, 434, (315, 415, 680, 441)),
        region(METHOD, "Proc_info_publishedInWsdl", "Published in WSDL",
               (338, 443, 466, 462), 650, 14, 340, 460, (338, 441, 680, 465)),
        region(METHOD, "cb_4dTags", "4D tags and URLs (4DACTION...)",
               (315, 479, 568, 501), 650, 16, 317, 496, (315, 477, 680, 504)),
        region(COMMON, "CommonCancel", "Cancel",
               (509, 685, 565, 704), 503, 16, 537, 702, (493, 681, 579, 706), align="center"),
    ],
    "fig-04": [
        region(METHOD, "Proc_Info_All_windowTitle", "Attributes for methods",
               (322, 68, 557, 93), 610, 20, 440, 88, (140, 65, 740, 96), align="center", weight=6),
        region(METHOD, "Proc_info_matchingMethodName", "Matching method name:",
               (214, 136, 449, 163), 180, 20, 445, 157, (160, 131, 450, 168), align="right"),
        region(METHOD, "Proc_info_useThe@ToDesignateSeveralMethods",
               "Use the @ to designate several methods. For example, enter “Web@” to "
               "designate the methods whose name begins with “Web”, or “@” for all the methods.",
               [(141, 179, 739, 201), (136, 200, 743, 222), (399, 221, 475, 240)],
               760, 18, 440, 198, (135, 175, 745, 244), align="center",
               wrap=dict(width=602, lines=3, spacing=20)),
        region(METHOD, "Proc_info_attributeToModify", "Attribute to Modify",
               (136, 277, 282, 300), 700, 18, 139, 297, (136, 273, 744, 303)),
        region(METHOD, "Proc_info_invisible", "Invisible",
               (161, 327, 241, 351), 400, 22, 164, 348, (159, 323, 629, 354)),
        region(METHOD, "Proc_info_value", "Value:",
               (228, 377, 289, 400), 200, 20, 286, 398, (160, 374, 289, 404), align="right"),
        region(COMMON, "CommonApply", "Apply",
               (420, 470, 472, 489), 398, 20, 446, 486, (391, 468, 502, 491), align="center"),
        region(COMMON, "CommonDone", "Done",
               (659, 546, 713, 570), 630, 20, 686, 566, (625, 540, 746, 574), align="center"),
    ],
    "fig-05": [
        region(TOOLBAR, "TB_Execute", "Execute",
               (43, 80, 129, 104), 30, 22, 86, 101, (20, 77, 131, 108), align="center"),
        region(EXECUTE, "common_STR#1029:1", "Execute Method",
               (301, 131, 511, 161), 650, 26, 407, 157, (165, 128, 649, 166), align="center", weight=6),
        region(EXECUTE, "common_STR#1029:3", "New Process",
               (73, 591, 212, 616), 600, 22, 76, 612, (73, 586, 700, 622)),
        region(EXECUTE, "common_STR#1029:4", "To be executed: ",
               (170, 638, 364, 667), 130, 24, 360, 662, (130, 630, 365, 674), align="right"),
        region(EXECUTE, "common_STR#1029:7", "Locally",
               (386, 638, 476, 668), 550, 24, 390, 662, (383, 632, 664, 673)),
        region(COMMON, "CommonCancel", "Cancel",
               (177, 741, 266, 769), 163, 26, 223, 764, (157, 737, 291, 777), align="center"),
        region(EXECUTE, "common_STR#1029:6", "Debug",
               (357, 741, 439, 773), 337, 26, 399, 764, (333, 737, 467, 777), align="center"),
        region(EXECUTE, "common_STR#1029:5", "Execute",
               (531, 741, 644, 771), 518, 26, 583, 764, (511, 737, 655, 777), align="center"),
    ],
}


def resource_units(path):
    tree = ET.parse(path)
    result = []

    def walk(element, context, languages):
        tag = element.tag.split("}")[-1]
        if tag == "file":
            languages = {key: element.get(key) for key in ("source-language", "target-language")}
        if tag == "group":
            context = [*context, dict(element.attrib)]
        if tag == "trans-unit":
            parts = {child.tag.split("}")[-1]: "".join(child.itertext()) for child in element}
            result.append(dict(attributes=dict(element.attrib), context=context,
                               languages=languages, **parts))
        for child in element:
            walk(child, context, languages)

    walk(tree.getroot(), [], {})
    return result


def resolve(app, specification):
    path = app / "Contents/Resources" / specification["resource"]
    matches = [unit for unit in resource_units(path)
               if unit["attributes"].get("resname") == specification["resname"]]
    if len(matches) != 1:
        raise ValueError(f"Ambiguous/missing resource: {path}: {specification['resname']}")
    unit = matches[0]
    if unit["languages"] != {"source-language": "en-US", "target-language": "ja"}:
        raise ValueError(f"Unexpected resource languages: {path}")
    if unit.get("source") != specification["source"] or not unit.get("target", "").strip():
        raise ValueError(f"Empty target or source/context mismatch: {specification['resname']}")
    return dict(file=specification["resource"], sha256=hashlib.sha256(path.read_bytes()).hexdigest(), **unit)


def wrap_label(text, font, width, limit):
    lines, line = [], ""
    for character in text:
        if font.getlength(line + character) > width:
            if not line:
                raise FigureFitError("A glyph exceeds the fixed paragraph width")
            lines.append(line)
            line = ""
        line += character
    if line:
        lines.append(line)
    if len(lines) > limit:
        raise FigureFitError(f"Full resource needs {len(lines)} lines; only {limit} fit")
    return lines


def validate_labels(app):
    for stem, regions in REGIONS.items():
        source = (ROOT / f"figures/{stem}.en.txt").read_text().splitlines()
        target = (ROOT / f"figures/{stem}.ja.txt").read_text().splitlines()
        expected = source.copy()
        for specification in regions:
            unit = resolve(app, specification)
            if specification["resname"] in ("common_STR#1029:5", "common_STR#1029:7"):
                continue  # These visible controls were absent from the original OCR lines.
            if specification["wrap"]:
                expected[2:5] = target[2:5]
                if "".join(target[2:5]) != unit["target"]:
                    raise ValueError(f"Edited explanatory text in {stem}.ja.txt")
            else:
                key = specification["source"].rstrip()
                if specification["resname"] == "Proc_info_matchingMethodName":
                    key += " @"
                if source.count(key) != 1:
                    raise ValueError(f"Ambiguous OCR line: {stem}: {key}")
                translated = unit["target"].rstrip()
                if key.endswith(" @"):
                    translated += " @"
                expected[source.index(key)] = translated
        if expected != target:
            raise ValueError(f"Edited or misaligned labels in {stem}.ja.txt; not overwriting them")


def restore_toolbar(original, canvas, box):
    # The toolbar has dithered row gradients; copy an adjacent untouched strip,
    # only under the source glyphs and their one-pixel antialiasing halo.
    background = original.crop((200, box[1], 200 + box[2] - box[0], box[3]))
    old = original.crop(box)
    delta = changed_pixels(old, background)
    difference = ImageChops.difference(old, background)
    core = ImageChops.lighter(ImageChops.lighter(*difference.split()[:2]), difference.split()[2])
    core = core.point(lambda value: 255 if value > 6 else 0)
    if core.getbbox() is None:
        raise ValueError("No toolbar text found")
    halo = core.filter(ImageFilter.MaxFilter(3))
    mask = ImageChops.multiply(halo, delta)
    restored = old.copy()
    restored.paste(background, (0, 0), mask)
    remaining = ImageChops.difference(restored, background)
    if any(max(channel.getextrema()) > 6 for channel in remaining.split()):
        raise ValueError("Toolbar source glyph core was not restored")
    canvas.paste(restored, box)
    full_mask = Image.new("L", original.size)
    full_mask.paste(mask, box)
    return full_mask


def render(stem, app, paths):
    path = ROOT / f"figures/{stem}.png"
    with Image.open(path) as source:
        original = source.copy()
        metadata = dict(source.info)
    canvas = original.copy()
    erasure = Image.new("L", original.size)
    drawing = Image.new("L", original.size)
    records = []
    for specification in REGIONS[stem]:
        unit = resolve(app, specification)
        font = ImageFont.truetype(str(paths[specification["weight"]]), specification["size"],
                                  layout_engine=ImageFont.Layout.BASIC)
        lines = [unit["target"]]
        if specification["wrap"]:
            wrap = specification["wrap"]
            lines = wrap_label(unit["target"], font, wrap["width"], wrap["lines"])
        boxes = specification["erase"]
        if isinstance(boxes[0], int):
            boxes = [boxes]
        pixels = original.load()
        old_pixels = [pixels[x, y] for box in boxes
                      for y in range(box[1], box[3]) for x in range(box[0], box[2])]
        peak = max(map(sum, old_pixels))
        foreground = Counter(pixel for pixel in old_pixels if sum(pixel) == peak).most_common(1)[0][0]
        glyphs = Image.new("L", original.size)
        draw = ImageDraw.Draw(glyphs)
        positions = []
        for index, line in enumerate(lines):
            advance = font.getlength(line)
            x = specification["x"]
            if specification["align"] == "center":
                x -= advance / 2
            elif specification["align"] == "right":
                x -= advance
            baseline = specification["baseline"] + index * (specification["wrap"] or {}).get("spacing", 0)
            draw.text((round(x), baseline), line, font=font, fill=255, anchor="ls")
            positions.append([round(x), baseline])
        fit = specification["fit"]
        bounds = glyphs.getbbox()
        if not bounds or any((bounds[0] < fit[0], bounds[1] < fit[1],
                              bounds[2] > fit[2], bounds[3] > fit[3])):
            raise FigureFitError(f"{stem}: {specification['resname']} does not fit {fit}: {bounds}")
        local_erasure = Image.new("L", original.size)
        locked = Image.new("L", original.size)
        for box in boxes:
            if specification["resname"] == "TB_Execute":
                mask = restore_toolbar(original, canvas, box)
            else:
                mask, _, _ = erase_text(
                    original, canvas, box, specification["donor"], locked, foreground=foreground,
                    native_antialiasing=True,
                )
            local_erasure = ImageChops.lighter(local_erasure, mask)
        for y in range(bounds[1], bounds[3]):
            for x in range(bounds[0], bounds[2]):
                if glyphs.getpixel((x, y)) and not local_erasure.getpixel((x, y)):
                    expected = original.getpixel((specification["donor"], y))
                    pixel = original.getpixel((x, y))
                    tolerance = 3 if specification["resname"] == "TB_Execute" else 0
                    if max(abs(a - b) for a, b in zip(pixel, expected)) > tolerance:
                        raise FigureFitError(f"{stem}: target covers a nontext feature at {(x, y)}")
        canvas.paste(foreground, (0, 0, *canvas.size), glyphs)
        erasure = ImageChops.lighter(erasure, local_erasure)
        drawing = ImageChops.lighter(drawing, glyphs)
        records.append(dict(
            resource=unit, source_erase_boxes=boxes, donor_x=specification["donor"],
            font=f"HiraginoSans-W{specification['weight']}", size_px=specification["size"],
            positions=positions, rendered_lines=lines, foreground=foreground,
            draw_bounds=bounds, fit=fit,
            restoration=(
                dict(method="adjacent dithered row-gradient strip under glyphs and one-pixel halo",
                     donor_strip=[200, boxes[0][1], 200 + boxes[0][2] - boxes[0][0], boxes[0][3]],
                     residual_background_noise_max=6, visual_review_required=True)
                if specification["resname"] == "TB_Execute"
                else dict(method="row donors under glyphs including native antialiasing/shadows",
                          source_glyph_residual_pixels=0)
            ),
        ))
    changed = changed_pixels(original, canvas)
    allowed = ImageChops.lighter(erasure, drawing).point(lambda value: 255 if value else 0)
    if ImageChops.multiply(changed, ImageChops.invert(allowed)).getbbox():
        raise ValueError(f"Unexpected nontext changes in {stem}")
    report = dict(
        figure=stem, status="editor_approved_approximation",
        original_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        dimensions_px=list(original.size), mode=original.mode,
        changed_pixels=changed.histogram()[255], unexpected_changes=0,
        metadata=dict(dpi=metadata.get("dpi"),
                      icc_profile_sha256=hashlib.sha256(metadata["icc_profile"]).hexdigest()
                      if metadata.get("icc_profile") else None),
        labels=records,
    )
    return canvas, erasure, drawing, metadata, report


def encode(image, metadata=None):
    stream = io.BytesIO()
    image.save(stream, format="PNG", compress_level=9, **(metadata or {}))
    return stream.getvalue()


def native_captures():
    records = json.loads((ROOT / CAPTURES).read_text())["captures"]
    for record in records:
        stem = record["figure"]
        for name, path in [("capture", record["capture"]), ("output", record["output"]),
                           ("original", f"figures/{stem}.png")]:
            data = (ROOT / path).read_bytes()
            if hashlib.sha256(data).hexdigest() != record[f"{name}_sha256"]:
                raise ValueError(f"Edited native capture artifact: {path}")
            with Image.open(ROOT / path) as image:
                if list(image.size) != record[f"{name}_dimensions_px"]:
                    raise ValueError(f"Unexpected capture dimensions: {path}")
        layout = json.loads((ROOT / f"figures/layout/{stem}.json").read_text())
        if (layout.get("replace") != Path(record["output"]).name or layout["localize"]
                or layout["width_pt"] != record["width_pt"]):
            raise ValueError(f"Native capture layout differs from the reviewed placement: {stem}")
        data = (ROOT / record["capture"]).read_bytes()
        if record["crop"]:
            with Image.open(ROOT / record["capture"]) as source:
                cropped = source.crop(record["crop"])
                metadata = PngImagePlugin.PngInfo()
                metadata.add(b"sRGB", bytes([source.info["srgb"]]))
                data = encode(cropped, dict(pnginfo=metadata, dpi=source.info["dpi"]))
        if data != (ROOT / record["output"]).read_bytes():
            raise ValueError(f"Native capture/crop does not replay exactly: {stem}")
    return records


def blocked_explorer(app, paths):
    specifications = [
        dict(resource="ja.lproj/ExplorerMenusJA.xlf",
             resname=None, source="Edit Documentation...", group="ContextualMenuExplorerMethods",
             unit_id="122", size=22, available_width=232),
        dict(resource="ja.lproj/ExplorerJA.xlf",
             resname="Exp_Comments", source="Documentation", size=18, available_width=150),
    ]
    labels = []
    for specification in specifications:
        path = app / "Contents/Resources" / specification["resource"]
        units = resource_units(path)
        if specification["resname"]:
            unit = resolve(app, specification)
        else:
            matches = [unit for unit in units if unit["attributes"].get("id") == specification["unit_id"]
                       and any(group.get("resname") == specification["group"] for group in unit["context"])]
            if len(matches) != 1 or matches[0].get("source") != specification["source"]:
                raise ValueError("Could not disambiguate Explorer's documentation menu command")
            unit = dict(file=specification["resource"],
                        sha256=hashlib.sha256(path.read_bytes()).hexdigest(), **matches[0])
        font = ImageFont.truetype(str(paths[3]), specification["size"], layout_engine=ImageFont.Layout.BASIC)
        width = font.getlength(unit["target"])
        if width <= specification["available_width"]:
            raise ValueError("Explorer blocker is stale; re-examine its geometry")
        labels.append(dict(resource=unit, size_px=specification["size"],
                           full_label_width_px=width, available_width_px=specification["available_width"]))
    path = ROOT / "figures/fig-02.png"
    return dict(figure="fig-02", original_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                reason="Complete official labels exceed the original English menu/tab widths. "
                       "Mechanical resizing or label shortening is not performed.",
                labels=labels, mechanical_replacement_enabled=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", type=Path, default=Path("/Applications/4D 20.8/4D.app"))
    parser.add_argument("--write-new", action="store_true")
    args = parser.parse_args()
    with (args.app / "Contents/Info.plist").open("rb") as stream:
        version = plistlib.load(stream)["CFBundleShortVersionString"]
    if not version.startswith("20.8"):
        raise ValueError(f"The editor authorised 4D 20.8, not {version}")
    validate_labels(args.app)
    text = "".join(resolve(args.app, specification)["target"]
                   for regions in REGIONS.values() for specification in regions)
    text += "ドキュメンテーションを編集..."
    paths, fonts = load_fonts(text)
    captures = native_captures()
    diagnostic = blocked_explorer(args.app, paths)
    payloads, reports, blocked = {}, [], []
    if not any(record["figure"] == "fig-02" for record in captures):
        blocked.append(diagnostic)
    for stem in REGIONS:
        try:
            image, erase, draw, metadata, report = render(stem, args.app, paths)
        except FigureFitError as error:
            blocked.append(dict(figure=stem, reason=str(error), replacement_enabled=False))
            print(f"BLOCKED: {error}", file=sys.stderr)
            continue
        output = Path(f"figures/{stem}-ja.png")
        payloads[output] = encode(image, metadata)
        report["output"] = str(output)
        report["output_sha256"] = hashlib.sha256(payloads[output]).hexdigest()
        report["masks"] = {}
        for kind, mask in [("erase", erase), ("draw", draw)]:
            path = ARTIFACTS / f"{stem}-{kind}.png"
            payloads[path] = encode(mask)
            report["masks"][kind] = str(path)
        reports.append(report)
    report = dict(
        app=str(args.app), app_version=version,
        editorial_approval="Editor accepted figures 01/04/05: images are good (2026-10-26)",
        historical_native_rendering="not claimed; original application build, OS and scale unknown",
        typography="Fixed source-scale Hiragino Sans W3/W6 trials; no fitting by shrinking or abbreviation. "
                   "Japanese explanatory text uses upright W3, not synthetic Latin italics.",
        shaping="Pillow FreeType BASIC; horizontal Japanese/Latin, no combining marks; CoreText glyph coverage",
        pillow_version=PIL.__version__, freetype_version=features.version_module("freetype2"),
        fonts=fonts, figures=reports, mechanical_fit_diagnostic=[diagnostic],
        reviewed_native_captures=str(CAPTURES), blocked=blocked,
        replay_command=[".venv/bin/python", "tools/render_native_screenshots.py", "--write-new"],
    )
    payloads[ARTIFACTS / "render.json"] = (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode()
    for path, data in payloads.items():
        output = ROOT / "build/native-hiragino-review" / path
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(data)
    if args.write_new:
        for path, data in payloads.items():
            if (ROOT / path).exists() and (ROOT / path).read_bytes() != data:
                raise FileExistsError(f"Refusing to overwrite existing edits: {path}")
        for path, data in payloads.items():
            write_new_bytes(ROOT / path, data)
    print(f"Rendered {len(reports)} native drafts; {len(blocked)} blocked. PDF configuration unchanged.")
    return 2 if blocked else 0


if __name__ == "__main__":
    sys.exit(main())
