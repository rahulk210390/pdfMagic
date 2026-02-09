from __future__ import annotations

from io import BytesIO
from typing import Iterable

from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from pypdf import PdfReader, PdfWriter


def _read_upload_bytes(upload: UploadFile) -> bytes:
    try:
        data = upload.file.read()
    finally: 
        upload.file.close()
    if not data:
        raise HTTPException(status_code=400, detail=f"Empty file: {upload.filename}")
    return data


def _is_pdf(data: bytes, filename: str | None) -> bool:
    if data.startswith(b"%PDF"):
        return True
    if filename:
        return filename.lower().endswith(".pdf")
    return False


def _image_bytes_to_pdf_bytes(data: bytes) -> bytes:
    try:
        image = Image.open(BytesIO(data))
    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=400, detail="Unsupported image file") from exc
    if image.mode in ("RGBA", "P", "LA"):
        image = image.convert("RGB")
    pdf_buffer = BytesIO()
    image.save(pdf_buffer, format="PDF")
    return pdf_buffer.getvalue()


def _append_pdf_bytes(writer: PdfWriter, data: bytes) -> None:
    reader = PdfReader(BytesIO(data))
    for page in reader.pages:
        writer.add_page(page)


def merge_pdfs(uploads: Iterable[UploadFile]) -> bytes:
    writer = PdfWriter()
    for upload in uploads:
        data = _read_upload_bytes(upload)
        if not _is_pdf(data, upload.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Non-PDF file provided: {upload.filename}",
            )
        _append_pdf_bytes(writer, data)
    if len(writer.pages) == 0:
        raise HTTPException(status_code=400, detail="No PDF pages to merge")
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def images_to_pdf(uploads: Iterable[UploadFile]) -> bytes:
    writer = PdfWriter()
    for upload in uploads:
        data = _read_upload_bytes(upload)
        if _is_pdf(data, upload.filename):
            raise HTTPException(
                status_code=400,
                detail=f"PDF not allowed in images-only flow: {upload.filename}",
            )
        image_pdf = _image_bytes_to_pdf_bytes(data)
        _append_pdf_bytes(writer, image_pdf)
    if len(writer.pages) == 0:
        raise HTTPException(status_code=400, detail="No images to convert")
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def merge_files(uploads: Iterable[UploadFile]) -> bytes:
    writer = PdfWriter()
    for upload in uploads:
        data = _read_upload_bytes(upload)
        if _is_pdf(data, upload.filename):
            _append_pdf_bytes(writer, data)
        else:
            image_pdf = _image_bytes_to_pdf_bytes(data)
            _append_pdf_bytes(writer, image_pdf)
    if len(writer.pages) == 0:
        raise HTTPException(status_code=400, detail="No pages to merge")
    output = BytesIO()
    writer.write(output)
    return output.getvalue()
