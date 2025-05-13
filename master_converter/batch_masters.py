 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch-convert all .xlsx in ../fichier_Excel into:
  - master_converter/csv/         : metadata CSV
  - master_converter/ttl/         : metadata TTL
  - master_converter/csv_metrics/ : volume+ECTS CSV
  - master_converter/ttl_metrics/ : volume+ECTS TTL

Extracts for each course unit:
  key, title, level, semester, track, objective, content, volume, ects.
"""

import os
import glob
import pandas as pd

# --- 1) Directory setup ---
SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR   = os.path.dirname(SCRIPT_DIR)
EXCEL_DIR     = os.path.join(PROJECT_DIR, "fichier_Excel")
CSV_DIR       = os.path.join(SCRIPT_DIR, "csv")
TTL_DIR       = os.path.join(SCRIPT_DIR, "ttl")
METRIC_CSV_DIR= os.path.join(SCRIPT_DIR, "csv_metrics")
METRIC_TTL_DIR= os.path.join(SCRIPT_DIR, "ttl_metrics")

for d in (CSV_DIR, TTL_DIR, METRIC_CSV_DIR, METRIC_TTL_DIR):
    os.makedirs(d, exist_ok=True)

# --- 2) Utility functions ---

def to_str(val):
    """
    - Decode bytes → UTF-8 str
    - Map NaN → empty string
    - Else cast to str
    """
    if isinstance(val, (bytes, bytearray)):
        return val.decode("utf-8", errors="replace")
    if pd.isna(val):
        return ""
    return str(val)

def sanitize(key: str) -> str:
    """Make a valid Turtle identifier from arbitrary text."""
    return "".join(c if c.isalnum() else "_" for c in key.strip())

def triple_literal(prop: str, val: str, last: bool=False) -> str:
    """
    Render a Turtle literal triple for property ns1:prop with text val.
    Uses ";" or "." correctly depending on last.
    """
    if not val:
        return ""
    # drop stray carriage returns
    val = val.replace('\r', '')
    # escape backslashes and quotes
    esc = val.replace('\\', '\\\\').replace('"', '\\"')
    # choose single-line or block literal
    if "\n" in esc or len(esc) >= 60:
        lit = '"""\n' + esc + '\n"""'
    else:
        lit = f'"{esc}"'
    sep = " ." if last else " ;"
    return f"    ns1:{prop} {lit}{sep}\n"

# RDF prefixes for all TTL files
PREFIX = """@prefix ns1: <http://example.org/masters/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

"""

# --- 3) Extraction from a DataFrame ---

def extract_from_df(df: pd.DataFrame):
    # first column as strings
    col0 = df.iloc[:, 0].astype(str)
    # skip sheets without any "Objectifs"
    if not col0.str.contains("Objectifs", case=False, na=False).any():
        return None

    def get_val(keyword: str) -> str:
        m = col0.str.contains(keyword, case=False, na=False)
        if not m.any():
            return ""
        idx = m.idxmax()
        return to_str(df.iat[idx, 1]) if df.shape[1] > 1 else ""

    header = to_str(df.iat[0, 0])
    if "|" in header:
        key, title = map(lambda s: to_str(s.strip()), header.split("|", 1))
    else:
        key   = get_val("X") or header.strip()
        title = to_str(df.iat[0, 1]) if df.shape[1] > 1 else ""

    return {
        "key":       to_str(key),
        "title":     to_str(title),
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

# --- 4) Writing outputs ---

def write_metadata_csv(recs, base):
    df = pd.DataFrame(recs, columns=[
        "key", "title", "level", "semester",
        "parcours", "objective", "content"
    ])
    path = os.path.join(CSV_DIR, base + ".csv")
    df.to_csv(path, sep="|", index=False, encoding="utf-8-sig")
    print(f"→ {os.path.relpath(path)}")

def write_metadata_ttl(recs, base):
    path = os.path.join(TTL_DIR, base + ".ttl")
    with open(path, "w", encoding="utf-8") as f:
        f.write(PREFIX)
        for r in recs:
            subj = sanitize(r["key"])
            # 1) échappement propre des backslashes et guillemets
            title_esc = r["title"].replace('\\', '\\\\').replace('"', '\\"')
            # 2) écriture avec un f-string simple
            f.write(f'ns1:{subj} rdfs:label "{title_esc}" ;\n')
            f.write(triple_literal("content",   r["content"]))
            f.write(triple_literal("level",     r["level"]))
            f.write(triple_literal("semester",  r["semester"]))
            f.write(triple_literal("objective", r["objective"]))
            f.write(triple_literal("parcours",  r["parcours"], last=True))
            f.write("\n")
    print(f"→ {os.path.relpath(path)}")


def write_metrics_csv(recs, base):
    df = pd.DataFrame(recs, columns=["key", "volume", "ects"])
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

# --- 5) Main batch process ---

def main():
    files = glob.glob(os.path.join(EXCEL_DIR, "*.xlsx"))
    if not files:
        print("Aucun .xlsx trouvé dans:", EXCEL_DIR)
        return

    for xlsx in files:
        base = os.path.splitext(os.path.basename(xlsx))[0]
        recs = extract_all(xlsx)
        if not recs:
            print(f"Aucune UE extraite de {base}")
            continue
        write_metadata_csv(recs, base)
        write_metadata_ttl(recs, base)
        write_metrics_csv(recs, base)
        write_metrics_ttl(recs, base)

if __name__ == "__main__":
    main()