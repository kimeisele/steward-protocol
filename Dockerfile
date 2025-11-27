FROM python:3.9-slim

WORKDIR /app

# Install system dependencies (SQLite)
RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Core API dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pydantic \
    mangum \
    httpx \
    pyyaml \
    requests \
    python-dotenv \
    cryptography

# Copy project files FIRST (as root)
COPY . .

# Create a non-root user and give ownership of /app
RUN useradd -m -u 1000 steward && \
    chown -R steward:steward /app

# Switch to non-root user
USER steward

# Expose port (Cloud Run default)
ENV PORT=8080
ENV GOVERNANCE_MODE=SERVERLESS_BYPASS
ENV ENV=production
ENV PYTHONPATH=/app:$PYTHONPATH

# Run the application
CMD ["uvicorn", "gateway.api:app", "--host", "0.0.0.0", "--port", "8080"]
