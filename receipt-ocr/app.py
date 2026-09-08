from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from src.excel_generator import generate_full_workbook
from src.main import process_image
from src.pdf import extract_pdf
from src.pdf_structure import extract_pdf_structure

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
    if suffix not in {".jpg", ".jpeg", ".png", ".pdf"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Only JPG, JPEG, PNG, and PDF are allowed.",
        )

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        result = {"pages": extract_pdf(tmp_path)} if suffix == ".pdf" else process_image(tmp_path)

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


@app.post("/convert-pdf-to-excel")
async def convert_pdf_to_excel(
    background_tasks: BackgroundTasks, file: UploadFile = File(...)
):
    """Convert an uploaded PDF into a downloadable editable Excel workbook."""
    original_filename = file.filename or "uploaded.pdf"
    suffix = Path(original_filename).suffix.lower()
    if suffix != ".pdf":
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported.")

    temporary_directory = tempfile.mkdtemp(prefix="receipt-pdf-")
    input_path = Path(temporary_directory) / "input.pdf"
    output_path = Path(temporary_directory) / "converted.xlsx"
    try:
        with input_path.open("wb") as temporary_file:
            shutil.copyfileobj(file.file, temporary_file)

        structure = extract_pdf_structure(str(input_path))
        result = generate_full_workbook(structure, output_path)
        if result["failed_pages"]:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "One or more PDF pages could not be converted.",
                    "failed_pages": result["failed_pages"],
                },
            )

        if result["unsupported_fields"]:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "The PDF contains unsupported form fields.",
                    "unsupported_fields": result["unsupported_fields"],
                },
            )

        background_tasks.add_task(shutil.rmtree, temporary_directory, ignore_errors=True)
        download_name = f"{Path(original_filename).stem}_converted.xlsx"
        return FileResponse(
            path=output_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=download_name,
            background=background_tasks,
        )
    except HTTPException:
        shutil.rmtree(temporary_directory, ignore_errors=True)
        raise
    except Exception as error:
        shutil.rmtree(temporary_directory, ignore_errors=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error converting the PDF: {error}",
        ) from error


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
