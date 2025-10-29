# Multi-Modal Medical PDF Extraction

## Project Description

Transform scanned medical PDFs into structured datasets for downstream analytics, retrieval-augmented generation, and conversational agents. This pipeline ingests raw documents, recovers text and layout cues, and emits:

- Normalized text suitable for search and indexing
- Rule-generated Q&A pairs grounded in document content
- Simulated multi-turn dialogues capturing clinician–patient style exchanges
- Aligned image–text datasets for grounding multimodal models

The stack is optimized for developers shipping data products that blend OCR, NLP, and lightweight heuristics.

## How to run 4 scripts 
- navigate to ETL folder 📂  then   run  [ ./run_etl.sh ] 


## Interesting Techniques Used

- **Rule-based Q&A generation with NLTK** for deterministic question construction and answer span alignment.
- **Multi-column detection via pdfplumber** to maintain reading order in complex medical brochures and lab reports.
- **Simulated dialogue construction** that stitches Q&A and metadata into coherent multi-turn transcripts.
- **Simple structure detection through regex** to flag headings, bullet lists, and caption blocks without heavyweight parsers.
- **OCR powered by Tesseract** to recover text from scanned forms, handwritten notes, and embedded figures.
- _(Optional)_ **`pipreqs`-driven dependency discovery** keeping `requirements.txt` lean and reproducible.

## Not-so-obvious Tools & Libraries

- [`pdfplumber`](https://github.com/jsvine/pdfplumber) for layout-aware PDF text extraction, column segmentation, and annotation parsing.
- [`pytesseract`](https://github.com/madmaze/pytesseract) for delegating OCR to the Tesseract engine when vector text is unavailable.
- [`nltk`](https://www.nltk.org/) enabling rule-based sentence tokenization, POS tagging, and templated Q&A generation.
- [`PyMuPDF`](https://pymupdf.readthedocs.io/) (a.k.a. `fitz`) to extract page-level images, vector graphics, and metadata used in multimodal datasets.
- [`pipreqs`](https://github.com/bndr/pipreqs) to synthesize a minimal `requirements.txt` directly from import usage.

## Project Structure

```
.
├── ETL/                       # Scripts for extracting & cleaning text from PDFs
├── outputs/                   # Generated JSON, text files, images
├── pdfs/                      # Source medical PDF documents
├── images/                    # Extracted figures/diagrams from documents
├── requirements.txt           # Minimal set of required libraries
└── README.md
```

The `ETL/` directory handles raw PDF processing, contains logic for generating Q&A pairs and conversational datasets. All results are stored in `outputs/`.

## Features

- Image caption extraction combines **`pytesseract` OCR** with regular-expression based caption matching for high-recall figure summaries.
- Configurable pipelines let you toggle OCR, layout analysis, and dialogue generation per document type.
- Outputs standardized to JSON for seamless ingestion into warehouses or LLM fine-tuning workflows.

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Place source PDFs under `pdfs/` and run the ETL stage to generate clean text and layout metadata.
3. Execute NLP scripts to derive Q&A datasets and synthetic dialogues.
4. Inspect `outputs/` for JSONL artifacts, extracted images, and intermediate logs ready for integration into your data stack.

## Contributing

Contributions are welcome. Please open an issue describing your enhancement or bug fix, and include sample documents when possible so we can reproduce edge cases involving OCR or complex layouts.
