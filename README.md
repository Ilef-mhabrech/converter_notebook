# 🎓 Masters Converter Notebook

Bulk-convert university Master’s program outlines (PDF → Excel → CSV & Turtle) in one go.

---

## 🚀 Table of Contents

1. [Installation](#installation)  
2. [Prerequisites](#prerequisites)  
3. [Processing Steps](#processing-steps)  
4. [Usage](#usage)  
5. [How It Works](#how-it-works)  
6. [Output Structure](#output-structure) 
7. [Testing Turtle Outputs with Python](#Testing-Turtle-Outputs-with-Python) 

---

##  Installation

1. **Clone** this repository:
   ```bash
   git clone https://github.com/Ilef-mhabrech/converter_notebook.git
   cd converter_notebook

 # (Optional) Create & activate a virtual env

   python3 -m venv .venv
   source .venv/bin/activate      # macOS/Linux


# Install dependencies
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