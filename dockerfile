# --- Stage 1: The Builder ---
# Install dependencies and build tools
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies for Python packages (e.g., lxml, playwright)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libxml2-dev \
    libxslt-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt to leverage Docker's build cache
COPY requirements.txt .

# Install Python dependencies and Playwright browsers
RUN pip install --no-cache-dir -r requirements.txt \
    && playwright install --with-deps chromium

# --- Stage 2: The Final Production Image ---
FROM python:3.11-slim

WORKDIR /app

# Install minimal runtime dependencies for lxml and playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 \
    libxslt1.1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
# Corrected Playwright cache path
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright

# Copy application code
COPY . .

# Create and set permissions for cache directory
RUN mkdir -p /app/cache && chown -R 1001:1001 /app/cache

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=10000

# Expose the port Render expects (defaults to 10000)
EXPOSE 10000

# Run as non-root user for security
USER 1001

# Run gunicorn with optimized settings for Render
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:${PORT}", "--workers", "2", "--threads", "4", "--timeout", "120"]