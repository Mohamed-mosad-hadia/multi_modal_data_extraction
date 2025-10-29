import os
import re
import json
import pdfplumber
from pathlib import Path
import logging
import argparse
from datetime import datetime


# === Logging Setup ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("extract_text")


def is_multi_column(page):
    try:
        words = page.extract_words()
        x_positions = sorted(set(w["x0"] for w in words))
        gaps = [x_positions[i] - x_positions[i - 1] for i in range(1, len(x_positions))]
        return any(g > 100 for g in gaps)
    except Exception as e:
        logger.warning(f"Multi-column detection failed: {e}")
        return False


def clean_text(text):
    if not text:
        return ""

    text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    text = re.sub(r"\n{2,}", "\n\n", text)
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)
    return text.strip()


def extract_pdf(pdf_path):
    file_result = {
        "filename": os.path.basename(pdf_path),
        "processed_at": datetime.now().isoformat(),
        "pages": [],
    }
    full_text = []

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text(layout=is_multi_column(page))
            cleaned = clean_text(text)
            file_result["pages"].append({"page": i, "text": cleaned})
            full_text.append(
                f"\n[File: {file_result['filename']} | Page {i}]\n{cleaned}"
            )

    return file_result, "\n".join(full_text)


def save_combined_outputs(all_json_data, all_text, output_folder):
    json_output = output_folder / "all_extracted_data.json"
    text_output = output_folder / "all_extracted_text.txt"

    with open(json_output, "w", encoding="utf-8") as f_json:
        json.dump(all_json_data, f_json, ensure_ascii=False, indent=2)

    with open(text_output, "w", encoding="utf-8") as f_text:
        f_text.write(all_text)

    logger.info(f"Combined JSON saved to: {json_output}")
    logger.info(f"Combined TXT saved to: {text_output}")


def main():
    parser = argparse.ArgumentParser(description="Extract text from PDFs.")
    parser.add_argument(
        "--input", type=str, default=r"D:\Data_Engineer_Task\task1_multimodal\pdfs", help="Input folder containing PDFs"
    )

    parser.add_argument("--output",type=str,default="outputs/extracted_text",help="Output folder for results",)
    args = parser.parse_args()

    input_folder = Path(args.input)
    output_folder = Path(args.output)
    output_folder.mkdir(parents=True, exist_ok=True)

    all_json_results = []
    all_combined_text = ""

    pdf_files = list(input_folder.glob("*.pdf"))
    if not pdf_files:
        logger.warning("No PDF files found in the directory.")
        return

    for pdf_path in pdf_files:
        logger.info(f"Processing: {pdf_path.name}")
        json_data, plain_text = extract_pdf(pdf_path)
        all_json_results.append(json_data)
        all_combined_text += plain_text + "\n\n"

    save_combined_outputs(all_json_results, all_combined_text, output_folder)
    logger.info("✅ All PDFs processed and combined files saved.")


if __name__ == "__main__":
    main()
