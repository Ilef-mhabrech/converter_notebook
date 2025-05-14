#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from rdflib import Graph
import pandas as pd

def load_graph(path: str) -> Graph:
    if not os.path.isfile(path):
        sys.exit(f"[Erreur] Fichier introuvable : {path}")
    g = Graph()
    try:
        g.parse(path, format="turtle")
    except Exception as e:
        sys.exit(f"[Erreur] Échec du parse Turtle : {e}")
    return g

def build_query() -> str:
    PREFIXES = {
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "ns1":  "http://example.org/course/",
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

def main():
    ttl_path = "ttl_corrigé/M1_Architecture_Logicielle_Mention_Informatique.ttl"
    graph = load_graph(ttl_path)
    results = graph.query(build_query())

    rows = []
    for ue, label, content, objective, hours, semester, level in results:
        rows.append({
            "UE":        str(ue),
            "Label":     str(label),
            "Contenu":   str(content)   if content   else "",
            "Objectif":  str(objective) if objective else "",
            "Heures":    str(hours)     if hours     else "",
            "Semestre":  str(semester)  if semester  else "",
            "Niveau":    str(level)     if level     else "",
        })
    df = pd.DataFrame(rows)

    if df.empty:
        print("[Info] Aucune donnée renvoyée par la requête.")
    else:
        # Affichage Markdown (nécessite tabulate) :
        print(df.to_markdown(index=False))

if __name__ == "__main__":
    main()
