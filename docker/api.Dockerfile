# Backend API Dockerfile - Multi-stage build
# Stage 1: Install all dependencies
FROM python:3.11-slim AS builder

WORKDIR /build

# Copy source needed for installation
COPY pyproject.toml README.md ./
COPY chatgpt_archive/ chatgpt_archive/
COPY api/ api/

# Install root chatgpt_archive package first (makes it findable for api/ install),
# then install the API package which reads its pyproject.toml for all deps.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir ".[semantic]" && \
    pip install --no-cache-dir "./api/"

# ---
# Stage 2: Lean runtime image — no build tools, no test files
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder (excludes build tools — those weren't in
# python:3.11-slim to begin with, so this is already lean)
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy only the source code needed at runtime (tests excluded via .dockerignore)
COPY chatgpt_archive/ chatgpt_archive/
COPY api/ api/

# Create data directory for SQLite database
RUN mkdir -p /data

ENV CHATGPT_ARCHIVE_DB=/data/chats.db
ENV API_HOST=0.0.0.0
ENV API_PORT=8000

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
