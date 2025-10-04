# Terraform Infrastructure for BioNexus
terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "domain_name" {
  description = "Primary domain name"
  type        = string
  default     = "bionexus.space"
}

variable "azure_subscription_id" {
  description = "Azure Subscription ID"
  type        = string
}

# Providers
provider "google" {
  project = var.project_id
  region  = var.region
}

provider "azurerm" {
  subscription_id = var.azure_subscription_id
  features {}
}

# Enable required GCP APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "cloudsql.googleapis.com",
    "storage.googleapis.com",
    "secretmanager.googleapis.com",
    "maps.googleapis.com",
    "bigquery.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "cloudtrace.googleapis.com"
  ])
  
  project = var.project_id
  service = each.value
  
  disable_dependent_services = false
}

# Cloud Storage for documents and media
resource "google_storage_bucket" "bionexus_storage" {
  for_each = toset(["documents", "images", "backups", "analytics"])
  
  name     = "${var.project_id}-bionexus-${each.value}"
  location = var.region
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 365
    }
  }
  
  lifecycle_rule {
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
    condition {
      age = 30
    }
  }
}

# Secret Manager for API keys and credentials
resource "google_secret_manager_secret" "api_keys" {
  for_each = toset([
    "openai-api-key",
    "meteomatics-username", 
    "meteomatics-password",
    "azure-cognitive-key",
    "neo4j-password",
    "neo4j-uri",
    "miro-api-key",
    "miro-client-id",
    "jwt-secret-key",
    "google-maps-api-key",
    "huggingface-api-key",
    "milvus-host",
    "milvus-user",
    "milvus-password"
  ])
  
  secret_id = each.value
  
  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}

# BigQuery dataset for analytics
resource "google_bigquery_dataset" "bionexus_analytics" {
  dataset_id = "bionexus_analytics"
  location   = var.region
  
  description = "BioNexus research analytics and usage metrics"
  
  access {
    role          = "OWNER"
    user_by_email = "admin@${var.domain_name}"
  }
  
  access {
    role         = "READER"
    special_group = "projectReaders"
  }
}

# BigQuery tables for different analytics
resource "google_bigquery_table" "analytics_tables" {
  for_each = {
    "search_events" = {
      description = "User search activity and results"
      schema = jsonencode([
        {
          name = "timestamp"
          type = "TIMESTAMP"
          mode = "REQUIRED"
        },
        {
          name = "user_id"
          type = "STRING"
          mode = "REQUIRED"
        },
        {
          name = "search_query"
          type = "STRING"
          mode = "REQUIRED"
        },
        {
          name = "results_count"
          type = "INTEGER"
          mode = "REQUIRED"
        },
        {
          name = "session_id"
          type = "STRING"
          mode = "REQUIRED"
        },
        {
          name = "research_domain"
          type = "STRING"
          mode = "NULLABLE"
        }
      ])
    }
    
    "user_sessions" = {
      description = "User session tracking and engagement metrics"
      schema = jsonencode([
        {
          name = "session_id"
          type = "STRING"
          mode = "REQUIRED"
        },
        {
          name = "user_id"
          type = "STRING"
          mode = "REQUIRED"
        },
        {
          name = "start_timestamp"
          type = "TIMESTAMP"
          mode = "REQUIRED"
        },
        {
          name = "end_timestamp"
          type = "TIMESTAMP"
          mode = "NULLABLE"
        },
        {
          name = "page_views"
          type = "INTEGER"
          mode = "REQUIRED"
        },
        {
          name = "actions_performed"
          type = "JSON"
          mode = "NULLABLE"
        }
      ])
    }
    
    "research_impact" = {
      description = "Research citation and impact metrics"
      schema = jsonencode([
        {
          name = "publication_id"
          type = "STRING"
          mode = "REQUIRED"
        },
        {
          name = "citation_count"
          type = "INTEGER"
          mode = "REQUIRED"
        },
        {
          name = "impact_score"
          type = "FLOAT"
          mode = "REQUIRED"
        },
        {
          name = "research_domain"
          type = "STRING"
          mode = "REQUIRED"
        },
        {
          name = "timestamp"
          type = "TIMESTAMP"
          mode = "REQUIRED"
        }
      ])
    }
  }
  
  dataset_id = google_bigquery_dataset.bionexus_analytics.dataset_id
  table_id   = each.key
  
  description = each.value.description
  schema      = each.value.schema
  
  time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }
}

