# services/voice_cloner/Dockerfile
FROM python:3.11-slim

# Install system dependencies (libsndfile for audio I/O, ffmpeg)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency definition
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and default character voice samples
COPY app.py .
COPY voices/ ./voices/

ENV PORT=8004
ENV PYTHONUNBUFFERED=1

EXPOSE 8004

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8004/health || exit 1

# Start FastAPI Voice Cloning server
CMD ["python", "app.py"]
