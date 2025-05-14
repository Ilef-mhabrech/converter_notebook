#!/usr/bin/env python3
import rdflib
import argparse
import re
import tempfile
import os
from pathlib import Path
from rdflib import Graph, Namespace, URIRef, Literal

# Préfixes RDF courants pour cohérence
DEFAULT_PREFIXES = {
    'rdf':  'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
    'owl':  'http://www.w3.org/2002/07/owl#',
    'xsd':  'http://www.w3.org/2001/XMLSchema#',
}

def preprocess_raw(input_path: str) -> str:
    """
    Lit le fichier en octets, nettoie les artefacts de dumps Python,
    corrige le double-encodage UTF-8, insère les points manquants,
    puis retourne le texte prêt à parser.
    """
    raw = open(input_path, 'rb').read()
    # étape 1: décodage initial en UTF-8 (substitue erreurs)
    text = raw.decode('utf-8', errors='replace')
    # étape 2: interpréter les séquences d'échappement Python
    text = text.encode('utf-8').decode('unicode_escape', errors='replace')
    # étape 3: supprimer les artefacts b' et les séquences '^b'
    text = text.replace("^b", "").replace("b'", "").replace('b"', "")
    # étape 4: corriger le double-encodage (mojibake)
    text = text.encode('latin-1', errors='ignore').decode('utf-8', errors='ignore')
    # étape 5: garantir qu'après chaque bloc de triplets se termine par un point
    text = re.sub(r';\s*\n\s*(ns1:)', r';\n.\n\1', text)
    # étape 6: s'assurer que le fichier se termine par un point
    if not text.strip().endswith('.'):
        text += '\n.'
    # étape 7: suppression des caractères de contrôle superflus
    text = re.sub(r'[\x00-\x08\x0B-\x1F]', '', text)
    return text


def load_graph(input_ttl: str) -> Graph:
    """Charge le TTL, avec pré-nettoyage si nécessaire."""
    g = Graph()
    try:
        g.parse(input_ttl, format='turtle')
        print(f"[INFO] {input_ttl} chargé avec {len(g)} triplets.")
    except Exception:
        print(f"[WARN] parsing natif échoué pour {input_ttl}, nettoyage…")
        cleaned = preprocess_raw(input_ttl)
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.ttl', encoding='utf-8') as tmp:
            tmp.write(cleaned)
            tmp_path = tmp.name
        try:
            g.parse(tmp_path, format='turtle')
            print(f"[INFO] {input_ttl} (nettoyé) chargé avec {len(g)} triplets.")
        finally:
            os.remove(tmp_path)
    return g


def clean_uris(graph: Graph) -> int:
    """Normalise les URI : trim et encodage des espaces."""
    changes = 0
    for s, p, o in list(graph.triples((None, None, None))):
        for term, role in ((s, 's'), (p, 'p'), (o, 'o')):
            if isinstance(term, URIRef):
                orig = str(term)
                cleaned = orig.strip()
                cleaned = re.sub(r' ', '%20', cleaned)
                if cleaned != orig:
                    graph.remove((s, p, o))
                    parts = {'s': s, 'p': p, 'o': o}
                    parts[role] = URIRef(cleaned)
                    graph.add((parts['s'], parts['p'], parts['o']))
                    changes += 1
    print(f"[INFO] {changes} URI nettoyées.")
    return changes


def fix_prefixes(graph: Graph) -> int:
    """Lie les préfixes standards manquants."""
    existing = {p for p, _ in graph.namespaces()}
    bound = 0
    for prefix, uri in DEFAULT_PREFIXES.items():
        if prefix not in existing:
            graph.bind(prefix, Namespace(uri))
            bound += 1
    print(f"[INFO] {bound} préfixes liés.")
    return bound


def remove_empty_literals(graph: Graph) -> int:
    """Supprime les triplets dont le littéral est vide."""
    to_remove = list(graph.triples((None, None, Literal(''))))
    for s, p, o in to_remove:
        graph.remove((s, p, o))
    print(f"[INFO] {len(to_remove)} littéraux vides supprimés.")
    return len(to_remove)


def write_graph(graph: Graph, output_ttl: str) -> None:
    """Enregistre le graphe nettoyé au format Turtle."""
    graph.serialize(destination=output_ttl, format='turtle')
    print(f"[INFO] Écrit {output_ttl} ({len(graph)} triplets)." )


def process_file(input_path: Path, output_path: Path) -> None:
    """Traite et corrige un fichier TTL."""
    try:
        g = load_graph(str(input_path))
        clean_uris(g)
        fix_prefixes(g)
        remove_empty_literals(g)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        write_graph(g, str(output_path))
    except Exception as e:
        print(f"[ERROR] Impossible de traiter {input_path}: {e}")


def main():
    parser = argparse.ArgumentParser(description='Corriger des fichiers TTL RDF')
    parser.add_argument('input',  help="Fichier ou dossier d'entrée")
    parser.add_argument('output', help="Fichier ou dossier de sortie")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if input_path.is_dir():
        if output_path.exists() and not output_path.is_dir():
            print(f"[ERROR] {output_path} doit être un dossier.")
            return
        for root, _, files in os.walk(input_path):
            for fname in files:
                if fname.lower().endswith('.ttl'):
                    in_f = Path(root) / fname
                    rel = in_f.relative_to(input_path)
                    out_f = output_path / rel
                    process_file(in_f, out_f)
    else:
        if output_path.exists() and output_path.is_dir():
            print(f"[ERROR] {output_path} doit être un fichier.")
            return
        process_file(input_path, output_path)

if __name__ == '__main__':
    main()
