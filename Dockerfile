FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY scripts ./scripts

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

ENV PORT=8501

CMD ["sh", "-c", "streamlit run scripts/web_app.py --server.address 0.0.0.0 --server.port ${PORT}"]
