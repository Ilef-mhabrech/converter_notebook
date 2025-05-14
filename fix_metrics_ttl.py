#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_metrics_ttl.py

Lit tous les .ttl de master_converter/ttl_metrics, corrige la syntaxe des blocs
(ns1:<Sujet> ns1:volume \"\"\"...\"\"\" ;) -> fusionne en une ligne et remplace ';' par '.',
puis écrit les fichiers corrigés dans ttl_metrics_corrige/.
"""

import os
import sys
import glob

SRC_DIR = "master_converter/ttl_metrics"
DST_DIR = "ttl_metrics_corrige"

def process_file(src_path, dst_path):
    with open(src_path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    # Récupérer les lignes de prefixes
    prefixes = []
    i = 0
    while i < len(lines) and lines[i].startswith("@prefix"):
        prefixes.append(lines[i])
        i += 1

    # Grouper le reste en blocs séparés par une ligne vide
    blocks = []
    current = []
    for line in lines[i:]:
        if line.strip() == "":
            if current:
                blocks.append(current)
                current = []
        else:
            current.append(line)
    if current:
        blocks.append(current)

    # Traiter chaque bloc
    fixed = []
    for block in blocks:
        # Fusionner toutes les lignes, nettoyer les espaces
        merged = " ".join(l.strip() for l in block)
        # Remplacer le point-virgule final par un point
        if merged.endswith(";"):
            merged = merged[:-1].rstrip() + " ."
        fixed.append(merged)

    # Écriture
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    with open(dst_path, "w", encoding="utf-8") as f:
        for p in prefixes:
            f.write(p + "\n")
        f.write("\n")
        for entry in fixed:
            f.write(entry + "\n\n")

def main():
    if not os.path.isdir(SRC_DIR):
        print(f"[Erreur] Dossier source introuvable : {SRC_DIR}")
        sys.exit(1)
    os.makedirs(DST_DIR, exist_ok=True)

    for src in glob.glob(os.path.join(SRC_DIR, "*.ttl")):
        name = os.path.basename(src)
        dst = os.path.join(DST_DIR, name)
        print(f"Traitement de {name}...")
        process_file(src, dst)

    print(f"\n✓ Fichiers corrigés dans le dossier « {DST_DIR}/ »")

if __name__ == "__main__":
    main()
