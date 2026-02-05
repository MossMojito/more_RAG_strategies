# ==========================================
# 🐳 Production Dockerfile
# ==========================================
FROM python:3.10-slim-buster as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt
RUN pip install --user --no-cache-dir playwright && playwright install --with-deps chromium

# ==========================================
# Final Stage
# ==========================================
FROM python:3.10-slim-buster

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright

# Update PATH
ENV PATH=/root/.local/bin:$PATH

# Copy Project Code
COPY src/ ./src/
COPY data/ ./data/
COPY app.py .

# Environment Variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="${PYTHONPATH}:/app/src"

EXPOSE 7860

CMD ["python", "app.py"]
