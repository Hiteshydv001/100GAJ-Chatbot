# Dockerfile for the Flask Application

# --- Stage 1: The Builder ---
# This stage installs dependencies, including build tools like gcc,
# and upgrades pip/setuptools to prevent installation errors.
FROM python:3.11-slim as builder

WORKDIR /app

# First, upgrade pip and setuptools to ensure the build environment is modern.
RUN pip install --upgrade pip setuptools wheel

# Install system dependencies needed for building certain Python packages
RUN apt-get update && apt-get install -y --no-install-recommends gcc && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file to leverage Docker's build cache
COPY requirements.txt .

# Install Python dependencies using the now-upgraded tools
RUN pip install --no-cache-dir -r requirements.txt


# --- Stage 2: The Final Production Image ---
# This stage creates the final, lean image without the build tools.
FROM python:3.11-slim

WORKDIR /app

# Copy the installed Python packages from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy your entire application code into the image
COPY . .

# Set environment variable for unbuffered logging
ENV PYTHONUNBUFFERED=1

# Expose the port Render expects.
# The actual port number will be provided by the $PORT environment variable at runtime.
EXPOSE 10000

# Run the app as a non-root user for better security.
# Render's default non-root user has UID 1001.
USER 1001

# The command to run your application.
# This uses Gunicorn, points to main:app, uses the dynamic $PORT,
CMD gunicorn main:app --bind 0.0.0.0:${PORT} --timeout 180