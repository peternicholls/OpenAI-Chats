# Backend API Dockerfile - Multi-stage build
FROM python:3.11-slim AS builder

WORKDIR /build

# Copy the entire project for editable install
COPY pyproject.toml README.md ./
COPY chatgpt_archive/ chatgpt_archive/
COPY api/ api/

# Install dependencies
RUN pip install --no-cache-dir -e "." && \
    pip install --no-cache-dir fastapi uvicorn[standard] python-multipart pydantic

# ---
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages and source
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /build /app

# Create data directory
RUN mkdir -p /data

ENV CHATGPT_ARCHIVE_DB=/data/chats.db
ENV API_HOST=0.0.0.0
ENV API_PORT=8000

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
