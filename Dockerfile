FROM python:3.12-slim AS dev

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps for ChromaDB compilation
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -f /tmp/requirements.txt

# Use a non-root user for app processes
RUN useradd -ms /bin/sh appuser && chown -R appuser /app
USER appuser

# Default stage for development
CMD ["python", "-m", "http.server", "8000"]

