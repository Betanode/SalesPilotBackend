import fitz  # pymupdf
import pytesseract
from PIL import Image
import re


def extract_text_layer(page) -> str:
    """Extract selectable text"""
    return page.get_text() or ""


def extract_image_ocr(page) -> str:
    """Extract text from images using OCR"""
    try:
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        return pytesseract.image_to_string(img)
    except Exception:
        return ""


def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def merge_text(text_layer: str, ocr_text: str) -> str:
    """
    Smart merge:
    - If OCR adds new info → include
    - Avoid duplicate spam
    """

    if not ocr_text.strip():
        return text_layer

    # simple heuristic: add only if significantly different
    if len(ocr_text) > 0.3 * len(text_layer):
        return text_layer + "\n" + ocr_text

    return text_layer


def extract_text(file_path: str) -> str:
    doc = fitz.open(file_path)

    final_text = []

    for page in doc:
        text_layer = extract_text_layer(page)
        ocr_text = extract_image_ocr(page)

        merged = merge_text(text_layer, ocr_text)
        final_text.append(merged)

    doc.close()

    return clean_text("\n".join(final_text))
