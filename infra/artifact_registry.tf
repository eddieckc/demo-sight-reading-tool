resource "google_artifact_registry_repository" "repo" {
  location      = var.region
  repository_id = var.repository_name
  description   = "Docker container repository for AI Sight-Reading Tool backend and frontend services."
  format        = "DOCKER"

  depends_on = [google_project_service.enabled_apis]
}
