FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git \
    && rm -rf /var/lib/apt/lists/*

# FIX #5: set cache dir so models persist in the image layer and aren't
# re-downloaded on every Railway deploy
ENV TRANSFORMERS_CACHE=/app/.cache \
    HF_HOME=/app/.cache \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy and install Python deps first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download model weights into the image so cold starts are instant
RUN python - <<'EOF'
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModel
MODEL = "microsoft/codebert-base"
AutoTokenizer.from_pretrained(MODEL)
AutoModelForSequenceClassification.from_pretrained(MODEL, num_labels=4)
AutoModel.from_pretrained(MODEL)
EOF

# Copy app
COPY . .

# Railway assigns PORT dynamically — default 8080 if unset
EXPOSE 8080

# FIX #6: use $PORT so Railway can inject its own port at runtime
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:${PORT:-8080} --workers 1 --timeout 120"]
