import json
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from PIL import Image, ImageChops

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import render_native_screenshots as native
import render_demo_screenshots as shared


class NativeErasureTest(unittest.TestCase):
    def test_native_coloured_antialiasing_and_dark_shadow_restore_only_glyphs(self):
        image = Image.new("RGB", (32, 16), (20, 121, 225))
        image.putpixel((2, 2), (117, 171, 236))
        image.putpixel((3, 2), (18, 118, 221))
        candidate = image.copy()
        mask, _, _ = shared.erase_text(
            image, candidate, (0, 0, 8, 8), 20, Image.new("L", image.size),
            foreground=(255, 255, 255), native_antialiasing=True,
        )
        self.assertEqual(candidate.getpixel((2, 2)), (20, 121, 225))
        self.assertEqual(candidate.getpixel((3, 2)), (20, 121, 225))
        self.assertEqual(mask.histogram()[255], 2)

    def test_unrelated_colour_is_rejected_instead_of_erased(self):
        image = Image.new("RGB", (32, 16), (42, 40, 38))
        image.putpixel((2, 2), (255, 20, 0))
        image.putpixel((3, 3), (220, 220, 220))
        with self.assertRaisesRegex(ValueError, "nontext feature"):
            shared.erase_text(image, image.copy(), (0, 0, 8, 8), 20,
                              Image.new("L", image.size), foreground=(220, 220, 220),
                              native_antialiasing=True)

    def test_wrap_keeps_the_exact_complete_resource_and_refuses_overflow(self):
        class Font:
            def getlength(self, text):
                return len(text)

        text = 'Web@ と @ の説明'
        self.assertEqual("".join(native.wrap_label(text, Font(), 8, 2)), text)
        with self.assertRaises(shared.FigureFitError):
            native.wrap_label(text, Font(), 3, 2)

    def test_namespaced_resource_preserves_inline_text_and_context(self):
        xml = """<xliff xmlns="urn:oasis:names:tc:xliff:document:1.2"><file
        source-language="en-US" target-language="ja"><body><group resname="dialog">
        <trans-unit id="1" resname="caption"><source>A<g>B</g>C</source>
        <target>X<g>Y</g>Z</target></trans-unit></group></body></file></xliff>"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.xlf"
            path.write_text(xml)
            unit, = native.resource_units(path)
            self.assertEqual(unit["source"], "ABC")
            self.assertEqual(unit["target"], "XYZ")
            self.assertEqual(unit["context"], [{"resname": "dialog"}])
            self.assertEqual(unit["languages"]["target-language"], "ja")


class EditorCaptureTest(unittest.TestCase):
    def test_supplied_captures_replay_without_rescaling_or_painted_code(self):
        records = native.native_captures()
        self.assertEqual([record["figure"] for record in records], ["fig-02", "fig-03"])
        for record in records:
            with self.subTest(figure=record["figure"]):
                with Image.open(native.ROOT / record["capture"]) as capture:
                    with Image.open(native.ROOT / record["output"]) as output:
                        expected = capture.crop(record["crop"]) if record["crop"] else capture
                        self.assertEqual(output.mode, capture.mode)
                        self.assertEqual(output.tobytes(), expected.tobytes())
                        self.assertEqual(output.info["srgb"], capture.info["srgb"])
                        self.assertEqual(output.info["dpi"], capture.info["dpi"])
        self.assertEqual(
            records[1]["code"],
            (native.ROOT / "figures/fig-03.en.txt").read_text().splitlines()[-1],
        )

    def test_stale_capture_hash_is_an_error_not_a_silent_fallback(self):
        manifest = json.loads((native.ROOT / native.CAPTURES).read_text())
        manifest["captures"][0]["output_sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "captures.json"
            path.write_text(json.dumps(manifest))
            with patch.object(native, "CAPTURES", path):
                with self.assertRaisesRegex(ValueError, "Edited native capture artifact"):
                    native.native_captures()


@unittest.skipUnless(sys.platform == "darwin", "Requires the approved local 4D/Hiragino installation")
class NativeScreenshotTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = Path("/Applications/4D 20.8/4D.app")
        text = "".join(native.resolve(cls.app, region)["target"]
                       for regions in native.REGIONS.values() for region in regions)
        text += "ドキュメンテーションを編集..."
        cls.paths, _ = shared.load_fonts(text)
        cls.report = json.loads((native.ROOT / native.ARTIFACTS / "render.json").read_text())

    def test_resource_backed_labels_remain_line_aligned_and_values_are_unchanged(self):
        native.validate_labels(self.app)
        self.assertEqual(
            (native.ROOT / "figures/fig-04.ja.txt").read_text().splitlines()[8:10],
            ["True", "False"],
        )
        self.assertEqual(
            (native.ROOT / "figures/fig-05.ja.txt").read_text().splitlines()[2:11],
            (native.ROOT / "figures/fig-05.en.txt").read_text().splitlines()[2:11],
        )

    def test_three_actual_figures_replay_and_preserve_all_unmasked_pixels_and_metadata(self):
        protected = {
            "fig-01": [(293, 107, 683, 134), (293, 296, 315, 383), (293, 516, 358, 538)],
            "fig-04": [(459, 134, 776, 164), (298, 375, 381, 430)],
            "fig-05": [(34, 215, 780, 581), (34, 590, 63, 621), (20, 0, 150, 78)],
        }
        for stem in native.REGIONS:
            with self.subTest(figure=stem):
                result, erase, draw, metadata, report = native.render(stem, self.app, self.paths)
                with Image.open(native.ROOT / f"figures/{stem}.png") as image:
                    original = image.copy()
                allowed = ImageChops.lighter(erase, draw).point(lambda value: 255 if value else 0)
                self.assertIsNone(ImageChops.multiply(
                    shared.changed_pixels(original, result), ImageChops.invert(allowed),
                ).getbbox())
                for box in protected[stem]:
                    self.assertEqual(original.crop(box).tobytes(), result.crop(box).tobytes())
                encoded = native.encode(result, metadata)
                self.assertEqual(encoded, (native.ROOT / f"figures/{stem}-ja.png").read_bytes())
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "roundtrip.png"
                    path.write_bytes(encoded)
                    with Image.open(path) as decoded:
                        self.assertEqual(decoded.size, original.size)
                        self.assertEqual(decoded.mode, original.mode)
                        self.assertEqual(decoded.info.get("icc_profile"), metadata.get("icc_profile"))
                        self.assertEqual(decoded.info.get("dpi"), metadata.get("dpi"))
                record = next(item for item in self.report["figures"] if item["figure"] == stem)
                self.assertEqual(record["labels"], json.loads(json.dumps(report["labels"])))
                for kind, mask in [("erase", erase), ("draw", draw)]:
                    self.assertEqual(native.encode(mask), (native.ROOT / record["masks"][kind]).read_bytes())

    def test_native_explorer_capture_supersedes_the_historical_mechanical_fit_blocker(self):
        report = native.blocked_explorer(self.app, self.paths)
        self.assertFalse(report["mechanical_replacement_enabled"])
        self.assertEqual(len(report["labels"]), 2)
        for label in report["labels"]:
            self.assertGreater(label["full_label_width_px"], label["available_width_px"])
        layout = json.loads((native.ROOT / "figures/layout/fig-02.json").read_text())
        self.assertEqual(layout["replace"], "fig-02-ja.png")
        self.assertEqual(self.report["blocked"], [])
        self.assertEqual(self.report["reviewed_native_captures"], str(native.CAPTURES))
        self.assertTrue(any(record["figure"] == "fig-02" for record in native.native_captures()))


if __name__ == "__main__":
    unittest.main()
