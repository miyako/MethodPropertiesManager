import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import prepare_demo_screenshot_labels as labels


class ScreenshotLabelsTest(unittest.TestCase):
    def setUp(self):
        self.root = labels.config.ROOT
        self.units = labels.read_units(self.root / labels.RESOURCE, "ja")
        self.units["CommonClose"] = ("Close", "閉じる")
        self.objects = json.loads((self.root / labels.FORM).read_text())["pages"][1]["objects"]

    def test_demo_labels_align_and_identifiers_are_preserved(self):
        for number in range(6, 10):
            with self.subTest(figure=number):
                text, report = labels.prepare_figure(number, self.root, self.units, self.objects)
                original = (self.root / f"figures/fig-{number:02}.en.txt").read_text().splitlines()
                translated = text.splitlines()
                self.assertEqual(len(original), len(translated))
                self.assertEqual(translated[0], self.units["MPM_WindowTitle"][1])
                for source, target in zip(original, translated):
                    if source.startswith("Method") and source != "Method Properties Manager" and source != "Methods":
                        self.assertEqual(source, target)
                layout = json.loads((self.root / f"figures/layout/fig-{number:02}.json").read_text())
                self.assertEqual(report["replacement_enabled"], bool(layout.get("replace")))
                self.assertEqual(report["rendering_status"], "labels_only_font_geometry_not_assessed")
                image = self.root / f"figures/fig-{number:02}.png"
                self.assertEqual(report["original_sha256"], hashlib.sha256(image.read_bytes()).hexdigest())
                for item in report["labels"]:
                    if "target" in item:
                        self.assertIsNone(item["resolved_japanese_font"])
                        self.assertIsNone(item["erase_draw_masks"])

    def test_both_instruction_fragments_use_the_same_resource(self):
        _, report = labels.prepare_figure(6, self.root, self.units, self.objects)
        fragments = [item for item in report["labels"] if item.get("resname") == "MPM_EditLabel"]
        self.assertEqual([item["resource_line"] for item in fragments], [1, 2])
        self.assertEqual("\r".join(item["target"] for item in fragments), self.units["MPM_EditLabel"][1])

    def test_instruction_source_changes_are_not_silently_accepted(self):
        source, target = self.units["MPM_EditLabel"]
        self.units["MPM_EditLabel"] = (source + "changed", target)
        with self.assertRaisesRegex(ValueError, "does not match"):
            labels.prepare_figure(6, self.root, self.units, self.objects)

    def test_unknown_ocr_labels_are_not_silently_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "figures/layout").mkdir(parents=True)
            for name in ["fig-06.en.txt", "layout/fig-06.json"]:
                shutil.copy2(self.root / "figures" / name, root / "figures" / name)
            text = (root / "figures/fig-06.en.txt").read_text().replace("Any", "Unknown label", 1)
            (root / "figures/fig-06.en.txt").write_text(text)
            with self.assertRaisesRegex(ValueError, "Unresolved screenshot label"):
                labels.prepare_figure(6, root, self.units, self.objects)

    def test_unexpected_replacement_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "figures/layout").mkdir(parents=True)
            shutil.copy2(self.root / "figures/fig-06.en.txt", root / "figures/fig-06.en.txt")
            layout = json.loads((self.root / "figures/layout/fig-06.json").read_text())
            layout["replace"] = "unreviewed.png"
            (root / "figures/layout/fig-06.json").write_text(json.dumps(layout))
            with self.assertRaisesRegex(ValueError, "Unexpected screenshot replacement"):
                labels.prepare_figure(6, root, self.units, self.objects)

    def test_existing_editor_changes_are_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "labels.ja.txt"
            labels.write_new(path, "original\n")
            labels.write_new(path, "original\n")
            path.write_text("editor correction\n")
            with self.assertRaisesRegex(FileExistsError, "Refusing to overwrite"):
                labels.write_new(path, "original\n")
            self.assertEqual(path.read_text(), "editor correction\n")

    def test_native_xliff_10_with_en_us_and_no_namespace(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "CommonJA.xlf"
            path.write_text(
                '<xliff version="1.0"><file source-language="en-US" target-language="ja">'
                '<body><group resname="Buttons"><trans-unit id="23" resname="CommonClose">'
                '<source>Close</source><target>閉じる</target></trans-unit>'
                '</group></body></file></xliff>'
            )
            self.assertEqual(
                labels.read_units(path, "ja", {"CommonClose"}),
                {"CommonClose": ("Close", "閉じる")},
            )

    def test_missing_native_resource_is_an_error(self):
        with self.assertRaisesRegex(ValueError, "Missing requested resources"):
            labels.read_units(self.root / labels.RESOURCE, "ja", {"CommonClose"})


if __name__ == "__main__":
    unittest.main()
