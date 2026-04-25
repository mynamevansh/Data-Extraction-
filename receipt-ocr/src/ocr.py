

from __future__ import annotations

import os
from typing import Dict, List

import easyocr


def extract_text(image_path: str) -> List[Dict[str, float | str]]:
    """Extract text and confidence scores from an image path."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    reader = easyocr.Reader(["en"], gpu=False)
    results = reader.readtext(image_path)

    extracted: List[Dict[str, float | str]] = []
    for _, text, confidence in results:
        extracted.append(
            {
                "text": text,
                "confidence": float(confidence),
            }
        )

    return extracted
