"""
OCR Bill Scanner module – extract bill details using EasyOCR.
"""

import os
import re
from datetime import datetime
from typing import Optional
from PIL import Image
import easyocr
from database import get_session, Bill

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Lazy-load OCR reader to avoid slow startup
_reader: Optional[easyocr.Reader] = None


def get_ocr_reader() -> easyocr.Reader:
    """Initialize EasyOCR reader once (English)."""
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(["en"], gpu=False)
    return _reader


class BillScanner:
    """Extracts structured data from bill images using OCR."""

    DATE_PATTERNS = [
        r"(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4})",
        r"(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})",
    ]

    AMOUNT_PATTERNS = [
        r"(?:total|grand\s*total|amount|payable|net)\s*[:\-]?\s*(?:₹|rs\.?|inr)?\s*([\d,]+\.?\d*)",
        r"(?:₹|rs\.?|inr)\s*([\d,]+\.?\d*)",
        r"([\d,]+\.\d{2})\s*(?:total|payable)?",
    ]

    def __init__(self, user_id: int):
        self.user_id = user_id

    def save_upload(self, uploaded_file) -> str:
        """Save uploaded image and return file path."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = uploaded_file.name.split(".")[-1] if "." in uploaded_file.name else "png"
        filename = f"bill_{self.user_id}_{timestamp}.{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        image = Image.open(uploaded_file)
        image.save(filepath)
        return filepath

    def extract_text(self, image_path: str) -> list[str]:
        """Run OCR and return list of detected text lines."""
        reader = get_ocr_reader()
        results = reader.readtext(image_path, detail=0)
        return [line.strip() for line in results if line.strip()]

    def parse_bill(self, lines: list[str]) -> dict:
        """Parse OCR text into structured bill fields."""
        full_text = " ".join(lines).lower()
        full_text_orig = " ".join(lines)

        store_name = lines[0] if lines else "Unknown Store"

        bill_date = None
        for pattern in self.DATE_PATTERNS:
            match = re.search(pattern, full_text_orig, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%d/%m/%y", "%d-%m-%y"):
                    try:
                        bill_date = datetime.strptime(date_str, fmt).date()
                        break
                    except ValueError:
                        continue
                if bill_date:
                    break

        total_amount = 0.0
        for pattern in self.AMOUNT_PATTERNS:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            if matches:
                amounts = []
                for m in matches:
                    try:
                        amounts.append(float(m.replace(",", "")))
                    except ValueError:
                        continue
                if amounts:
                    total_amount = max(amounts)
                    break

        items = []
        item_pattern = re.compile(
            r"([A-Za-z][A-Za-z0-9\s\-]{2,30})\s+(?:₹|rs\.?)?\s*([\d,]+\.?\d*)",
            re.IGNORECASE,
        )
        for line in lines[1:]:
            match = item_pattern.search(line)
            if match:
                name, price = match.group(1).strip(), match.group(2)
                if float(price.replace(",", "")) < total_amount:
                    items.append(f"{name}: ₹{price}")

        return {
            "store_name": store_name[:150],
            "bill_date": bill_date,
            "total_amount": round(total_amount, 2),
            "items": "\n".join(items[:10]) if items else "No items detected",
            "raw_text": "\n".join(lines),
        }

    def scan_bill(self, uploaded_file) -> dict:
        """Full pipeline: save image, OCR, parse."""
        filepath = self.save_upload(uploaded_file)
        lines = self.extract_text(filepath)
        parsed = self.parse_bill(lines)
        parsed["image_path"] = filepath
        return parsed

    def save_bill(
        self,
        store_name: str,
        bill_date,
        total_amount: float,
        items: str,
        image_path: str,
    ) -> tuple[bool, str]:
        """Persist scanned bill to database."""
        session = get_session()
        try:
            bill = Bill(
                user_id=self.user_id,
                store_name=store_name,
                bill_date=bill_date,
                total_amount=total_amount,
                items=items,
                image_path=image_path,
            )
            session.add(bill)
            session.commit()
            return True, "Bill saved successfully."
        except Exception as exc:
            session.rollback()
            return False, f"Failed to save bill: {exc}"
        finally:
            session.close()
