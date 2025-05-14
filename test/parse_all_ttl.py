#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
parse_all_ttl_to_file.py
------------------------
Parcourt tous les .ttl d'un dossier, exécute la même requête SPARQL
sur chacun, et agrège dans un DataFrame pandas.
Enregistre le résultat dans un fichier CSV ou Markdown.

Usage :
  source .venv/bin/activate
  pip install rdflib pandas tabulate
  chmod +x parse_all_ttl_to_file.py
  python3 parse_all_ttl_to_file.py ttl_folder [output_file]

  - ttl_folder    : chemin vers le dossier contenant les .ttl
  - output_file   : (optionnel) fichier de sortie (CSV ou .md)
                    par défaut 'results.csv'
"""
import sys
import os
import glob
from rdflib import Graph
import pandas as pd
from urllib.parse import urlparse

def load_graph(path: str, fmt: str = "turtle") -> Graph:
    if not os.path.isfile(path):
        sys.exit(f"[Erreur] Fichier introuvable : {path}")
    g = Graph()
    try:
        g.parse(path, format=fmt)
    except Exception as e:
        sys.exit(f"[Erreur] parse Turtle {os.path.basename(path)} : {e}")
    return g

def build_query() -> str:
    PREFIXES = {
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "ns1" : "http://example.org/course/",
    }
    prefixes_str = "\n".join(f"PREFIX {p}: <{uri}>" for p, uri in PREFIXES.items())
    return prefixes_str + """

SELECT ?ue ?label ?content ?objective ?hours ?semester ?level WHERE {
  ?ue rdfs:label    ?label    .
  OPTIONAL { ?ue ns1:content   ?content   . }
  OPTIONAL { ?ue ns1:objective ?objective . }
  OPTIONAL { ?ue ns1:hours     ?hours     . }
  OPTIONAL { ?ue ns1:semester  ?semester  . }
  OPTIONAL { ?ue ns1:level     ?level     . }
}
"""

def short_name(uri: str) -> str:
    p = urlparse(uri)
    if p.fragment:
        return p.fragment
    return p.path.rsplit("/", 1)[-1] or uri

def main():
    # Arguments
    if len(sys.argv) < 2:
        print("Usage: python3 parse_all_ttl_to_file.py ttl_folder [output_file]")
        sys.exit(1)
    ttl_dir = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'results.csv'

    pattern = os.path.join(ttl_dir, "*.ttl")
    files = glob.glob(pattern)
    if not files:
        sys.exit(f"[Erreur] Aucun fichier .ttl trouvé dans {ttl_dir}")

    all_rows = []
    query = build_query()

    for path in files:
        g = load_graph(path)
        for ue, label, content, objective, hours, semester, level in g.query(query):
            all_rows.append({
                "Fichier"  : os.path.basename(path),
                "UE"       : short_name(str(ue)),
                "Label"    : str(label),
                "Contenu"  : str(content)   if content   else "",
                "Objectif" : str(objective) if objective else "",
                "Heures"   : str(hours)     if hours     else "",
                "Semestre" : str(semester)  if semester  else "",
                "Niveau"   : str(level)     if level     else "",
            })

    df = pd.DataFrame(all_rows)
    if df.empty:
        print("[Info] Aucune donnée trouvée dans vos TTL.")
    else:
        # Supprimer les colonnes entièrement vides
        df = df.replace('', pd.NA).dropna(axis=1, how='all')
        # Choix du format en fonction de l'extension
        ext = os.path.splitext(output_file)[1].lower()
        if ext in ('.md', '.markdown'):
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(df.to_markdown(index=False))
        else:
            df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Résultats enregistrés dans {output_file}")

if __name__ == "__main__":
    main()
