import re
import sys

# Utilisation : python correction_ttl.py <fichier_source.ttl> <fichier_corrige.ttl>

if len(sys.argv) != 3:
    print("Usage: python correction_ttl.py <source.ttl> <output.ttl>")
    sys.exit(1)

source_file = sys.argv[1]
output_file = sys.argv[2]

with open(source_file, 'r', encoding='utf-8') as file:
    content = file.read()

# Correction des labels vides
content = re.sub(r'rdfs:label "" ;', 'rdfs:label "Non spécifié" ;', content)

# Correction des points-virgules mal placés (remplacer les points seuls par des points-virgules sauf fin de définition)
content = re.sub(r'\.(\s*ns1:)', r';\1', content)

# Correction du préfixe ns1 mal utilisé
content = re.sub(r'(@prefix ns1: <.*?>)\s*\.', r'\1 .', content)

# Suppression des espaces multiples et remplacement par un espace unique
content = re.sub(r'\s+', ' ', content)

# Réorganisation claire des propriétés sur plusieurs lignes
content = re.sub(r'(;\s*)(ns1:\w+)', r';\n    \2', content)
content = re.sub(r'(\.[\s]*)', r'.\n\n', content)

# Écrire le contenu corrigé dans le nouveau fichier
with open(output_file, 'w', encoding='utf-8') as file:
    file.write(content)

print(f"Correction terminée. Fichier sauvegardé sous '{output_file}'.")