# Cloud Run service for backend API
resource "google_cloud_run_service" "bionexus_backend" {
  name     = "bionexus-backend"
  location = var.region
  
  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale"         = "100"
        "autoscaling.knative.dev/minScale"         = "1"
        "run.googleapis.com/execution-environment" = "gen2"
        "run.googleapis.com/cpu-throttling"        = "false"
      }
    }
    
    spec {
      container_concurrency = 80
      timeout_seconds      = 300
      
      containers {
        image = "gcr.io/${var.project_id}/bionexus-backend:latest"
        
        ports {
          name           = "http1"
          container_port = 8000
        }
        
        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }
        
        env {
          name  = "ENVIRONMENT"
          value = "production"
        }
        
        env {
          name = "NEO4J_URI"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.api_keys["neo4j-uri"].secret_id
              key  = "latest"
            }
          }
        }
        
        env {
          name = "NEO4J_PASSWORD"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.api_keys["neo4j-password"].secret_id
              key  = "latest"
            }
          }
        }
        
        env {
          name = "MILVUS_HOST"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.api_keys["milvus-host"].secret_id
              key  = "latest"
            }
          }
        }
        
        env {
          name = "MILVUS_USER"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.api_keys["milvus-user"].secret_id
              key  = "latest"
            }
          }
        }
        
        env {
          name = "MILVUS_PASSWORD"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.api_keys["milvus-password"].secret_id
              key  = "latest"
            }
          }
        }
        
        env {
          name = "GCS_BUCKET_NAME"
          value = google_storage_bucket.bionexus_storage["documents"].name
        }
        
        env {
          name = "GCS_PROJECT_ID"
          value = var.project_id
        }
        
        env {
          name = "OPENAI_API_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.api_keys["openai-api-key"].secret_id
              key  = "latest"
            }
          }
        }
        
        env {
          name = "HUGGINGFACE_API_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.api_keys["huggingface-api-key"].secret_id
              key  = "latest"
            }
          }
        }
        
        resources {
          limits = {
            cpu    = "2000m"
            memory = "4Gi"
          }
        }
        
        startup_probe {
          http_get {
            path = "/health"
            port = 8000
          }
          initial_delay_seconds = 30
          timeout_seconds      = 5
          period_seconds       = 10
          failure_threshold    = 3
        }
        
        liveness_probe {
          http_get {
            path = "/health"
            port = 8000
          }
          initial_delay_seconds = 60
          timeout_seconds      = 5
          period_seconds       = 30
          failure_threshold    = 3
        }
      }
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
  
  depends_on = [google_project_service.apis]
}

# Cloud Run service for frontend
resource "google_cloud_run_service" "bionexus_frontend" {
  name     = "bionexus-frontend"
  location = var.region
  
  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale"         = "50"
        "autoscaling.knative.dev/minScale"         = "1"
        "run.googleapis.com/execution-environment" = "gen2"
      }
    }
    
    spec {
      container_concurrency = 100
      
      containers {
        image = "gcr.io/${var.project_id}/bionexus-frontend:latest"
        
        ports {
          name           = "http1"
          container_port = 3000
        }
        
        env {
          name  = "NEXT_PUBLIC_API_URL"
          value = "https://api.${var.domain_name}"
        }
        
        env {
          name = "NEXT_PUBLIC_MAPS_API_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.api_keys["google-maps-api-key"].secret_id
              key  = "latest"
            }
          }
        }
        
        resources {
          limits = {
            cpu    = "1000m"
            memory = "2Gi"
          }
        }
      }
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
  
  depends_on = [google_project_service.apis]
}

