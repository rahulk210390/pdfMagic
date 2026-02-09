from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .pdf_utils import images_to_pdf, merge_files, merge_pdfs

app = FastAPI(title="PdfMagic API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.post("/merge-pdf")
async def merge_pdf(files: list[UploadFile] = File(...)) -> StreamingResponse:
    output_bytes = merge_pdfs(files)
    return StreamingResponse(
        iter([output_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=merged.pdf"},
    )


@app.post("/images-to-pdf")
async def images_to_pdf_endpoint(
    files: list[UploadFile] = File(...)
) -> StreamingResponse:
    output_bytes = images_to_pdf(files)
    return StreamingResponse(
        iter([output_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=images.pdf"},
    )


@app.post("/merge-files")
async def merge_files_endpoint(
    files: list[UploadFile] = File(...)
) -> StreamingResponse:
    output_bytes = merge_files(files)
    return StreamingResponse(
        iter([output_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=merged-files.pdf"},
    )
