

from __future__ import annotations

import io
import os
import warnings
from contextlib import redirect_stderr, redirect_stdout
from typing import Dict, List

import easyocr


def extract_text(image_path: str) -> List[Dict[str, float | str]]:
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        reader = easyocr.Reader(["en"], gpu=False)
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=(
                "'pin_memory' argument is set as true but no accelerator is found, "
                "then device pinned memory won't be used."
            ),
            category=UserWarning,
        )
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
