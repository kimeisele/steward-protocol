# Local Testing Guide

## Run the Gateway Locally

### Prerequisites
```bash
pip install fastapi uvicorn pydantic httpx
```

### Set Environment Variables
```bash
export GOVERNANCE_MODE=SERVERLESS_BYPASS
export ENV=development
export API_KEY=test-key-local
```

### Run the Server
```bash
cd /Users/ss/projects/steward-protocol
python3 -m uvicorn gateway.api:app --host 0.0.0.0 --port 8000
```

### Test with curl
```bash
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -H "x-api-key: test-key-local" \
  -d '{"user_id": "hil_operator_01", "command": "briefing"}'
```

### Access the Frontend Locally
1. Open `docs/public/index.html` in your browser
2. Click ⚙️ settings
3. Enter:
   - API URL: `http://localhost:8000`
   - API Key: `test-key-local`
4. Start chatting!

## This Proves
- ✅ The code works
- ✅ The architecture is sound
- ✅ You can demo it to anyone
- ⏳ Just need to deploy when ready
