#!/usr/bin/env python3
"""Make Hiragino Sans review drafts for demo screenshots, without enabling them."""

import argparse
import ctypes as C
import hashlib
import io
import json
import sys
import unicodedata
from collections import Counter
from pathlib import Path

import PIL
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, features

import config
from prepare_demo_screenshot_labels import RESOURCE, read_units

ROOT = config.ROOT
PREPARED = ROOT / "figures/localisation/demo-labels.json"
ARTIFACTS = Path("figures/localisation/hiragino")

# Rectangles are source-image pixels; none include a control border or example value.
REGIONS = {
    "MPM_WindowTitle": ((694, 88, 1060, 121), 1200, 26, 6, 877, 115, "center", (260, 82, 1500, 126)),
    "MPM_Methods": ((158, 181, 262, 209), 550, 24, 6, 160, 205, "left", (157, 179, 579, 211)),
    "MPM_FilterLabel": ((632, 178, 1019, 211), 1625, 26, 3, 632, 204, "left", (630, 176, 1605, 212)),
    "MPM_EditLabel:1": ((632, 341, 1535, 371), 1625, 26, 3, 632, 365, "left", (632, 338, 1605, 371)),
    "MPM_EditLabel:2": ((632, 372, 952, 403), 1625, 26, 3, 632, 395, "left", (632, 369, 1605, 405)),
    "MPM_Apply": ((1084, 419, 1159, 451), 1054, 26, 3, 1122, 444, "center", (1049, 416, 1196, 452)),
    "MPM_Remove": ((1270, 419, 1374, 451), 1254, 26, 3, 1322, 444, "center", (1249, 416, 1396, 452)),
    "MPM_Capable": ((1068, 418, 1174, 451), 1054, 26, 3, 1122, 444, "center", (1049, 416, 1196, 452)),
    "MPM_Incapable": ((1262, 418, 1382, 451), 1254, 26, 3, 1322, 444, "center", (1249, 416, 1396, 452)),
    "MPM_Indifferent": ((1461, 416, 1586, 448), 1454, 26, 3, 1522, 444, "center", (1449, 414, 1596, 452)),
    "MPM_Count": ((344, 837, 455, 874), 600, 36, 3, 156, 869, "left", (155, 833, 463, 879)),
    "CommonClose": ((1484, 842, 1561, 873), 1454, 26, 3, 1522, 867, "center", (1449, 840, 1596, 876)),
    "read_any": ((638, 222, 696, 254), 800, 26, 3, 641, 247, "left", (638, 220, 942, 257)),
    "write_any": ((638, 419, 696, 451), 800, 26, 3, 641, 444, "left", (638, 415, 942, 453)),
    "MPM_ChoicePreemptive": ((638, 418, 780, 452), 800, 26, 3, 641, 444, "left", (638, 415, 942, 453)),
}


class FigureFitError(ValueError):
    def __init__(self, message, details=None):
        super().__init__(message)
        self.details = details or {}


def bind(library, name, result, *arguments):
    function = getattr(library, name)
    function.restype, function.argtypes = result, list(arguments)
    return function


