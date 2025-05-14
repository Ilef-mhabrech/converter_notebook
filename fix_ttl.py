 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_all_ttl.py

Nettoie et normalise tous les fichiers .ttl d'un dossier.
Les sauvegardes (.bak) sont déplacées dans un sous-dossier backups/.

Usage :
  source .venv/bin/activate
  pip install rdflib
  chmod +x fix_all_ttl.py
  python3 fix_all_ttl.py path/to/ttl_folder
"""

import sys, os, glob, shutil, re
from rdflib import Graph

def clean_raw(raw: str) -> str:
    # 1) Décoder les \xNN Pythons en UTF-8
    try:
        decoded = raw.encode('latin-1').decode('unicode-escape')
    except:
        decoded = raw
    # 2) Enlever b'…', b"…", ^b'…', ^b"…"
    cleaned = re.sub(r"(?:\^?b)'([^']*)'", r"\1", decoded)
    cleaned = re.sub(r'(?:\^?b)"([^"]*)"', r"\1", cleaned)
    # 3) Normaliser littéraux multi-ligne vers """..."""
    props = ['rdfs:label', 'ns1:content', 'ns1:objective', 'ns1:parcours']
    for p in props:
        pattern = re.compile(
            rf'(^\s*{p}\s*)"([^"\\]*?)\r?\n(.*?)"', 
            re.MULTILINE|re.DOTALL
        )
        def repl(m):
            prefix = m.group(1)
            first  = m.group(2).strip()
            rest   = m.group(3).rstrip()
            body   = first + '\n' + rest
            return f'{prefix}"""\n{body}\n"""'
        cleaned = pattern.sub(repl, cleaned)
    return cleaned

def fix_file(path: str, backup_dir: str):
    print(f"▶ Cleaning {os.path.basename(path)}")
    raw = open(path, 'r', encoding='latin-1', errors='ignore').read()
    cleaned = clean_raw(raw)

    # backup
    os.makedirs(backup_dir, exist_ok=True)
    bak = os.path.join(backup_dir, os.path.basename(path)+'.bak')
    shutil.copy2(path, bak)

    # parse & serialize
    g = Graph()
    try:
        g.parse(data=cleaned, format='turtle')
    except Exception as e:
        print(f"⚠ Cannot parse {os.path.basename(path)}: {e}\n")
        return
    g.serialize(destination=path, format='turtle')
    print(f"[✓] Fixed {os.path.basename(path)} (backup → backups/)\n")

def main(folder: str):
    ttl_files = glob.glob(os.path.join(folder, '*.ttl'))
    if not ttl_files:
        print(f"No .ttl files found in {folder}")
        sys.exit(1)
    backup_dir = os.path.join(folder, 'backups')
    for ttl in ttl_files:
        fix_file(ttl, backup_dir)

if __name__=='__main__':
    if len(sys.argv)!=2:
        print("Usage: python3 fix_all_ttl.py path/to/ttl_folder")
        sys.exit(1)
    main(sys.argv[1])