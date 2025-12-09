# STAGE 1: Builder
FROM python:3.10-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# 1. Install PyTorch CPU specifically (Explicit URL ensures success)
RUN pip install --user --no-cache-dir torch==2.1.2 --index-url https://download.pytorch.org/whl/cpu

# 2. Install the rest of the dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# STAGE 2: Runtime
FROM python:3.10-slim as runtime

WORKDIR /app

# Create a non-root user for security
RUN useradd -m -u 1000 appuser

# Copy installed packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY ./app ./app

# Set environment variables
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create the cache directory and ensure ownership
# (This fixes the [Errno 13] Permission denied error)
RUN mkdir -p /home/appuser/huggingface && chown -R appuser:appuser /home/appuser/huggingface

# Switch to non-root user
USER appuser

# Expose the port
EXPOSE 8000

# Run command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]