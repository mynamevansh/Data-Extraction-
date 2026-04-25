

from __future__ import annotations

import io
import os
import warnings
from contextlib import redirect_stderr, redirect_stdout
from typing import Dict, List

import easyocr

from preprocess import preprocess_image


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
        preprocessed_image = preprocess_image(image_path)
        image_source = preprocessed_image if preprocessed_image is not None else image_path
        results = reader.readtext(image_source)

    extracted: List[Dict[str, float | str]] = []
    for _, text, confidence in results:
        extracted.append(
            {
                "text": text,
                "confidence": float(confidence),
            }
        )

    return extracted
