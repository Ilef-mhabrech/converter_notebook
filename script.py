#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
from pathlib import Path
import textwrap

# --- chemins ---
input_dir = Path('fichier_excel')
csv_dir   = input_dir.parent / 'csv'
ttl_dir   = input_dir.parent / 'turtle'

csv_dir.mkdir(exist_ok=True)
ttl_dir.mkdir(exist_ok=True)

# --- préfixes pour Turtle ---
PREFIXES = textwrap.dedent("""\
    @prefix ns1: <http://example.org/course/> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

    """)

def quote_literal(s: str) -> str:
    """Échappe les guillemets et entoure en triple quotes si multilignes."""
    if not isinstance(s, str) or pd.isna(s):
        return '"nan"'
    # échappement simple des guillemets
    esc = s.replace('"', '\\"')
    # si multilignes, ou plus de 100 caractères, on met en triple quotes
    if '\n' in esc or len(esc) > 100:
        return '"""\n' + esc + '\n"""'
    else:
        return f'"{esc}"'

for xlsx in input_dir.glob('*.xlsx'):
    df = pd.read_excel(xlsx, dtype=str)  # tout en str pour simplifier
    # 1) CSV
    csv_path = csv_dir / f"{xlsx.stem}.csv"
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"→ {xlsx.name} → {csv_path.name}")

    # 2) Turtle
    ttl_path = ttl_dir / f"{xlsx.stem}.ttl"
    with ttl_path.open('w', encoding='utf-8') as f:
        f.write(PREFIXES)

        # on s'attend à ces colonnes dans le CSV :
        #   code, label, content, level, objective, parcours
        for _, row in df.iterrows():
            code      = row.get('code', '').strip()
            label     = quote_literal(row.get('label', 'nan'))
            content   = quote_literal(row.get('content', 'nan'))
            level     = quote_literal(row.get('level', 'nan'))
            objective = quote_literal(row.get('objective', 'nan'))
            parcours  = quote_literal(row.get('parcours', 'nan'))

            if not code:
                continue  # skip si pas de code
            f.write(f"ns1:{code} rdfs:label {label} ;\n")
            f.write(f"    ns1:content {content} ;\n")
            f.write(f"    ns1:level {level} ;\n")
            f.write(f"    ns1:objective {objective} ;\n")
            f.write(f"    ns1:parcours {parcours} .\n\n")

    print(f"→ {xlsx.name} → {ttl_path.name}")
