FROM python:3.11-slim-bookworm

RUN apt-get update \
    && apt-get install -y python3-opencv \
    && apt-get install -y tesseract-ocr

RUN apt-get autoremove -y \
    && apt-get clean -y \
    && apt-get autoclean -y

WORKDIR /home

COPY ./backend/pyproject.toml ./backend/gunicorn_conf.py ./backend/requirements.txt ./

COPY ./backend/app ./app

RUN pip install --no-cache-dir --upgrade -r requirements.txt

CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]