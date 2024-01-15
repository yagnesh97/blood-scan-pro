from pydantic import BaseModel

from .enums import MIMETypes


class ReaderResponse(BaseModel):
    filename: str
    content_type: MIMETypes
    size: int
    content: str | None


class WebsocketResponse(BaseModel):
    status: bool
    message: str
