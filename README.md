# converter_notebook

# Batch Conversion of Master’s Program Outlines

This directory contains the `batch_masters.py` script and output folders to bulk-convert Master’s program outlines (PDF) into **CSV** and **Turtle (TTL)** files.

---

##  Processing Steps

1. **Download PDFs**  
   Retrieve all Master’s program outlines in PDF format from the university website.

2. **Convert PDF → Excel**  
   Use  **I Love PDF** to transform each PDF into an Excel file (`.xlsx`).

3. **Run the Script**  
   From the root of this directory, execute:
   python3 batch_masters.py

Note: Install dependencies before running:
  pip install pandas openpyxl

## Script Overview (batch_masters.py)

**Initialization** 

Creates four output folders (if they don’t already exist):
csv/, ttl/, csv_metrics/, ttl_metrics/.

Defines RDF prefixes for the Turtle files.

**Data Extraction**

Iterates through every sheet in each *.xlsx file.

Detects sections containing “Objectifs” (Objectives) to locate course units (UEs).

For each UE, collects:

Metadata:
key (identifier), title, level, semester,
parcours (track), objective, content.

Metrics:
volume (hours) and ects (credits).

**File Generation**

Metadata CSV → csv/<basename>.csv

Metadata Turtle → ttl/<basename>.ttl

Metrics CSV → csv_metrics/<basename>_metrics.csv

Metrics Turtle → ttl_metrics/<basename>_metrics.ttl



Each TTL file includes RDF prefix declarations and triples (ns1:…) describing the course units and their credits.


## results 

  📂 Output Structure

├── batch_masters.py
├── csv/             # Metadata CSV files
├── ttl/             # Metadata Turtle files
├── csv_metrics/     # Volume & ECTS CSV files
└── ttl_metrics/     # Volume & ECTS Turtle files