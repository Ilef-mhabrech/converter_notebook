#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
clean_ttl3.py

Nettoie tous les .ttl d'un dossier en :
  - retirant toute occurrence b'…' et b"…" (non-gourmand, multi-ligne)
  - supprimant les séquences d'échappement \xHH
  - remplaçant "nan" par ""
Produit, pour chaque foo.ttl, foo_clean.ttl dans un dossier séparé.
"""

import os
import re
import glob
import argparse

def clean_text(text: str) -> str:
    # 1) supprimer b'…' ou b"…"
    text = re.sub(r"b(['\"])(?:\\.|(?!\1).)*\1", "", text, flags=re.DOTALL)
    # 2) en plus supprimer toute occurrence isolée de b' ou b"
    text = text.replace("b'", "").replace('b"', "")
    # 3) supprimer les séquences \xHH
    text = re.sub(r'\\x[0-9A-Fa-f]{2}', "", text)
    # 4) remplacer les littéraux "nan" par ""
    text = re.sub(r'"\s*nan\s*"', '""', text, flags=re.IGNORECASE)
    return text

def process_file(path: str, dest_dir: str):
    with open(path, encoding='utf-8', errors='ignore') as f:
        src = f.read()
    cleaned = clean_text(src)

    basename = os.path.basename(path)
    name, ext = os.path.splitext(basename)
    out_name  = f"{name}_clean{ext}"
    out_path  = os.path.join(dest_dir, out_name)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(cleaned)
    print(f"Cleaned → {out_path}")

def main():
    parser = argparse.ArgumentParser(
        description="Nettoie les TTL en retirant b'…', b\"…\", \\xHH et nan"
    )
    parser.add_argument("src_dir", help="Dossier contenant les .ttl à nettoyer")
    parser.add_argument(
        "-d", "--dest-dir",
        help="Dossier cible (créé s’il n’existe pas)",
        default=None
    )
    args = parser.parse_args()

    src = args.src_dir
    dst = args.dest_dir or os.path.join(src, "clean3")

    if not os.path.isdir(src):
        print(f"Erreur : {src} n’est pas un dossier valide.")
        return

    os.makedirs(dst, exist_ok=True)

    files = glob.glob(os.path.join(src, "*.ttl"))
    if not files:
        print(f"Aucun .ttl trouvé dans {src}.")
        return

    for ttl in files:
        process_file(ttl, dst)

if __name__ == "__main__":
    main()
