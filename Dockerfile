FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (SQLite)
RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Core dependencies from pyproject.toml (runtime essentials only)
RUN pip install --no-cache-dir \
    # API Framework
    fastapi>=0.104.0 \
    uvicorn>=0.24.0 \
    pydantic>=2.0.0 \
    pydantic-settings>=2.0.0 \
    mangum \
    # HTTP & Async
    httpx \
    requests>=2.31.0 \
    aiofiles>=23.2.1 \
    # Data & Config
    pyyaml>=6.0.1 \
    tomlkit>=0.12.0 \
    python-dotenv>=1.0.0 \
    jsonschema>=4.17.0 \
    # Security & Crypto
    cryptography>=41.0.0 \
    ecdsa>=0.18.0 \
    cffi>=1.15.0 \
    # Rendering & Output
    jinja2 \
    rich>=13.0.0 \
    # System Utilities
    psutil>=7.1.3 \
    gitpython>=3.1.0

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