def verify_native_font(path, weight, text):
    if sys.platform != "darwin":
        raise RuntimeError("Hiragino Sans verification requires the local macOS CoreText installation")
    cf = C.CDLL("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation")
    ct = C.CDLL("/System/Library/Frameworks/CoreText.framework/CoreText")
    create = bind(cf, "CFStringCreateWithCString", C.c_void_p, C.c_void_p, C.c_char_p, C.c_uint32)
    length = bind(cf, "CFStringGetLength", C.c_long, C.c_void_p)
    copy_utf8 = bind(cf, "CFStringGetCString", C.c_bool, C.c_void_p, C.c_char_p, C.c_long, C.c_uint32)
    release = bind(cf, "CFRelease", None, C.c_void_p)
    make_font = bind(ct, "CTFontCreateWithName", C.c_void_p, C.c_void_p, C.c_double, C.c_void_p)
    copy_name = bind(ct, "CTFontCopyPostScriptName", C.c_void_p, C.c_void_p)
    copy_attribute = bind(ct, "CTFontCopyAttribute", C.c_void_p, C.c_void_p, C.c_void_p)
    copy_path = bind(cf, "CFURLCopyFileSystemPath", C.c_void_p, C.c_void_p, C.c_long)
    get_glyphs = bind(
        ct, "CTFontGetGlyphsForCharacters", C.c_bool,
        C.c_void_p, C.POINTER(C.c_uint16), C.POINTER(C.c_uint16), C.c_long,
    )

    def string(reference):
        buffer = C.create_string_buffer(4 * length(reference) + 1)
        if not copy_utf8(reference, buffer, len(buffer), 0x08000100):
            raise RuntimeError("Could not decode CoreText font metadata")
        return buffer.value.decode("utf-8")

    expected = f"HiraginoSans-W{weight}"
    name = create(None, expected.encode(), 0x08000100)
    font = make_font(name, 26, None)
    references = [name, font]
    try:
        postscript = copy_name(font)
        references.append(postscript)
        if string(postscript) != expected:
            raise ValueError(f"CoreText substituted a different face for {expected}")
        url = copy_attribute(font, C.c_void_p.in_dll(ct, "kCTFontURLAttribute"))
        references.append(url)
        actual_path = copy_path(url, 0)
        references.append(actual_path)
        if not Path(string(actual_path)).samefile(path):
            raise ValueError(f"CoreText and Pillow resolved different files for {expected}")
        characters = "".join(sorted(set(text) - {"\r", "\n"}))
        if any(ord(character) > 0xFFFF for character in characters):
            raise ValueError("This BMP glyph check does not support non-BMP labels")
        codes = (C.c_uint16 * len(characters))(*map(ord, characters))
        glyphs = (C.c_uint16 * len(characters))()
        covered = get_glyphs(font, codes, glyphs, len(characters))
        missing = [character for character, glyph in zip(characters, glyphs) if not glyph]
        if not covered or missing:
            raise ValueError(f"{expected} lacks glyphs: {missing!r}")
        return {
            "postscript_name": expected,
            "file": str(path),
            "file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "face_index": 0,
            "glyph_coverage": "CoreText glyph IDs checked without fallback",
            "characters_checked": characters,
        }
    finally:
        for reference in reversed(references):
            if reference:
                release(reference)


def load_fonts(text):
    if any(unicodedata.combining(character) for character in text):
        raise ValueError("Combining-mark labels require shaping beyond this BASIC-layout trial")
    paths, evidence = {}, {}
    for weight in (3, 6):
        matches = [
            path for path in Path("/System/Library/Fonts").glob(f"*W{weight}.ttc")
            if ImageFont.truetype(str(path), 26).getname() == ("Hiragino Sans", f"W{weight}")
        ]
        if len(matches) != 1:
            raise ValueError(f"Expected one installed Hiragino Sans W{weight} file, found {matches}")
        paths[weight] = matches[0]
        evidence[str(weight)] = verify_native_font(matches[0], weight, text)
    return paths, evidence


def protected_pixels(image):
    red, green, blue = image.split()
    high = ImageChops.lighter(ImageChops.lighter(red, green), blue)
    low = ImageChops.darker(ImageChops.darker(red, green), blue)
    protected = ImageChops.subtract(high, low).point(lambda value: 255 if value > 35 else 0)
    protected = protected.filter(ImageFilter.MaxFilter(5))
    borders = Image.new("L", image.size)
    border_draw = ImageDraw.Draw(borders)
    for box in [(632, 218, 988, 262), (632, 414, 988, 455),
                (1044, 414, 1200, 455), (1244, 414, 1400, 455),
                (1444, 412, 1600, 455), (1444, 838, 1600, 881)]:
        border_draw.rectangle(box, outline=255, width=3)
    protected = ImageChops.lighter(protected, borders)
    draw = ImageDraw.Draw(protected)
    for box in [(154, 212, 583, 808), (472, 831, 584, 882),
                (154, 210, 583, 214), (948, 214, 987, 264), (948, 410, 987, 460)]:
        draw.rectangle(box, fill=255)
    return protected


