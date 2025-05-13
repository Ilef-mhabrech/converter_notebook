#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clean_ttl2.py

Nettoie tous les .ttl d'un dossier en :
  1) supprimant les artefacts b'…' (même multi-ligne)
  2) remplaçant les littéraux "nan" par ""
  3) retirant complètement les blocs où le sujet est vide (ns1: <nothing>)
Résultat -> fichiers *_clean.ttl dans un dossier à part.
"""

import os, re, glob, argparse

def clean_text(text: str) -> str:
    # 1) retirer tous les b'…'
    text = re.sub(
        r"b'((?:\\.|[^'])*)'",
        lambda m: m.group(1),
        text,
        flags=re.DOTALL
    )
    # 2) remplacer "nan" insensible à la casse
    text = re.sub(r'"\s*nan\s*"', '""', text, flags=re.IGNORECASE)
    return text

def filter_empty_subject_blocks(text: str) -> str:
    # on découpe en blocs séparés par une ligne vide
    blocks = text.split('\n\n')
    out = []
    for blk in blocks:
        # trouver la première ligne non vide
        for line in blk.splitlines():
            if line.strip()=='': continue
            first = line
            break
        else:
            # bloc vide
            continue
        # si sujet vide "ns1:" suivi d'espace, on jette le bloc
        if re.match(r'^ns1:\s', first):
            continue
        out.append(blk)
    # on recompose, en conservant les doubles sauts de ligne
    return '\n\n'.join(out)

def process_file(path:str, dest_dir:str):
    text = open(path, encoding='utf-8').read()
    cleaned = clean_text(text)
    filtered = filter_empty_subject_blocks(cleaned)
    base = os.path.basename(path)
    name, ext = os.path.splitext(base)
    out = os.path.join(dest_dir, f"{name}_clean{ext}")
    with open(out, 'w', encoding='utf-8') as f:
        f.write(filtered)
    print(f"→ {out}")

def main():
    p = argparse.ArgumentParser(
        description="Nettoie et purifie tous les .ttl d'un dossier"
    )
    p.add_argument("src_dir", help="Dossier source contenant les .ttl")
    p.add_argument("-d","--dest-dir", default=None,
                   help="Dossier cible (créé si besoin)")
    args = p.parse_args()

    src = args.src_dir
    dst = args.dest_dir or os.path.join(src, "clean2")
    if not os.path.isdir(src):
        print("Erreur: src_dir invalide:", src); return
    os.makedirs(dst, exist_ok=True)

    for ttl in glob.glob(os.path.join(src, "*.ttl")):
        process_file(ttl, dst)

if __name__=="__main__":
    main()
