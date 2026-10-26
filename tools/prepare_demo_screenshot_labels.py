#!/usr/bin/env python3
"""Prepare resource-backed labels for figures 06-09, without repainting images."""

import argparse
import hashlib
import json
import plistlib
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

import config

DEMO = Path("demo/MethodPropertiesManager")
FORM = DEMO / "Project/Sources/Forms/method_properties_manager/form.4DForm"
RESOURCE = DEMO / "Resources/ja.lproj/methodPropertiesJA.xlf"
CONTROLS = {
    "MPM_WindowTitle": None,
    "MPM_Methods": "List Box",
    "MPM_FilterLabel": "Text1",
    "MPM_EditLabel": "Text2",
    "MPM_Apply": "apply_button",
    "MPM_Remove": "remove_button",
    "MPM_Capable": "capable_button",
    "MPM_Incapable": "incapable_button",
    "MPM_Indifferent": "indifferent_button",
    "MPM_Count": "Text3",
    "MPM_ChoiceAny": None,
    "MPM_ChoicePreemptive": "Popup Dropdown List1",
    "CommonClose": "Button2",
}


def read_units(path, language, wanted=None):
    tree = ET.parse(path)
    root = tree.getroot()
    prefix = root.tag.split("}", 1)[0] + "}" if root.tag.startswith("{") else ""
    if root.tag != prefix + "xliff":
        raise ValueError(f"Expected an XLIFF document: {path}")
    files = root.findall(prefix + "file")
    if not files or any(
        item.get("source-language", "").lower().split("-")[0] != "en"
        or item.get("target-language") != language
        for item in files
    ):
        raise ValueError(f"Unexpected resource languages: {path}")
    result = {}
    for unit in root.findall(".//" + prefix + "trans-unit"):
        key = unit.get("resname") or unit.get("id")
        if wanted is not None and key not in wanted:
            continue
        source, target = unit.find(prefix + "source"), unit.find(prefix + "target")
        if source is None or target is None:
            raise ValueError(f"Incomplete resource: {path}: {key}")
        value = ("".join(source.itertext()), "".join(target.itertext()))
        if not all(value) or key in result:
            raise ValueError(f"Empty or ambiguous resource: {path}: {key}")
        result[key] = value
    if wanted is not None and wanted != result.keys():
        raise ValueError(f"Missing requested resources: {path}: {wanted - result.keys()}")
    return result


def prepare_figure(number, root, units, objects):
    stem = f"fig-{number:02}"
    lines = (root / f"figures/{stem}.en.txt").read_text().splitlines()
    layout = json.loads((root / f"figures/layout/{stem}.json").read_text())
    if len(lines) != len(layout["items"]):
        raise ValueError(f"OCR text/layout misalignment: {stem}")
    if layout.get("localize") is not False or layout.get("replace"):
        raise ValueError(f"Expected an unchanged screenshot layout: {stem}")
    source_index = {units[key][0]: key for key in CONTROLS if key != "MPM_EditLabel"}
    edit_first = [i for i, line in enumerate(lines) if line.startswith("Edit this property")]
    edit_last = [i for i, line in enumerate(lines) if line == "to select multiple methods):"]
    if len(edit_first) != 1 or len(edit_last) != 1:
        raise ValueError(f"Unexpected instruction fragments: {stem}")
    first, last = edit_first[0], edit_last[0]
    if lines[first] + " " + lines[last] != units["MPM_EditLabel"][0]:
        raise ValueError(f"Instruction does not match the demo resource: {stem}")
    instruction = units["MPM_EditLabel"][1].splitlines()
    if len(instruction) != 2:
        raise ValueError("The reviewed Japanese instruction must have two lines")
    targets, labels = [], []
    for index, source in enumerate(lines):
        if not source or re.fullmatch(r"Method\d+", source):
            target = source
            labels.append({"line": index + 1, "source": source, "action": "preserve"})
        else:
            fragment = None
            if index in (first, last):
                key = "MPM_EditLabel"
                fragment = 0 if index == first else 1
                target = instruction[fragment]
            else:
                if source not in source_index:
                    raise ValueError(f"Unresolved screenshot label: {stem}: {source!r}")
                key = source_index[source]
                target = units[key][1]
            control = CONTROLS[key]
            if key == "MPM_ChoiceAny":
                control = (
                    "Popup Dropdown List"
                    if layout["items"][index]["box"][1] < 300
                    else "Popup Dropdown List1"
                )
            obj = objects[control] if control else None
            label = {
                "line": index + 1,
                "source": source,
                "target": target,
                "resource": "4D/CommonJA.xlf" if key == "CommonClose" else str(RESOURCE),
                "resname": key,
                "control": control or "window title",
                "ocr_box": layout["items"][index]["box"],
                "erase_draw_masks": None,
                "declared_font": (
                    {
                        "family": obj["fontFamily"],
                        "size_pt": obj["fontSize"],
                        "weight": "bold" if key == "MPM_Methods" else "regular",
                    }
                    if obj
                    else None
                ),
                "resolved_japanese_font": None,
            }
            if fragment is not None:
                label["resource_line"] = fragment + 1
            labels.append(label)
        targets.append(target)
    image_path = root / f"figures/{stem}.png"
    with Image.open(image_path) as image:
        dimensions, mode = image.size, image.mode
    return "\n".join(targets) + "\n", {
        "figure": stem,
        "original_sha256": hashlib.sha256(image_path.read_bytes()).hexdigest(),
        "dimensions_px": dimensions,
        "mode": mode,
        "source_4d_build": None,
        "source_os_version": None,
        "source_locale": "en",
        "source_theme": "dark",
        "source_display_scale": None,
        "rendering_status": "blocked_pending_font_geometry_confirmation",
        "replacement_enabled": False,
        "labels": labels,
    }