def erase_text(original, canvas, box, donor, protected):
    pixels, output, locked = original.load(), canvas.load(), protected.load()
    rows, candidates = {}, []
    for y in range(box[1], box[3]):
        samples = [pixels[x, y] for x in range(donor, donor + 5)]
        if len(set(samples)) != 1:
            raise ValueError(f"Nonuniform background donor at ({donor}, {y})")
        background = samples[0]
        rows[y] = background
        for x in range(box[0], box[2]):
            pixel = pixels[x, y]
            delta = [a - b for a, b in zip(pixel, background)]
            if min(delta) > 20 and max(delta) - min(delta) <= 8 and not locked[x, y]:
                candidates.append(pixel)
    if not candidates:
        raise ValueError(f"No text foreground found inside {box}")
    peak = max(sum(pixel) for pixel in candidates)
    foreground = Counter(pixel for pixel in candidates if sum(pixel) >= peak - 6).most_common(1)[0][0]
    mask = Image.new("L", original.size)
    selected = mask.load()
    for y, background in rows.items():
        direction = [a - b for a, b in zip(foreground, background)]
        norm = sum(value * value for value in direction)
        for x in range(box[0], box[2]):
            if locked[x, y]:
                continue
            delta = [a - b for a, b in zip(pixels[x, y], background)]
            alpha = sum(a * b for a, b in zip(delta, direction)) / norm
            residual = max(abs(a - alpha * b) for a, b in zip(delta, direction))
            if any(delta) and 0 < alpha <= 1.02 and residual <= 1.05:
                selected[x, y] = 255
                output[x, y] = background
    if mask.getbbox() is None:
        raise ValueError(f"No source glyph pixels selected inside {box}")
    for y, background in rows.items():
        for x in range(box[0], box[2]):
            if not locked[x, y] and output[x, y] != background:
                raise ValueError(f"Unrestored source glyph or nontext feature at ({x}, {y})")
    return mask, foreground, list(dict.fromkeys(rows.values()))


def region_for(label):
    key = label["resname"]
    if key == "MPM_EditLabel":
        key += ":" + str(label["resource_line"])
    if key == "MPM_ChoiceAny":
        key = "read_any" if label["control"] == "Popup Dropdown List" else "write_any"
    return REGIONS[key]


def changed_pixels(original, candidate):
    channels = ImageChops.difference(original, candidate).split()
    return ImageChops.lighter(ImageChops.lighter(*channels[:2]), channels[2]).point(
        lambda value: 255 if value else 0
    )


def render_figure(prepared, paths):
    stem = prepared["figure"]
    source = ROOT / f"figures/{stem}.png"
    if hashlib.sha256(source.read_bytes()).hexdigest() != prepared["original_sha256"]:
        raise ValueError(f"Original screenshot changed: {source}")
    with Image.open(source) as image:
        if image.mode != "RGB" or image.info:
            raise ValueError(f"Unexpected source mode/profile requiring explicit handling: {source}")
        original = image.copy()
    canvas = original.copy()
    protected = protected_pixels(original)
    erase_mask, draw_mask = (Image.new("L", original.size) for _ in range(2))
    records, fonts = [], {}
    for label in prepared["labels"]:
        if label.get("action") == "preserve":
            continue
        box, donor, size, weight, x, baseline, alignment, limits = region_for(label)
        if (weight, size) not in fonts:
            fonts[weight, size] = ImageFont.truetype(
                str(paths[weight]), size, layout_engine=ImageFont.Layout.BASIC
            )
        font = fonts[weight, size]
        text = label["target"]
        if alignment == "center":
            left, _, right, _ = font.getbbox(text, anchor="ls")
            x = round(x - (left + right) / 2)
        target = Image.new("L", original.size)
        ImageDraw.Draw(target).text((x, baseline), text, font=font, fill=255, anchor="ls")
        bounds = target.getbbox()
        if bounds is None or not (
            limits[0] <= bounds[0] and limits[1] <= bounds[1]
            and bounds[2] <= limits[2] and bounds[3] <= limits[3]
        ):
            raise FigureFitError(f"{stem}: {label['resname']} does not fit its verified region")
        collision = ImageChops.multiply(target, protected).getbbox()
        if collision:
            raise FigureFitError(
                f"{stem}: {label['resname']} at {size}px crosses a protected annotation/control",
                {"resname": label["resname"], "size_px": size,
                 "text_advance_px": font.getlength(text), "draw_bounds": bounds,
                 "collision_bounds": collision},
            )
        selected, foreground, backgrounds = erase_text(original, canvas, box, donor, protected)
        erase_mask = ImageChops.lighter(erase_mask, selected)
        canvas.paste(foreground, (0, 0, *canvas.size), target)
        draw_mask = ImageChops.lighter(draw_mask, target)
        records.append({
            "resname": label["resname"], "resource_line": label.get("resource_line"),
            "source": label["source"], "target": text, "source_erase_region": box,
            "background_donor_columns": [donor, donor + 5], "background_colors": backgrounds,
            "foreground": foreground, "face": f"HiraginoSans-W{weight}",
            "size_px": size, "baseline_px": baseline, "draw_origin": [x, baseline],
            "draw_bounds": bounds, "alignment": alignment,
            "source_glyph_residual_pixels": 0,
        })
    changed = changed_pixels(original, canvas)
    allowed = ImageChops.lighter(erase_mask, draw_mask).point(lambda value: 255 if value else 0)
    if ImageChops.multiply(changed, ImageChops.invert(allowed)).getbbox():
        raise ValueError(f"Unexpected changes outside erasure/draw masks: {stem}")
    if ImageChops.multiply(changed, protected).getbbox():
        raise ValueError(f"Example values, annotations or controls changed: {stem}")
    return canvas, erase_mask, draw_mask, {
        "figure": stem, "status": "editor_requested_font_trial_requires_visual_review",
        "original_sha256": prepared["original_sha256"], "dimensions_px": original.size,
        "changed_pixels": changed.histogram()[255], "unexpected_changes": 0,
        "replacement_enabled": False, "labels": records,
    }


