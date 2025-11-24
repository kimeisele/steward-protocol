# Serverless Deployment Guide (GAD-X-FINALE)

This guide documents how to deploy the **Steward Protocol Gateway** (`gateway/api.py`) to a serverless platform. This architecture achieves the "fucking cheap" goal by scaling to zero when not in use.

## Architecture

-   **Runtime**: Python 3.9+
-   **Framework**: FastAPI + Uvicorn
-   **State**: Stateless Compute (Kernel re-hydrates from DB or starts fresh)
-   **Storage**: SQLite (can be replaced with S3/Cloud SQL for persistence across cold starts)

## Option 1: Google Cloud Run (Recommended)

Cloud Run allows you to run stateless containers that are invocable via HTTP requests.

### 1. Dockerfile

Create a `Dockerfile` in the project root:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y sqlite3

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install fastapi uvicorn pydantic

# Expose port
ENV PORT=8080

# Run the application
CMD ["uvicorn", "gateway.api:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 2. Deploy

```bash
# Build and Deploy
gcloud run deploy steward-gateway \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars API_KEY=your-secret-key
```

### 3. Cost Optimization

-   **Min Instances**: Set to `0` (Scale to zero).
-   **CPU Allocation**: "CPU is only allocated during request processing".
-   **Result**: You pay **$0.00** when no one is chatting.

## Option 2: AWS Lambda (via Mangum)

### 1. Adapter

Install `mangum` to adapt FastAPI for Lambda:
`pip install mangum`

Add to `gateway/api.py`:
```python
from mangum import Mangum
handler = Mangum(app)
```

### 2. serverless.yml

```yaml
service: steward-gateway

provider:
  name: aws
  runtime: python3.9
  environment:
    API_KEY: ${env:API_KEY}

functions:
  api:
    handler: gateway.api.handler
    events:
      - http:
          path: /{proxy+}
          method: any
```

## Verification

Once deployed, test with `curl`:

```bash
curl -X POST https://your-service-url/v1/chat \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-secret-key" \
  -d '{"user_id": "hil_operator_01", "command": "briefing"}'
```

**Expected Output:**
```json
{
  "status": "success",
  "summary": "🤖 HIL ASSISTANT: STRATEGIC BRIEFING...",
  "ledger_hash": "a1b2c3d4...",
  "task_id": "TASK-123456"
}
```
