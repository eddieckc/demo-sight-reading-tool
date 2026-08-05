output "backend_url" {
  description = "The HTTPS URL of the deployed Cloud Run Backend service."
  value       = google_cloud_run_v2_service.backend.uri
}

output "frontend_url" {
  description = "The HTTPS URL of the deployed Cloud Run Frontend application."
  value       = google_cloud_run_v2_service.frontend.uri
}

output "backend_service_account_email" {
  description = "The IAM Service Account email used by the Backend for Vertex AI Gemini access."
  value       = google_service_account.backend_sa.email
}

output "artifact_registry_repo" {
  description = "The Artifact Registry repository URI for Docker images."
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_name}"
}
