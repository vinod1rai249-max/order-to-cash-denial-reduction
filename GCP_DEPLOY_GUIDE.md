# --- GCP CLOUD RUN DEPLOYMENT GUIDE ---

## 1. Build and Push Images to Artifact Registry

Run these commands in your local terminal (ensure you are authenticated with gcloud):

```bash
# Variables
PROJECT_ID="adpo-healthcare-agent"
REGION="us-central1"
REPO_NAME="order-to-cash-repo"

# 1. Create Repository (Run once)
gcloud artifacts repositories create $REPO_NAME --repository-format=docker --location=$REGION

# 2. Build Backend
gcloud builds submit --tag $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/backend:latest -f Dockerfile.backend .

# 3. Build Frontend
gcloud builds submit --tag $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/frontend:latest -f Dockerfile.frontend .
```

## 2. Deploy to Cloud Run

### Deploy Backend
```bash
gcloud run deploy otc-backend \
  --image $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/backend:latest \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars="GCP_PROJECT_ID=$PROJECT_ID,BQ_DATASET=billing_analytics,BQ_TABLE=governance_sink"
```

### Deploy Frontend
**Note:** Once the backend is deployed, you will get a URL (e.g., `https://otc-backend-xxxx.a.run.app`). Update the `API_URL` in your Streamlit code or set it via environment variable.

```bash
gcloud run deploy otc-frontend \
  --image $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/frontend:latest \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --port 8081
```

## 3. Local Multi-Container Test (Optional)
If you have Docker Desktop installed, you can use this `docker-compose.yml`:

```yaml
version: '3.8'
services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8080"
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "8501:8081"
    environment:
      - API_URL=http://backend:8080
```
