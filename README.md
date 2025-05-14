# 🎓 Masters Converter Notebook

A toolkit to bulk-convert university Master’s program outlines (PDF → Excel → CSV & Turtle).

---

## 🚀 Table of Contents

1. [Installation](#installation)  
2. [Prerequisites](#prerequisites)  
3. [Processing Workflow](#processing-workflow)  
4. [Usage](#usage)  
5. [Output Structure](#output-structure)  
6. [How It Works](#how-it-works)  
7. [Validating Turtle with SPARQL](#validating-turtle-with-sparql)  

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/Ilef-mhabrech/converter_notebook.git
cd converter_notebook

# 2. (Optional) Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate    # macOS / Linux

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt


##  Prerequisites
Python ≥ 3.7

pandas

openpyxl

## Processing Steps

**1-Download PDFs**
Fetch all Master’s program outlines in PDF from the university site:
https://sciences-techniques.univ-nantes.fr/formations/masters/master-informatique

**2-Convert PDF → Excel**
Use I Love PDF (or any PDF→Excel tool) to produce .xlsx files.

**3-Run the Script**
From the project root:
    ```bash 
 python3 master_converter/batch_masters.py

## Usage
After installation and placing your .xlsx files at the repository root, simply run:
       ```bash 
python3 master_converter/batch_masters.py

All output folders will be populated automatically.

## How It Works
**Initialization**

Creates four output directories (if missing):
csv/, ttl/, csv_metrics/, ttl_metrics/

Sets RDF prefixes for Turtle files.

**Data Extraction**

Iterates through every sheet in each .xlsx.

Identifies “Objectifs” sections to locate course units (UEs).

Extracts:

Metadata: key, title, level, semester, track, objective, content

Metrics: volume (hours), ects (credits)

**File Generation**

Metadata CSV → csv/<basename>.csv

Metadata Turtle → ttl/<basename>.ttl

Metrics CSV → csv_metrics/<basename>_metrics.csv

Metrics Turtle → ttl_metrics/<basename>_metrics.ttl

Each TTL file includes RDF prefix declarations and triples (ns1:…) describing the units and their credits.

## output structure :
.
├── batch_masters.py
├── requirements.txt
├── csv/             # Metadata CSV files
├── ttl/             # Metadata Turtle files
├── csv_metrics/     # Volume & ECTS CSV files
└── ttl_metrics/     # Volume & ECTS Turtle files

## Validating Turtle with SPARQL
Cleanup / Formatting :

chmod +x correction_ttl 
python3 python3 correction_ttl.py master_converter/ttl/ ttl_corrigé/

you can verify metrics also :
chmod +x fix_metrics_ttl.py
python3 fix_metrics_ttl.py

you can verifiy the content by : 
chmod +x verify_ttl.py
python3 verify_ttl.py ttl_corrigé/

Test a Single TTL File

chmod +x test/test_ttl.py
python3 test/test_ttl.py 

or Test All TTL Files : 

chmod +x test/parse_all_ttl.py
python3 test/parse_all_ttl.py 
python3 test/parse_all_ttl.py  master_converter/ttl results.md