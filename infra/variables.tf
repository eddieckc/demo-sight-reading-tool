variable "project_id" {
  type        = string
  description = "The GCP project ID where resources will be deployed."
}

variable "region" {
  type        = string
  description = "The GCP region for Cloud Run and Artifact Registry."
  default     = "us-central1"
}

variable "backend_service_name" {
  type        = string
  description = "The name of the Cloud Run backend service."
  default     = "ai-sight-reader-backend"
}

variable "frontend_service_name" {
  type        = string
  description = "The name of the Cloud Run frontend service."
  default     = "ai-sight-reader-frontend"
}

variable "gemini_model" {
  type        = string
  description = "The Vertex AI Gemini model to invoke."
  default     = "gemini-2.5-flash"
}

variable "repository_name" {
  type        = string
  description = "The Artifact Registry Docker repository name."
  default     = "ai-sight-reader-repo"
}
