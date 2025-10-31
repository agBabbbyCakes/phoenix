FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml uv.lock requirements.txt* /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY app /app/app
COPY templates /app/templates
COPY static /app/static
# Copy src directory if it exists (optional for Ethereum realtime)
# Note: This will fail silently if src doesn't exist, but the import is optional
COPY src /app/src

EXPOSE 8000

ENV FORCE_SAMPLE=1 \
    CLEAN_UI=1

# Use shell-form to allow env var expansion for PORT (required by platforms like Railway)
CMD sh -c 'uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}'