def encode_png(image):
    stream = io.BytesIO()
    image.save(stream, format="PNG", compress_level=9)
    return stream.getvalue()


def write_new_bytes(path, data):
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(f"Refusing to overwrite existing edits: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-new", action="store_true", help="Also create missing figure artifacts")
    args = parser.parse_args()
    prepared = json.loads(PREPARED.read_text())
    units = read_units(ROOT / RESOURCE, "ja")
    common = prepared["full_4d_resource"]
    native = Path(common["app"]) / common["file"]
    if hashlib.sha256(native.read_bytes()).hexdigest() != common["sha256"]:
        raise ValueError("The approved native 4D resource changed; refresh its provenance first")
    units["CommonClose"] = read_units(native, "ja", {"CommonClose"})["CommonClose"]
    for figure in prepared["figures"]:
        targets = (ROOT / f"figures/{figure['figure']}.ja.txt").read_text().splitlines()
        for label in figure["labels"]:
            if "target" in label:
                target = units[label["resname"]][1]
                if "resource_line" in label:
                    target = target.splitlines()[label["resource_line"] - 1]
                if target != label["target"] or target != targets[label["line"] - 1]:
                    raise ValueError(f"Edited or stale target label: {figure['figure']}: {label['resname']}")
    text = "".join(label["target"] for figure in prepared["figures"]
                   for label in figure["labels"] if "target" in label)
    paths, font_evidence = load_fonts(text)
    payloads, completed, blocked = {}, [], []
    for figure in prepared["figures"]:
        try:
            image, erase, draw, report = render_figure(figure, paths)
        except FigureFitError as error:
            blocked.append({"figure": figure["figure"], "reason": str(error), **error.details})
            print(f"BLOCKED: {error}", file=sys.stderr)
            continue
        stem = figure["figure"]
        output = Path(f"figures/{stem}-ja.png")
        payloads[output] = encode_png(image)
        report["output"] = str(output)
        report["output_sha256"] = hashlib.sha256(payloads[output]).hexdigest()
        report["masks"] = {}
        for kind, mask in [("erase", erase), ("draw", draw)]:
            path = ARTIFACTS / f"{stem}-{kind}.png"
            payloads[path] = encode_png(mask)
            report["masks"][kind] = str(path)
        completed.append(report)
    report = {
        "status": "hiragino_sans_trial_not_enabled_in_pdf",
        "editor_font_direction": "try Hiragino Sans",
        "historical_native_rendering": "not claimed; source OS/build remains unknown",
        "pixel_scale": "trial sizes use declared 4D point sizes times two",
        "count_label_position": "uses the approved Japanese form's wider, left-shifted label",
        "instruction_geometry": "approved two-line XLIFF; 30px line spacing retained from the source",
        "shaping": "Pillow FreeType BASIC; horizontal Japanese/Latin; all glyphs verified without fallback",
        "pillow_version": PIL.__version__, "freetype_version": features.version_module("freetype2"),
        "fonts": font_evidence,
        "replay_command": [".venv/bin/python", "tools/render_demo_screenshots.py", "--write-new"],
        "figures": completed, "blocked": blocked,
    }
    payloads[ARTIFACTS / "render.json"] = (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode()
    draft = ROOT / "build/hiragino-review"
    for path, data in payloads.items():
        target = draft / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    if args.write_new:
        for path, data in payloads.items():
            target = ROOT / path
            if target.exists() and target.read_bytes() != data:
                raise FileExistsError(f"Refusing to overwrite existing edits: {target}")
        for path, data in payloads.items():
            write_new_bytes(ROOT / path, data)
    print(f"Rendered {len(completed)} Hiragino Sans drafts; {len(blocked)} blocked. PDF replacements unchanged.")
    return 2 if blocked else 0


if __name__ == "__main__":
    sys.exit(main())
