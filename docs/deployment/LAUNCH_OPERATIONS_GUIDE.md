# Launch Operations Guide: Agentic World Deployment

This guide walks you through the **manual configuration steps** required to deploy the Agentic World to production.

## Prerequisites
- Google Cloud Account (Free tier is sufficient)
- GitHub Repository with admin access
- The code is already pushed to `main` branch

---

## PHASE 1: Google Cloud Setup

### Step 1.1: Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a project** → **New Project**
3. Name it (e.g., `agentic-world`)
4. Note the **Project ID** (e.g., `agentic-world-123456`)

### Step 1.2: Enable Required APIs
```bash
# Run in Cloud Shell or local terminal with gcloud CLI
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### Step 1.3: Create Service Account
1. Go to **IAM & Admin** → **Service Accounts**
2. Click **Create Service Account**
3. Name: `github-deployer`
4. Click **Create and Continue**
5. Grant these roles:
   - `Cloud Run Admin`
   - `Storage Admin`
   - `Service Account User`
6. Click **Done**

### Step 1.4: Generate JSON Key
1. Click on the newly created service account
2. Go to **Keys** tab
3. Click **Add Key** → **Create new key**
4. Choose **JSON**
5. Download the file (keep it safe!)

---

## PHASE 2: GitHub Secrets Configuration

### Step 2.1: Navigate to Secrets
1. Go to your GitHub repo: `https://github.com/kimeisele/steward-protocol`
2. Click **Settings** → **Secrets and variables** → **Actions**

### Step 2.2: Add Repository Secrets
Click **New repository secret** for each:

#### Secret 1: `GCP_PROJECT_ID`
- **Name**: `GCP_PROJECT_ID`
- **Value**: Your project ID from Step 1.1 (e.g., `agentic-world-123456`)

#### Secret 2: `GCP_SA_KEY`
- **Name**: `GCP_SA_KEY`
- **Value**: Open the JSON file from Step 1.4, copy **the entire content**, paste it here

#### Secret 3: `API_KEY`
- **Name**: `API_KEY`
- **Value**: Generate a strong key (e.g., `steward-protocol-2025-$(openssl rand -hex 16)`)
- **IMPORTANT**: Save this key somewhere safe! You'll need it to access the API.

---

## PHASE 3: GitHub Pages Setup

### Step 3.1: Enable Pages
1. Go to **Settings** → **Pages**
2. Under **Source**, select:
   - Branch: `main`
   - Folder: `/docs`
3. Click **Save**
4. Note the URL (e.g., `https://kimeisele.github.io/steward-protocol/`)

---

## PHASE 4: Trigger Deployment

### Step 4.1: Manual Workflow Trigger
1. Go to **Actions** tab in GitHub
2. Click on **Deploy to Cloud Run** workflow
3. Click **Run workflow** → **Run workflow**
4. Wait 2-3 minutes for the build to complete

### Step 4.2: Verify Deployment
Once the workflow is green:
1. Go to [Cloud Run Console](https://console.cloud.google.com/run)
2. You should see `steward-gateway` service
3. Click on it and note the **URL** (e.g., `https://steward-gateway-xxx-uc.a.run.app`)

---

## PHASE 5: Connect Frontend to Backend

### Step 5.1: Configure the Frontend
1. Go to your GitHub Pages URL (from Phase 3)
2. Click the **⚙️** icon in the top-right
3. Enter:
   - **API URL**: Your Cloud Run URL from Step 4.2
   - **API Key**: The `API_KEY` you created in Step 2.2
4. Click **Save**

### Step 5.2: Test the Connection
1. Type a command in the chat (e.g., `briefing`)
2. You should receive a response from the HIL Assistant

---

## Troubleshooting

### Workflow Fails with "Permission Denied"
- Check that the Service Account has the correct roles (Step 1.3)
- Verify `GCP_SA_KEY` is the complete JSON (including `{` and `}`)

### Cloud Run Service Won't Start
- Check logs in Cloud Run Console
- Verify `API_KEY` secret is set correctly
- Ensure `GOVERNANCE_MODE=SERVERLESS_BYPASS` is in the workflow

### Frontend Shows "Connection Error"
- Verify the Cloud Run URL is correct (no trailing slash)
- Check that the service is **publicly accessible** (Cloud Run → Permissions → Allow unauthenticated)
- Open browser console (F12) to see detailed error messages

### "Invalid API Key" Error
- Ensure the API Key in the frontend matches the one in GitHub Secrets
- Check for extra spaces or newlines when copying

---

## Security Checklist

- [ ] Service Account JSON key is stored **only** in GitHub Secrets (not on your laptop)
- [ ] `API_KEY` is strong and unique (not "steward-secret-key")
- [ ] Cloud Run service has proper IAM permissions (not fully public if not needed)
- [ ] GitHub Secrets are set to **Repository** level (not Environment)

---

## Success Criteria

✅ GitHub Actions workflow is **green**
✅ Cloud Run service is **running**
✅ GitHub Pages site is **live**
✅ Frontend can **connect** to backend
✅ You can **chat** with the Agentic World

**You have successfully deployed the Agentic World.** 🌍
