from typing import Any, AsyncGenerator

import google.generativeai as genai

from app.config import settings


async def get_ai_response(contents: list[Any]) -> AsyncGenerator[str, None]:
    """Gemini AI Response

    Args:
        contents (list[Any]): String and image contents.

    Returns:
        AsyncGenerator[str, None]: Generator function.

    Yields:
        Iterator[AsyncGenerator[str, None]]: Gemini AI Response.
    """
    genai.configure(api_key=settings.genai_key)
    model = genai.GenerativeModel(model_name=settings.genai_model_vision)
    result = model.generate_content(contents=contents, stream=True)

    for chunk in result:
        yield chunk.text
