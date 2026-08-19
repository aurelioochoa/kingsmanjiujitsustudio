#!/usr/bin/env python3
"""Verify that the Chile assets are actually from Chile.

Background: the sister-academy section once shipped with Guayaquil material
relabelled as Huechuraba — chile-reel.mp4 was a byte-for-byte copy of
post01.mp4 (the lineage reel) and the "head coach" avatar was a crop of
assets/linaje/joffre.jpg. Every automated check passed because the files
served 200; nothing compared them to each other.

This catches that class of mistake:
- no file under assets/photos/chile or assets/videos/chile-*.mp4 may be
  byte-identical to any Guayaquil asset
- no two files anywhere in assets/ may be byte-identical (dead duplicates)
- every referenced asset must exist and carry the magic bytes for its
  extension, so a saved 404 page can never pass as a JPEG or MP4

Usage:
    python3 scripts/check_assets.py
Exits non-zero on any failure.
"""
import hashlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")

MAGIC = {
    ".jpg": [b"\xff\xd8\xff"],
    ".jpeg": [b"\xff\xd8\xff"],
    ".png": [b"\x89PNG\r\n\x1a\n"],
    ".webp": [b"RIFF"],
    ".mp4": None,   # checked via the ftyp box at offset 4
}


def digest(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def walk(rel):
    base = os.path.join(ROOT, rel)
    for dirpath, _, names in os.walk(base):
        for n in names:
            if not n.startswith("."):
                yield os.path.join(dirpath, n)


def is_chile(path):
    rel = os.path.relpath(path, ROOT)
    return "photos/chile/" in rel or re.search(r"videos/chile-[^/]+$", rel)


def magic_ok(path):
    ext = os.path.splitext(path)[1].lower()
    if ext not in MAGIC:
        return True
    with open(path, "rb") as f:
        head = f.read(16)
    if ext == ".mp4":
        return head[4:8] == b"ftyp"
    return any(head.startswith(sig) for sig in MAGIC[ext])


def referenced_assets():
    """Every local asset path referenced from the HTML."""
    out = set()
    pages = [os.path.join(ROOT, "index.html")]
    clases = os.path.join(ROOT, "pages", "clases")
    if os.path.isdir(clases):
        pages += [os.path.join(clases, f) for f in os.listdir(clases)
                  if f.endswith(".html")]
    for p in pages:
        html = open(p, encoding="utf-8").read()
        for ref in re.findall(r'(?:src|href|poster)="([^"]+)"', html):
            if ref.startswith(("#", "http", "//", "data:", "mailto:", "tel:")):
                continue
            target = os.path.normpath(os.path.join(os.path.dirname(p), ref))
            if os.path.commonpath([target, ASSETS]) == ASSETS:
                out.add(target)
    return out


def main():
    failures = []

    by_hash = {}
    for path in walk("assets"):
        by_hash.setdefault(digest(path), []).append(path)

    used = referenced_assets()
    for paths in by_hash.values():
        if len(paths) < 2:
            continue
        rels = sorted(os.path.relpath(p, ROOT) for p in paths)
        if any(is_chile(p) for p in paths) and not all(is_chile(p) for p in paths):
            failures.append("material de Guayaquil reetiquetado como Chile: "
                            + " == ".join(rels))
        elif not any(p in used for p in paths):
            # Copias muertas (p.ej. una carpeta de scrape repetida). Los pares
            # postNN.jpg / postNN_child0.jpg sí son idénticos de origen — así
            # expone Instagram el primer hijo de un carrusel — pero se usan.
            failures.append("duplicados sin usar, peso muerto: " + " == ".join(rels))

    for target in sorted(used):
        rel = os.path.relpath(target, ROOT)
        if not os.path.exists(target):
            failures.append("referenciado pero no existe: " + rel)
        elif not magic_ok(target):
            failures.append("contenido no coincide con la extensión "
                            "(¿un 404 guardado como imagen?): " + rel)

    if failures:
        print("FALLA (%d):" % len(failures))
        for f in failures:
            print("  -", f)
        return 1
    print("OK — sin duplicados entre Chile y Guayaquil, sin duplicados muertos, "
          "y todos los assets referenciados tienen el formato que dice su extensión.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
