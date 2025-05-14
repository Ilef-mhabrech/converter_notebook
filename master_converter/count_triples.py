#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
count_triples.py

Charge un fichier .ttl, le nettoie des artefacts Python (b'…', b"…", \xHH, etc.),
le parse en RDF et exécute une requête SPARQL pour compter les triples.
"""

import sys, re
import rdflib

def load_and_clean_ttl(path):
    # 1) Lecture brute (on ignore les erreurs d'encodage)
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        raw = f.read()
    # 2) Normalisation des retours chariot
    text = raw.replace('\r\n', '\n').replace('\r', '\n')
    # 3) Retirer TOUTES les occurrences b'...' et b"..." (multiligne)
    text = re.sub(r"b(['\"])(?:\\.|(?!\1).)*\1", "", text, flags=re.DOTALL)
    # 4) Nettoyage résiduel : enlever tout « b' » ou « b" »
    text = text.replace("b'", "").replace('b"', "")
    # 5) Supprimer les séquences d’échappement hexadécimal \xHH
    text = re.sub(r'\\x[0-9A-Fa-f]{2}', "", text)
    # 6) Remplacer les littéraux "nan" par ""
    text = re.sub(r'"\s*nan\s*"', '""', text, flags=re.IGNORECASE)
    return text

def count_triples(ttl_path):
    g = rdflib.Graph()
    cleaned = load_and_clean_ttl(ttl_path)
    # on parse depuis la chaîne nettoyée
    g.parse(data=cleaned, format="ttl")
    # SPARQL pour compter
    q = """
    SELECT (COUNT(*) AS ?count)
    WHERE { ?s ?p ?o . }
    """
    res = g.query(q)
    for row in res:
        return int(row.count)
    return 0

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <fichier.ttl>")
        sys.exit(1)
    ttl_file = sys.argv[1]
    try:
        n = count_triples(ttl_file)
        print(f"Nombre de triples dans {ttl_file}: {n}")
    except Exception as e:
        print(f"Erreur lors du comptage des triples : {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()
