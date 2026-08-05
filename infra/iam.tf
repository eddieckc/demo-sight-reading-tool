# Dedicated Service Account for Cloud Run Backend
resource "google_service_account" "backend_sa" {
  account_id   = "ai-sight-reader-backend-sa"
  display_name = "AI Sight Reader Backend Service Account (Vertex AI Gemini Auth)"
  description  = "Service Account used by Cloud Run Backend to call Gemini on Vertex AI without API keys."
  depends_on   = [google_project_service.enabled_apis]
}

# Grant Vertex AI User role to the Backend Service Account
resource "google_project_iam_member" "backend_vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.backend_sa.email}"
}

# Allow public invocation of Frontend Cloud Run service
resource "google_cloud_run_v2_service_iam_member" "frontend_invoker" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.frontend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Allow public invocation of Backend Cloud Run service (protected by CORS / token if desired)
resource "google_cloud_run_v2_service_iam_member" "backend_invoker" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.backend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
