#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path
from rdflib import Graph, Namespace, RDF, RDFS, URIRef

# --- Préfixes RDF ---
NS1 = Namespace("http://example.org/masters/")
REQUIRED_PROPERTIES = [
    RDFS.label,
    NS1.content,
    NS1.objective,
    NS1.level,
    NS1.semester,
    NS1.parcours
]

# --- Chemin du dossier contenant les .ttl ---
if len(sys.argv) < 2:
    print("Usage : python3 verify_ttl.py dossier_ttl/")
    sys.exit(1)

ttl_dir = Path(sys.argv[1])
if not ttl_dir.is_dir():
    print(f"[ERREUR] Le dossier {ttl_dir} n'existe pas.")
    sys.exit(1)

ttl_files = list(ttl_dir.glob("*.ttl"))
if not ttl_files:
    print(f"[INFO] Aucun fichier .ttl trouvé dans {ttl_dir}")
    sys.exit(0)

print(f"\n🔍 Vérification des fichiers TTL dans le dossier : {ttl_dir}\n")

for ttl_path in ttl_files:
    g = Graph()
    try:
        g.parse(str(ttl_path), format="turtle")
    except Exception as e:
        print(f"❌ {ttl_path.name} — Erreur de syntaxe RDF : {e}")
        continue

    missing_props = {}
    for subj in set(g.subjects()):
        for prop in REQUIRED_PROPERTIES:
            if (subj, prop, None) not in g:
                missing_props.setdefault(subj, []).append(prop)
            else:
                for o in g.objects(subj, prop):
                    if not str(o).strip():
                        missing_props.setdefault(subj, []).append(prop)

    if missing_props:
        print(f"⚠ {ttl_path.name} — {len(g)} triplets — Propriétés manquantes ou vides :")
        for subj, props in missing_props.items():
            prop_names = ", ".join(p.split("#")[-1] if "#" in p else p.split("/")[-1] for p in props)
            print(f"   - {subj} → {prop_names}")
    else:
        print(f"✔ {ttl_path.name} — OK ({len(g)} triplets)")

print("\n✅ Vérification terminée.")
