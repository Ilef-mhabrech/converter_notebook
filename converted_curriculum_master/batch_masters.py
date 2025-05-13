#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch .xlsx → 
  - ./csv/          : metadata CSV
  - ./ttl/          : metadata TTL
  - ./csv_metrics/  : volume+ECTS CSV
  - ./ttl_metrics/  : volume+ECTS TTL

Pour chaque .xlsx du dossier, extrait UE + volume + ECTS.
"""

import os
import glob
import pandas as pd

# --- 1) Base dir & dossiers de sortie ---
BASE_DIR         = os.path.dirname(os.path.abspath(__file__))
CSV_DIR          = os.path.join(BASE_DIR, "csv")
TTL_DIR          = os.path.join(BASE_DIR, "ttl")
METRIC_CSV_DIR   = os.path.join(BASE_DIR, "csv_metrics")
METRIC_TTL_DIR   = os.path.join(BASE_DIR, "ttl_metrics")

for d in (CSV_DIR, TTL_DIR, METRIC_CSV_DIR, METRIC_TTL_DIR):
    os.makedirs(d, exist_ok=True)

os.chdir(BASE_DIR)

# --- 2) Préfixes pour TTL ---
PREFIX = """@prefix ns1: <http://example.org/masters/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

"""

def sanitize(key: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in key.strip())

def triple_literal(prop: str, val: str, last: bool=False) -> str:
    if not val or val.lower() == "nan":
        return ""
    esc = val.replace('\\', '\\\\').replace('"', '\\"')
    lit = f'"{esc}"' if "\n" not in esc and len(esc) < 60 else '"""\n' + esc + '\n"""'
    sep = " ." if last else " ;"
    return f"    ns1:{prop} {lit}{sep}\n"

# --- 3) Extraction d'une feuille ---
def extract_from_df(df: pd.DataFrame):
    col0 = df.iloc[:,0].astype(str)
    if not col0.str.contains("Objectifs", case=False, na=False).any():
        return None
    def get_val(keyword):
        m = col0.str.contains(keyword, case=False, na=False)
        if not m.any(): return ""
        idx = m.idxmax()
        return str(df.iat[idx,1]) if df.shape[1]>1 else ""
    header = str(df.iat[0,0])
    if "|" in header:
        key, title = map(str.strip, header.split("|",1))
    else:
        key   = get_val("X") or header.strip()
        title = str(df.iat[0,1]) if df.shape[1]>1 else ""
    return {
        "key":       key,
        "title":     title,
        "level":     get_val("Niveau"),
        "semester":  get_val("Semestre"),
        "parcours":  get_val("Parcours"),
        "objective": get_val("Objectifs"),
        "content":   get_val("Contenu"),
        "volume":    get_val("Volume"),
        "ects":      get_val("ECTS"),
    }

def extract_all(xlsx_path: str):
    wb   = pd.ExcelFile(xlsx_path)
    recs = []
    for sheet in wb.sheet_names:
        df = pd.read_excel(wb, sheet_name=sheet, header=None)
        rec = extract_from_df(df)
        if rec:
            recs.append(rec)
    return recs

# --- 4) Écriture des fichiers ---
def write_metadata_csv(recs, base):
    df = pd.DataFrame(recs, columns=[
        "key","title","level","semester",
        "parcours","objective","content"
    ])
    path = os.path.join(CSV_DIR, base + ".csv")
    df.to_csv(path, sep="|", index=False, encoding="utf-8-sig")
    print(f"→ {os.path.relpath(path)}")

def write_metadata_ttl(recs, base):
    path = os.path.join(TTL_DIR, base + ".ttl")
    with open(path, "w", encoding="utf-8") as f:
        f.write(PREFIX)
        for r in recs:
            subj      = sanitize(r["key"])
            title_esc = r["title"].replace('\\','\\\\').replace('"','\\"')
            f.write(f'ns1:{subj} rdfs:label "{title_esc}" ;\n')
            f.write(triple_literal("content",   r["content"]))
            f.write(triple_literal("level",     r["level"]))
            f.write(triple_literal("semester",  r["semester"]))
            f.write(triple_literal("objective", r["objective"]))
            f.write(triple_literal("parcours",  r["parcours"], last=True))
            f.write("\n")
    print(f"→ {os.path.relpath(path)}")

def write_metrics_csv(recs, base):
    df = pd.DataFrame(recs, columns=["key","volume","ects"])
    path = os.path.join(METRIC_CSV_DIR, base + "_metrics.csv")
    df.to_csv(path, sep="|", index=False, encoding="utf-8-sig")
    print(f"→ {os.path.relpath(path)}")

def write_metrics_ttl(recs, base):
    path = os.path.join(METRIC_TTL_DIR, base + "_metrics.ttl")
    with open(path, "w", encoding="utf-8") as f:
        f.write(PREFIX)
        for r in recs:
            subj = sanitize(r["key"])
            f.write(f"ns1:{subj} ")
            f.write(triple_literal("volume", r["volume"]))
            f.write(triple_literal("ects",   r["ects"], last=True))
            f.write("\n")
    print(f"→ {os.path.relpath(path)}")

# --- 5) Batch ---
def main():
    files = glob.glob("*.xlsx")
    if not files:
        print("Aucun .xlsx trouvé.")
        return
    for x in files:
        base = os.path.splitext(x)[0]
        recs = extract_all(x)
        if not recs:
            print(f"Aucune UE extraite de {x}")
            continue
        write_metadata_csv(recs, base)
        write_metadata_ttl(recs, base)
        write_metrics_csv(recs, base)
        write_metrics_ttl(recs, base)

if __name__ == "__main__":
    main()