# IAM for public access
resource "google_cloud_run_service_iam_member" "backend_public" {
  service  = google_cloud_run_service.bionexus_backend.name
  location = google_cloud_run_service.bionexus_backend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_service_iam_member" "frontend_public" {
  service  = google_cloud_run_service.bionexus_frontend.name
  location = google_cloud_run_service.bionexus_frontend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Load Balancer for custom domains
resource "google_compute_global_address" "bionexus_ip" {
  name = "bionexus-global-ip"
}

resource "google_compute_managed_ssl_certificate" "bionexus_ssl" {
  name = "bionexus-ssl-cert"
  
  managed {
    domains = [
      var.domain_name,
      "api.${var.domain_name}",
      "app.${var.domain_name}"
    ]
  }
}

# Cloud SQL instance for metadata (complementing Neo4j)
resource "google_sql_database_instance" "bionexus_metadata" {
  name             = "bionexus-metadata-${random_id.db_name_suffix.hex}"
  database_version = "POSTGRES_15"
  region          = var.region
  
  settings {
    tier = "db-f1-micro"
    
    backup_configuration {
      enabled                        = true
      start_time                    = "03:00"
      point_in_time_recovery_enabled = true
      backup_retention_settings {
        retained_backups = 7
      }
    }
    
    ip_configuration {
      ipv4_enabled    = true
      private_network = null
      require_ssl     = true
      
      authorized_networks {
        name  = "all-networks"
        value = "0.0.0.0/0"
      }
    }
    
    maintenance_window {
      day          = 7
      hour         = 3
      update_track = "stable"
    }
  }
  
  deletion_protection = false
}

resource "random_id" "db_name_suffix" {
  byte_length = 4
}

resource "google_sql_database" "bionexus_db" {
  name     = "bionexus"
  instance = google_sql_database_instance.bionexus_metadata.name
}

resource "google_sql_user" "bionexus_user" {
  name     = "bionexus"
  instance = google_sql_database_instance.bionexus_metadata.name
  password = random_password.db_password.result
}

resource "random_password" "db_password" {
  length  = 16
  special = true
}

# Store database credentials in Secret Manager
resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.api_keys["neo4j-password"].id
  secret_data = random_password.db_password.result
}

# Monitoring and Alerting
resource "google_monitoring_uptime_check_config" "bionexus_uptime" {
  display_name = "BioNexus Uptime Check"
  timeout      = "10s"
  period       = "60s"
  
  http_check {
    path         = "/health"
    port         = "443"
    use_ssl      = true
    validate_ssl = true
  }
  
  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = "api.${var.domain_name}"
    }
  }
}

# Alert policy for high error rates
resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "High Error Rate Alert"
  combiner     = "OR"
  
  conditions {
    display_name = "Error rate above threshold"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = "0.05"  # 5% error rate
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }
  
  notification_channels = []  # Add notification channels as needed
}

# Azure Resource Group for AI services
resource "azurerm_resource_group" "bionexus_ai" {
  name     = "bionexus-ai-services"
  location = "East US"
}

# Azure Cognitive Services
resource "azurerm_cognitive_account" "text_analytics" {
  name                = "bionexus-text-analytics"
  location            = azurerm_resource_group.bionexus_ai.location
  resource_group_name = azurerm_resource_group.bionexus_ai.name
  kind                = "TextAnalytics"
  sku_name           = "S"
}

resource "azurerm_cognitive_account" "computer_vision" {
  name                = "bionexus-computer-vision"
  location            = azurerm_resource_group.bionexus_ai.location
  resource_group_name = azurerm_resource_group.bionexus_ai.name
  kind                = "ComputerVision"
  sku_name           = "S1"
}

# Store Azure keys in GCP Secret Manager
resource "google_secret_manager_secret_version" "azure_text_key" {
  secret      = google_secret_manager_secret.api_keys["azure-cognitive-key"].id
  secret_data = azurerm_cognitive_account.text_analytics.primary_access_key
}

# Outputs
output "frontend_url" {
  value = google_cloud_run_service.bionexus_frontend.status[0].url
}

output "backend_url" {
  value = google_cloud_run_service.bionexus_backend.status[0].url
}

output "global_ip" {
  value = google_compute_global_address.bionexus_ip.address
}

output "storage_buckets" {
  value = {
    for k, v in google_storage_bucket.bionexus_storage :
    k => v.url
  }
}

output "bigquery_dataset" {
  value = google_bigquery_dataset.bionexus_analytics.dataset_id
}

output "database_connection" {
  value = google_sql_database_instance.bionexus_metadata.connection_name
  sensitive = true
}

output "azure_text_analytics_endpoint" {
  value = azurerm_cognitive_account.text_analytics.endpoint
}

output "azure_computer_vision_endpoint" {
  value = azurerm_cognitive_account.computer_vision.endpoint
}