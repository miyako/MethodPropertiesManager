#!/usr/bin/env python3
"""Compose figures into contact sheets for visual review.

The image viewer available to agents shows one image per call, so review
several figures at once:

  python tools/contact_sheet.py                 # all localised figures, 3 per sheet
  python tools/contact_sheet.py 02 04 10        # selected figures
  python tools/contact_sheet.py --compare 02    # original above, localised below

Sheets are written to build/contact-N.png. Use --draft for unenabled
replacement images and separate build/draft-contact-N.png sheets.
"""
import argparse
import sys

from PIL import Image, ImageDraw

import config

FIG = config.ROOT / "figures"
OUT = config.ROOT / "build"


def load(path, width):
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, "white")
    bg.alpha_composite(im)
    im = bg.convert("RGB")
    return im.resize((width, max(1, int(im.height * width / im.width))))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("figures", nargs="*", help="figure numbers, e.g. 02 11")
    ap.add_argument("--per-sheet", type=int, default=3)
    ap.add_argument("--width", type=int, default=900)
    ap.add_argument("--compare", action="store_true", help="stack original above localised")
    ap.add_argument("--draft", action="store_true", help="preview unenabled figures/fig-NN-<target>.png")
    args = ap.parse_args()
    language = config.load()["target_lang"]
    if args.draft:
        available = sorted(p.stem.removesuffix(f"-{language}") for p in FIG.glob(f"fig-*-{language}.png"))
    else:
        available = sorted(p.stem for p in (OUT / "figures").glob("fig-*.png"))
    names = [f"fig-{int(n):02d}" for n in args.figures] or available
    if not names:
        sys.exit("No draft figures available" if args.draft else "No figures in build/figures; run `make figures` first")
    if args.draft:
        missing = [name for name in names if not (FIG / f"{name}-{language}.png").is_file()]
        if missing:
            ap.error(f"No draft replacement for: {', '.join(missing)}")
    prefix = "draft-contact" if args.draft else "contact"
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob(f"{prefix}-*.png"):
        old.unlink()
    for s, i in enumerate(range(0, len(names), args.per_sheet), 1):
        tiles = []
        for name in names[i:i + args.per_sheet]:
            replacement = FIG / f"{name}-{language}.png" if args.draft else OUT / "figures" / f"{name}.png"
            parts = [load(replacement, args.width)]
            if args.compare:
                parts.insert(0, load(FIG / f"{name}.png", args.width))
            h = sum(p.height for p in parts) + 24 + 8 * (len(parts) - 1)
            tile = Image.new("RGB", (args.width, h), "white")
            ImageDraw.Draw(tile).text((4, 4), name + (" (draft)" if args.draft else ""), fill="red")
            y = 24
            for p in parts:
                tile.paste(p, (0, y))
                y += p.height + 8
            tiles.append(tile)
        sheet = Image.new("RGB", (args.width * len(tiles) + 10 * (len(tiles) - 1),
                                  max(t.height for t in tiles)), (200, 200, 200))
        for k, t in enumerate(tiles):
            sheet.paste(t, (k * (args.width + 10), 0))
        path = OUT / f"{prefix}-{s}.png"
        sheet.save(path)
        print(f"wrote: {path.relative_to(config.ROOT)} ({', '.join(names[i:i + args.per_sheet])})")


if __name__ == "__main__":
    main()
