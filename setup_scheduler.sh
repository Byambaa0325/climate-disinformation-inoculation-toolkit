#!/usr/bin/env bash
# One-time setup: Cloud Run Job + Cloud Scheduler for daily news scraping.
# Run this after `gcloud auth login` and `gcloud config set project PROJECT_ID`.
#
# Usage: bash setup_scheduler.sh my-project-id [region]
set -euo pipefail

PROJECT_ID="${1:?Usage: $0 PROJECT_ID [REGION]}"
REGION="${2:-us-central1}"
BUCKET="${PROJECT_ID}-climate-disinfo-data"
SA_NAME="climate-disinfo-scraper"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
JOB_NAME="climate-disinfo-scraper"
SCHEDULER_JOB="climate-disinfo-scraper-daily"
IMAGE="gcr.io/${PROJECT_ID}/climate-disinfo-scraper"

echo "=== Project: ${PROJECT_ID}  Region: ${REGION} ==="

# 1. Enable required APIs
gcloud services enable \
  run.googleapis.com \
  cloudscheduler.googleapis.com \
  cloudbuild.googleapis.com \
  storage.googleapis.com \
  --project="${PROJECT_ID}"

# 2. GCS bucket (ignore error if already exists)
gsutil mb -p "${PROJECT_ID}" -l "${REGION}" "gs://${BUCKET}" 2>/dev/null || \
  echo "  Bucket gs://${BUCKET} already exists."

# 3. Service account for the scraper
gcloud iam service-accounts create "${SA_NAME}" \
  --display-name="Climate Disinfo Scraper" \
  --project="${PROJECT_ID}" 2>/dev/null || \
  echo "  Service account ${SA_EMAIL} already exists."

# Grant it GCS write on the bucket
gsutil iam ch "serviceAccount:${SA_EMAIL}:roles/storage.objectAdmin" "gs://${BUCKET}"

# 4. Build & push the scraper image
gcloud builds submit \
  --config cloudbuild.scraper.yaml \
  --project="${PROJECT_ID}"

# 5. Create (or update) the Cloud Run Job
gcloud run jobs create "${JOB_NAME}" \
  --image="${IMAGE}" \
  --region="${REGION}" \
  --service-account="${SA_EMAIL}" \
  --set-env-vars="GCS_BUCKET=${BUCKET},GCS_OBJECT=news_headlines.json" \
  --max-retries=2 \
  --task-timeout=5m \
  --project="${PROJECT_ID}" 2>/dev/null || \
gcloud run jobs update "${JOB_NAME}" \
  --image="${IMAGE}" \
  --region="${REGION}" \
  --service-account="${SA_EMAIL}" \
  --set-env-vars="GCS_BUCKET=${BUCKET},GCS_OBJECT=news_headlines.json" \
  --project="${PROJECT_ID}"

# 6. Cloud Scheduler — invoke the job daily at 06:00 UTC
# Scheduler needs a dedicated SA to invoke Cloud Run Jobs
SCHEDULER_SA="cloudscheduler-invoker"
SCHEDULER_SA_EMAIL="${SCHEDULER_SA}@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud iam service-accounts create "${SCHEDULER_SA}" \
  --display-name="Cloud Scheduler → Cloud Run Jobs invoker" \
  --project="${PROJECT_ID}" 2>/dev/null || \
  echo "  Scheduler SA already exists."

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SCHEDULER_SA_EMAIL}" \
  --role="roles/run.invoker"

JOB_URI="https://${REGION}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT_ID}/jobs/${JOB_NAME}:run"

gcloud scheduler jobs create http "${SCHEDULER_JOB}" \
  --location="${REGION}" \
  --schedule="0 6 * * *" \
  --uri="${JOB_URI}" \
  --http-method=POST \
  --oauth-service-account-email="${SCHEDULER_SA_EMAIL}" \
  --project="${PROJECT_ID}" 2>/dev/null || \
gcloud scheduler jobs update http "${SCHEDULER_JOB}" \
  --location="${REGION}" \
  --schedule="0 6 * * *" \
  --uri="${JOB_URI}" \
  --http-method=POST \
  --oauth-service-account-email="${SCHEDULER_SA_EMAIL}" \
  --project="${PROJECT_ID}"

echo ""
echo "=== Done! ==="
echo "  GCS bucket:    gs://${BUCKET}"
echo "  Cloud Run Job: ${JOB_NAME} (${REGION})"
echo "  Scheduler:     ${SCHEDULER_JOB} → daily at 06:00 UTC"
echo ""
echo "To update the main backend to read from GCS, redeploy with:"
echo "  gcloud run services update climate-disinfo \\"
echo "    --update-env-vars=GCS_BUCKET=${BUCKET} \\"
echo "    --region=${REGION}"
echo ""
echo "To run the scraper immediately:"
echo "  gcloud run jobs execute ${JOB_NAME} --region=${REGION}"
