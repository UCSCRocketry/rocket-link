#!/usr/bin/env python3

import os
import re
from pathlib import Path
from PIL import Image

SRC_DIR = "."
WEBP_QUALITY = 100
VERBOSE = True


def log(message):
    """Simple logging function."""
    if VERBOSE:
        print(f"[INFO] {message}")


def convert_png_to_webp(png_path):
    """
    Convert a single PNG to WebP.
    Returns True if converted, False if skipped.
    """
    webp_path = png_path.with_suffix(".webp")

    if webp_path.exists() and webp_path.stat().st_mtime >= png_path.stat().st_mtime:
        return False

    try:
        with Image.open(png_path) as img:
            if img.mode == "RGBA":
                alpha = img.getchannel("A")
                if alpha.getextrema() == (255, 255):
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background

            img.save(webp_path, "WEBP", quality=WEBP_QUALITY, optimize=True)

        original_size = png_path.stat().st_size
        new_size = webp_path.stat().st_size
        savings = int(((original_size - new_size) / original_size) * 100)

        log(
            f"Converted {png_path.name} → {webp_path.name} "
            f"({original_size:,} → {new_size:,} bytes, {savings}% smaller)"
        )

        return True

    except Exception as e:
        print(f"[ERROR] Failed to convert {png_path}: {e}")
        if webp_path.exists():
            webp_path.unlink()
        return False


def update_markdown_file(md_path):
    try:
        content = md_path.read_text(encoding="utf-8")
        original_content = content

        patterns = [
            (r"(!\[[^\]]*\]\([^)]*?)\.png(\))", r"\1.webp\2"),
            (r"(\[[^\]]*\]\([^)]*?)\.png(\))", r"\1.webp\2"),
            (r'(src=["\'][^"\']*?)\.png(["\'])', r"\1.webp\2"),
        ]

        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

        if content != original_content:
            md_path.write_text(content, encoding="utf-8")

            png_count = len(re.findall(r"\.png", original_content, re.IGNORECASE))
            webp_count = len(re.findall(r"\.webp", content, re.IGNORECASE))
            replacements = webp_count - (
                webp_count
                - png_count
                + len(re.findall(r"\.png", content, re.IGNORECASE))
            )

            log(f"Updated {replacements} PNG reference(s) in {md_path.name}")
            return True

        return False

    except Exception as e:
        print(f"[ERROR] Failed to update {md_path}: {e}")
        return False


def main():
    """Main conversion process."""
    src_path = Path(SRC_DIR)

    if not src_path.exists():
        print(f"[ERROR] Directory '{SRC_DIR}' not found")
        return 1

    log(f"Processing directory: {src_path}")
    log(f"WebP quality: {WEBP_QUALITY}")

    png_files = list(src_path.rglob("*.png"))
    if not png_files:
        log("No PNG files found")
    else:
        log(f"Found {len(png_files)} PNG files")
        converted = 0

        for png_path in png_files:
            if convert_png_to_webp(png_path):
                converted += 1

        log(f"Converted {converted} new/updated images")

    md_files = list(src_path.rglob("*.html"))
    if not md_files:
        log("No Markdown files found")
    else:
        log(f"Found {len(md_files)} Markdown files")
        updated = 0

        for md_path in md_files:
            if update_markdown_file(md_path):
                updated += 1

        log(f"Updated {updated} Markdown files")

    log("Conversion complete!")
    return 0


if __name__ == "__main__":
    exit(main())
