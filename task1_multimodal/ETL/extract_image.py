import fitz  # PyMuPDF
import json
import pytesseract
from PIL import Image
from pathlib import Path
from io import BytesIO

# Set paths
pdf_dir = Path(r"D:\Data_Engineer_Task\task1_multimodal\pdfs")
image_output_dir = Path(r"D:\Data_Engineer_Task\task1_multimodal\outputs\images")
output_json = Path(
    r"D:\Data_Engineer_Task\task1_multimodal\outputs\image_text_pairs.json"
)
image_output_dir.mkdir(parents=True, exist_ok=True)

# Optional: Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


results = []
pair_id = 1

for pdf_file in pdf_dir.glob("*.pdf"):
    doc = fitz.open(pdf_file)
    for page_num, page in enumerate(doc):
        images = page.get_images(full=True)
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_filename = (
                f"{pdf_file.stem}_p{page_num+1}_img{img_index+1}.{image_ext}"
            )
            image_path = image_output_dir / image_filename

            # Save image
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)

            # OCR
            img = Image.open(BytesIO(image_bytes))
            ocr_text = pytesseract.image_to_string(img).strip()

            # Add to results
            results.append(
                {
                    "pair_id": f"img_{pair_id:03d}",
                    "image_path": str(image_path.relative_to(image_output_dir.parent)),
                    "image_type": "diagram",  # default guess
                    "caption_short": (
                        ocr_text.split("\n")[0][:80] if ocr_text else "No text detected"
                    ),
                    "caption_detailed": (
                        ocr_text if ocr_text else "No description available"
                    ),
                    "source_document": pdf_file.name,
                    "page_number": page_num + 1,
                }
            )
            pair_id += 1

# Save as JSON
with open(output_json, "w", encoding="utf-8") as f:
    json.dump({"image_text_pairs": results}, f, indent=2, ensure_ascii=False)

print(f"[✓] Extracted {len(results)} image-text pairs.")
