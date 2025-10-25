import json
import re
from pathlib import Path
from typing import Dict, Any, List


def detect_structure(text: str) -> Dict[str, str]:
    """Detect chapter, section, subsection titles from text."""
    chapter = None
    section = None
    subsection = None

    lines = text.split("\n")
    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Chapter (e.g. "Chapter 1", "CHAPTER 2:")
        if re.match(r"(?i)^chapter\s+\d+[:.\s-]*", line):
            chapter = line
            section = None
            subsection = None
            continue

        # Section (e.g. "Section 2.1 Something", "Section 1.3")
        if re.match(r"(?i)^section\s+\d+(\.\d+)*[:.\s-]*", line):
            section = line
            subsection = None
            continue

        # Subsection (e.g. "2.1.1 Introduction", "3.2.4")
        if re.match(r"^\d+(\.\d+)+\s+.+", line):
            subsection = line
            continue

    return {"chapter": chapter, "section": section, "subsection": subsection}


def annotate_structure(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Attach chapter/section info to each page."""
    current_chapter = None
    current_section = None
    current_subsection = None

    for page in doc.get("pages", []):
        text = page.get("text", "")
        structure = detect_structure(text)

        if structure["chapter"]:
            current_chapter = structure["chapter"]
        if structure["section"]:
            current_section = structure["section"]
        if structure["subsection"]:
            current_subsection = structure["subsection"]

        page["chapter"] = current_chapter
        page["section"] = current_section
        page["subsection"] = current_subsection

    return doc


def main():
    input_path = Path(
        r"D:\Data_Engineer_Task\task1_multimodal\outputs\extracted_text\all_extracted_data.json"
    )
    output_path = Path(
        r"D:\Data_Engineer_Task\task1_multimodal\outputs\extracted_text\extracted_data_cleaned.json"
    )

    with open(input_path, "r", encoding="utf-8") as f:
        docs: List[Dict[str, Any]] = json.load(f)

    structured_docs = [annotate_structure(doc) for doc in docs]

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(structured_docs, f, ensure_ascii=False, indent=2)

    print(f"[✓] Structured JSON saved to: {output_path}")


if __name__ == "__main__":
    main()
