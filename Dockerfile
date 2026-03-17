FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY scripts ./scripts

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

ENV PORT=8000

CMD ["sh", "-c", "uvicorn app.web_service:app --host 0.0.0.0 --port ${PORT}"]
