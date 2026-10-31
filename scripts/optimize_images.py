"""Rebuild responsive WebP copies without changing the original product photos.

Run from any directory: .venv/bin/python scripts/optimize_images.py
Pillow is already included in requirements.txt.
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "app/static/img/services"
DESTINATION = ROOT / "app/static/img/optimized"


def main():
    DESTINATION.mkdir(parents=True, exist_ok=True)
    for source in sorted(SOURCE.glob("*.jpg")):
        with Image.open(source) as image:
            for width in (320, 640):
                resized = image.copy()
                resized.thumbnail((width, 2000))
                resized.save(
                    DESTINATION / f"{source.stem}-{width}.webp",
                    "WEBP", quality=78, method=6,
                )
    print("Responsive product photos rebuilt.")


if __name__ == "__main__":
    main()
