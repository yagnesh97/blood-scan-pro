from io import BytesIO
from typing import NoReturn

import google.generativeai as genai
import pdfplumber
from fastapi import APIRouter, HTTPException, UploadFile, WebSocket, status
from fastapi.security import HTTPBearer
from PIL import Image

from app.config import settings
from app.static_values import PROMPT_TEXT

from .enums import MIMETypes
from .models import ReaderResponse, WebsocketResponse
from .utils import get_ai_response

router = APIRouter()
security = HTTPBearer()


@router.post("", response_model=ReaderResponse)
async def upload_pdf_file(file: UploadFile) -> ReaderResponse:
    if file.content_type not in MIMETypes.types():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document type.",
        )

    contents = []

    if file.content_type == MIMETypes.PDF.value:
        with pdfplumber.open(file.file) as pdf:
            for page in pdf.pages:
                image = page.to_image()
                image_bytes_io = BytesIO()
                image.save(image_bytes_io, format="PNG")
                contents.append(Image.open(image_bytes_io))
    elif file.content_type in [MIMETypes.JPEG.value, MIMETypes.PNG.value]:
        contents.append(Image.open(file.file))

    contents.append(
        "You are an expert at explaining the blood report. "
        "Explain the report in a few sentences at third-level grade"
        "based on this image(s)."
    )

    genai.configure(api_key=settings.genai_key)
    model = genai.GenerativeModel(model_name=settings.genai_model_vision)
    result = model.generate_content(contents=contents)

    reader_response = ReaderResponse(
        filename=file.filename,
        content_type=file.content_type,
        size=file.size,
        content=result.text,
    )
    return reader_response.model_dump()


@router.websocket(path="/ws")
async def websocket_endpoint(websocket: WebSocket) -> NoReturn:
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        text = data["text"]
        filename = data.get("filename")

        file = None
        if filename:
            file = await websocket.receive_bytes()

        if not websocket.session.get("file") and not file:
            await websocket.send_json(
                WebsocketResponse(
                    status=False,
                    message="Image or PDF file required to interpret the report.",
                ).model_dump()
            )

        if file:
            websocket.session["file"] = file

        contents = [Image.open(BytesIO(websocket.session["file"]))]
        contents.append(text or PROMPT_TEXT)
        async for chunk in get_ai_response(contents=contents):
            await websocket.send_json(
                WebsocketResponse(status=True, message=chunk).model_dump()
            )
