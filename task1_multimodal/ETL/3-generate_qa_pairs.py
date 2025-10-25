"""
generate_qa_pairs_nltk.py
=========================

Purpose:
--------
Generate diverse Question–Answer (Q&A) pairs from extracted medical text
Use rule-based methods or simple NLP

Inputs:
-------
- D:\Data_Engineer_Task\task1_multimodal\outputs\extracted_text\extracted_data_cleaned.json

Outputs:
--------
- qa_pairs.json → structured Q&A pairs with metadata

Requirements:
-------------
pip install nltk
"""

import json
import re
import nltk
from pathlib import Path
from typing import List, Dict
from nltk.tokenize import sent_tokenize

nltk.download("punkt")


def extract_qa_from_text(
    text: str, page: int, source_doc: str, start_id: int = 1
) -> List[Dict]:
    qa_pairs = []
    sentences = sent_tokenize(text)
    qa_id = start_id

    for sentence in sentences:
        s = sentence.strip()

        # Definition rule
        match = re.match(r"^([A-Z][a-zA-Z\s\-]+?) is (a|an|the) (.+)", s)
        if match:
            term, _, definition = match.groups()
            qa_pairs.append(
                {
                    "id": f"qa_{qa_id:03d}",
                    "question": f"What is {term.strip()}?",
                    "answer": definition.strip().rstrip("."),
                    "source_document": source_doc,
                    "page_number": page,
                    "confidence": "high",
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
                    "id": f"qa_{qa_id:03d}",
                    "question": f"What are the symptoms of {condition.strip()}?",
                    "answer": symptoms.strip(),
                    "source_document": source_doc,
                    "page_number": page,
                    "confidence": "high",
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
                    "id": f"qa_{qa_id:03d}",
                    "question": f"How is {condition.strip()} treated?",
                    "answer": treatment.strip(),
                    "source_document": source_doc,
                    "page_number": page,
                    "confidence": "high",
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
                    "id": f"qa_{qa_id:03d}",
                    "question": f"What causes {disease.strip()}?",
                    "answer": cause.strip(),
                    "source_document": source_doc,
                    "page_number": page,
                    "confidence": "high",
                    "category": "cause",
                }
            )
            qa_id += 1

    return qa_pairs


def process_documents(input_path: Path, output_path: Path, max_qas: int = 50):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    qa_list = []
    current_id = 1

    # Handle multiple documents
    for doc in data:
        filename = doc.get("filename", "unknown.pdf")
        pages = doc.get("pages", [])

        for page in pages:
            if len(qa_list) >= max_qas:
                break

            text = page.get("text", "")
            page_num = page.get("page", 0)

            qas = extract_qa_from_text(text, page_num, filename, current_id)
            for qa in qas:
                if len(qa_list) >= max_qas:
                    break
                qa_list.append(qa)
                current_id += 1

        if len(qa_list) >= max_qas:
            break

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"qa_pairs": qa_list}, f, ensure_ascii=False, indent=2)

    print(f"[✓] Generated {len(qa_list)} Q&A pairs")
    print(f"[→] Output saved to: {output_path}")


def main():
    input_json = Path(
        r"D:\Data_Engineer_Task\task1_multimodal\outputs\extracted_text\extracted_data_cleaned.json"
    )
    output_json = Path(r"D:\Data_Engineer_Task\task1_multimodal\outputs\qa_pairs.json")

    process_documents(input_json, output_json, max_qas=50)


if __name__ == "__main__":
    main()
