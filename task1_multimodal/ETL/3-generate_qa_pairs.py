"""
generate_qa_pairs_nltk.py
=========================

Purpose:
--------
Generate diverse Question–Answer (Q&A) pairs from extracted medical text
Use rule-based methods or simple NLP
"""

import json
import re
from pathlib import Path
from typing import List, Dict
import logging
import argparse
from datetime import datetime
import sqlite3


# Simple sentence tokenizer fallback to avoid external nltk dependency.
# Uses a basic regex to split on sentence-ending punctuation followed by whitespace.
def sent_tokenize(text: str) -> List[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s for s in sentences if s]
    nltk.download("punkt")


# === Logging Setup ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("qa_to_sqlite")


def extract_qa_from_text(
    text: str, page: int, source_doc: str, start_id: int = 1
) -> List[Dict]:
    """Extract Q&A pairs from text using simple rules."""
    qa_pairs = []
    sentences = sent_tokenize(text)
    qa_id = start_id

    for sentence in sentences:
        s = sentence.strip()
        timestamp = datetime.now().isoformat()

        # Definition rule
        match = re.match(r"^([A-Z][a-zA-Z\s\-]+?) is (a|an|the) (.+)", s)
        if match:
            term, _, definition = match.groups()
            qa_pairs.append(
                {
                    "id": f"qa_{qa_id:04d}",
                    "question": f"What is {term.strip()}?",
                    "answer": definition.strip().rstrip("."),
                    "source_document": source_doc,
                    "page_number": page,
                    "created_at": timestamp,
                    "category": "definition",
                }
            )
            qa_id += 1

        # Symptoms rule
        match = re.match(r"^Symptoms of (.+?) include (.+?)\.", s)
        if match:
            condition, symptoms = match.groups()
            qa_pairs.append(
                {
                    "id": f"qa_{qa_id:04d}",
                    "question": f"What are the symptoms of {condition.strip()}?",
                    "answer": symptoms.strip(),
                    "source_document": source_doc,
                    "page_number": page,
                    "created_at": timestamp,
                    "category": "symptoms",
                }
            )
            qa_id += 1

        # Treatment rule
        match = re.match(r"^Treatment of (.+?) includes (.+?)\.", s)
        if match:
            condition, treatment = match.groups()
            qa_pairs.append(
                {
                    "id": f"qa_{qa_id:04d}",
                    "question": f"How is {condition.strip()} treated?",
                    "answer": treatment.strip(),
                    "source_document": source_doc,
                    "page_number": page,
                    "created_at": timestamp,
                    "category": "treatment",
                }
            )
            qa_id += 1

        # Cause rule
        match = re.match(r"^(.+?) is caused by (.+?)\.", s)
        if match:
            disease, cause = match.groups()
            qa_pairs.append(
                {
                    "id": f"qa_{qa_id:04d}",
                    "question": f"What causes {disease.strip()}?",
                    "answer": cause.strip(),
                    "source_document": source_doc,
                    "page_number": page,
                    "created_at": timestamp,
                    "category": "cause",
                }
            )
            qa_id += 1

    return qa_pairs


def save_to_sqlite(db_path: Path, qa_pairs: List[Dict]):
    """Save extracted Q&A pairs to SQLite database."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS qa_pairs (
            id TEXT PRIMARY KEY,
            question TEXT,
            answer TEXT,
            source_document TEXT,
            page_number INTEGER,
            created_at TEXT,
            category TEXT
        )
    """
    )

    for qa in qa_pairs:
        cur.execute(
            """
            INSERT OR REPLACE INTO qa_pairs VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                qa["id"],
                qa["question"],
                qa["answer"],
                qa["source_document"],
                qa["page_number"],
                qa["created_at"],
                qa["category"],
            ),
        )

    conn.commit()
    conn.close()
    logger.info(f"✅ Saved {len(qa_pairs)} Q&A pairs to database: {db_path}")


def process_documents(input_path: Path, db_path: Path, max_qas: int = 100):
    """Load cleaned data, extract Q&A pairs, and save to SQLite."""
    logger.info(f"📥 Loading cleaned data from: {input_path}")
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_qas = []
    current_id = 1

    for doc in data:
        filename = doc.get("filename", "unknown.pdf")
        pages = doc.get("pages", [])

        for page in pages:
            if len(all_qas) >= max_qas:
                break
            text = page.get("text", "")
            page_num = page.get("page", 0)
            qas = extract_qa_from_text(text, page_num, filename, current_id)
            all_qas.extend(qas)
            current_id += len(qas)

        if len(all_qas) >= max_qas:
            break

    save_to_sqlite(db_path, all_qas)
    logger.info(f"🏁 Q&A extraction completed. Total pairs: {len(all_qas)}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate Q&A pairs and store in SQLite DB."
    )
    parser.add_argument(
        "--input",
        type=str,
        default="outputs/extracted_text/extracted_data_cleaned.json",
        help="Path to input cleaned JSON file",
    )
    parser.add_argument(
        "--db",
        type=str,
        default="outputs/qa_data.db",
        help="Path to SQLite database output file",
    )
    parser.add_argument(
        "--limit", type=int, default=100, help="Maximum number of Q&A pairs to generate"
    )
    args = parser.parse_args()

    input_json = Path(args.input)
    db_path = Path(args.db)

    process_documents(input_json, db_path, max_qas=args.limit)


if __name__ == "__main__":
    main()
