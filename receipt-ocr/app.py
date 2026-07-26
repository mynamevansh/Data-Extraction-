from __future__ import annotations

from importlib import import_module
import os
import shutil
import sys
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(str(Path(__file__).parent))

process_image = import_module("src.main").process_image

app = FastAPI(
    title="Receipt OCR API",
    description="API to extract structured store name, date, and total from receipt images using EasyOCR",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"status": "running", "message": "Receipt OCR API is active"}


@app.post("/extract")
async def extract_receipt(file: UploadFile = File(...)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Only JPG, JPEG, and PNG are allowed.",
        )

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        result = process_image(tmp_path)

        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except OSError:
            pass

        if result is None:
            raise HTTPException(
                status_code=400,
                detail="Failed to process image: no text could be extracted or recognized.",
            )

        return result

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error processing the receipt: {error}",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
