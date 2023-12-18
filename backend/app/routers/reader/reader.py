import google.generativeai as palm
import pdfplumber
from fastapi import APIRouter, HTTPException, UploadFile, status
from fastapi.security import HTTPBearer

from app.config import settings

from .enums import MIMETypes
from .models import ReaderResponse
from .utils import image_to_text, process_content

router = APIRouter()
security = HTTPBearer()


@router.post("")
async def upload_pdf_file(file: UploadFile) -> ReaderResponse:
    if file.content_type not in MIMETypes.types():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document type.",
        )

    content = ""
    binary_data = file.file.read()
    if file.content_type == MIMETypes.PDF.value:
        with pdfplumber.open(binary_data) as pdf:
            _ = map(lambda page: page.extract_text(), pdf.pages)
            content = process_content(content="\n".join(_))
    elif file.content_type in [MIMETypes.JPEG.value, MIMETypes.PNG.value]:
        text = image_to_text(binary_data)
        content = process_content(content=text)

    prompt = f"""
    You are an expert at explaining the blood report.

    Input: {content}

    Output: Explain the report in a few sentences at third-level grade.
    """

    palm.configure(api_key=settings.palm_key)
    completion = palm.generate_text(
        model=settings.palm_model,
        prompt=prompt,
        temperature=0,
        # The maximum length of the response
        max_output_tokens=800,
        safety_settings=[
            {
                "category": palm.types.HarmCategory.HARM_CATEGORY_MEDICAL,
                "threshold": palm.types.HarmBlockThreshold.BLOCK_NONE,
            }
        ],
    )

    reader_response = ReaderResponse(
        filename=file.filename,
        content_type=file.content_type,
        size=file.size,
        content=completion.result,
    )
    return reader_response.model_dump()
