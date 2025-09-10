FROM python:3.12-slim AS dev

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps kept minimal; psycopg[binary] ships prebuilt wheels
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -f /tmp/requirements.txt

# Use a non-root user for app processes
RUN useradd -ms /bin/sh appuser && chown -R appuser /app
USER appuser

# Default stage for development
CMD ["python", "-m", "http.server", "8000"]

