import json
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import render_demo_screenshots as renderer


class ErasureTest(unittest.TestCase):
    def test_restores_only_glyphs_and_preserves_locked_annotation(self):
        original = Image.new("RGB", (32, 16), (42, 40, 38))
        ImageDraw.Draw(original).rectangle((2, 2, 5, 5), fill=(220, 219, 217))
        original.putpixel((3, 3), (255, 38, 0))
        protected = Image.new("L", original.size)
        protected.putpixel((3, 3), 255)
        candidate = original.copy()
        mask, _, _ = renderer.erase_text(original, candidate, (0, 0, 8, 8), 20, protected)
        self.assertEqual(candidate.getpixel((2, 2)), (42, 40, 38))
        self.assertEqual(candidate.getpixel((3, 3)), (255, 38, 0))
        self.assertEqual(mask.getpixel((3, 3)), 0)
        changed = renderer.changed_pixels(original, candidate)
        self.assertIsNone(ImageChops.multiply(changed, ImageChops.invert(mask)).getbbox())

    def test_nonuniform_donor_is_rejected(self):
        original = Image.new("RGB", (32, 16), (42, 40, 38))
        original.putpixel((21, 0), (255, 38, 0))
        with self.assertRaisesRegex(ValueError, "Nonuniform background donor"):
            renderer.erase_text(original, original.copy(), (0, 0, 8, 8), 20, Image.new("L", original.size))

    def test_existing_editor_image_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "figure.png"
            renderer.write_new_bytes(path, b"generated")
            renderer.write_new_bytes(path, b"generated")
            path.write_bytes(b"editor correction")
            with self.assertRaises(FileExistsError):
                renderer.write_new_bytes(path, b"generated")
            self.assertEqual(path.read_bytes(), b"editor correction")


@unittest.skipUnless(sys.platform == "darwin", "Local Hiragino Sans/CoreText verification requires macOS")
class HiraginoTrialTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prepared = json.loads(renderer.PREPARED.read_text())
        text = "".join(label["target"] for figure in cls.prepared["figures"]
                       for label in figure["labels"] if "target" in label)
        cls.paths, cls.fonts = renderer.load_fonts(text)

    def test_exact_faces_and_glyphs_resolve_without_fallback(self):
        for weight in (3, 6):
            self.assertEqual(self.fonts[str(weight)]["postscript_name"], f"HiraginoSans-W{weight}")
            self.assertTrue(self.fonts[str(weight)]["characters_checked"])
        with self.assertRaisesRegex(ValueError, "lacks glyphs"):
            renderer.verify_native_font(self.paths[3], 3, "\uffff")

    def test_three_actual_figures_preserve_values_controls_and_every_unmasked_pixel(self):
        for prepared in self.prepared["figures"]:
            if prepared["figure"] == "fig-07":
                continue
            with self.subTest(figure=prepared["figure"]):
                candidate, erase, draw, report = renderer.render_figure(prepared, self.paths)
                with Image.open(renderer.ROOT / f"figures/{prepared['figure']}.png") as image:
                    original = image.copy()
                self.assertEqual(candidate.size, original.size)
                self.assertEqual(candidate.mode, original.mode)
                self.assertEqual(report["unexpected_changes"], 0)
                allowed = ImageChops.lighter(erase, draw).point(lambda value: 255 if value else 0)
                changed = renderer.changed_pixels(original, candidate)
                self.assertIsNone(ImageChops.multiply(changed, ImageChops.invert(allowed)).getbbox())
                self.assertIsNone(ImageChops.multiply(changed, renderer.protected_pixels(original)).getbbox())
                for box in [(154, 212, 583, 808), (472, 831, 584, 882)]:
                    self.assertEqual(original.crop(box).tobytes(), candidate.crop(box).tobytes())
                self.assertEqual(original.getpixel((638, 452)), candidate.getpixel((638, 452)))
                self.assertTrue(all(item["source_glyph_residual_pixels"] == 0 for item in report["labels"]))
                again, _, _, _ = renderer.render_figure(prepared, self.paths)
                self.assertEqual(renderer.encode_png(candidate), renderer.encode_png(again))

    def test_figure_07_rejects_red_annotation_collision_instead_of_shrinking_text(self):
        prepared = next(figure for figure in self.prepared["figures"] if figure["figure"] == "fig-07")
        with self.assertRaisesRegex(renderer.FigureFitError, "MPM_FilterLabel at 26px"):
            renderer.render_figure(prepared, self.paths)


if __name__ == "__main__":
    unittest.main()
