FROM python:3.9

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

EXPOSE 80

COPY main.py ./

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]