def write_new(path, text):
    if path.exists():
        if path.read_bytes() != text.encode("utf-8"):
            raise FileExistsError(f"Refusing to overwrite existing edits: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", type=Path, required=True, help="Approved full 4D app bundle")
    parser.add_argument("--output", type=Path, default=Path("build/screenshot-review/demo-labels.json"))
    parser.add_argument("--write-new", action="store_true", help="Create missing .ja.txt files only")
    args = parser.parse_args()
    root = config.ROOT
    common = args.app / "Contents/Resources/ja.lproj/CommonJA.xlf"
    units = read_units(root / RESOURCE, "ja")
    units["CommonClose"] = read_units(common, "ja", {"CommonClose"})["CommonClose"]
    with (args.app / "Contents/Info.plist").open("rb") as stream:
        app = plistlib.load(stream)
    objects = json.loads((root / FORM).read_text())["pages"][1]["objects"]
    prepared = [prepare_figure(number, root, units, objects) for number in range(6, 10)]
    report = {
        "status": "labels_prepared_images_unchanged",
        "prepare_command": [
            ".venv/bin/python",
            "tools/prepare_demo_screenshot_labels.py",
            "--app",
            str(args.app),
            * (["--write-new"] if args.write_new else []),
            "--output",
            str(args.output),
        ],
        "form": str(FORM),
        "full_4d_resource": {
            "app": str(args.app),
            "version": app["CFBundleShortVersionString"],
            "file": str(common.relative_to(args.app)),
            "sha256": hashlib.sha256(common.read_bytes()).hexdigest(),
        },
        "review_gate": (
            "Declared fonts do not prove Japanese fallback or historical native title rendering. "
            "Confirm fonts, baselines, fit and precise masks before drawing or enabling replace."
        ),
        "preserve_entirely": ["fig-03", "fig-10"],
        "native_ui_pending_matching_environment": ["fig-01", "fig-02", "fig-04", "fig-05"],
        "figures": [report for _, report in prepared],
    }
    if args.write_new:
        for number, (text, _) in enumerate(prepared, 6):
            path = root / f"figures/fig-{number:02}.ja.txt"
            if path.exists() and path.read_bytes() != text.encode("utf-8"):
                raise FileExistsError(f"Refusing to overwrite existing edits: {path}")
        for number, (text, _) in enumerate(prepared, 6):
            write_new(root / f"figures/fig-{number:02}.ja.txt", text)
    write_new(args.output, json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"Prepared labels for figures 06-09: {args.output}; no screenshot pixels changed.")


if __name__ == "__main__":
    main()
