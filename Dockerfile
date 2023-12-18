FROM python:3.11-slim-bookworm as requirements-stage

WORKDIR /tmp

RUN pip install poetry

COPY ./backend/pyproject.toml ./backend/poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.11-slim-bookworm

RUN apt-get update \
    && apt-get install -y python3-opencv \
    && apt-get install -y tesseract-ocr

RUN apt-get autoremove -y \
    && apt-get clean -y \
    && apt-get autoclean -y

COPY --from=requirements-stage /tmp/requirements.txt /requirements.txt

COPY ./backend/pyproject.toml ./backend/gunicorn_conf.py /

COPY ./backend/app /app

RUN pip install --no-cache-dir --upgrade -r requirements.txt

CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]