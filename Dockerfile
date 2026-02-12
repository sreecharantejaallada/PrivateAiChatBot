# Dockerfile
FROM python:3.12-slim

# System dependencies (if any)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Create non‑root user
RUN useradd -m -u 1000 appuser
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

COPY . .

USER appuser

# Runtime environment variables (can be overridden at run‑time)
ENV PYTHONUNBUFFERED=1 \
    LOG_LEVEL=INFO

CMD ["python", "-m", "app.bot"]
