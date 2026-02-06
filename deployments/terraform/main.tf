terraform {
  required_version = ">= 1.5.0"
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.29"
    }
  }
}

provider "kubernetes" {
  config_path = var.kubeconfig_path
}

variable "kubeconfig_path" {
  type        = string
  description = "Path to kubeconfig"
  default     = "~/.kube/config"
}

variable "namespace" {
  type        = string
  description = "Kubernetes namespace"
  default     = "telemetry"
}

resource "kubernetes_namespace" "telemetry" {
  metadata {
    name = var.namespace
  }
}

resource "kubernetes_config_map" "telemetry_config" {
  metadata {
    name      = "telemetry-config"
    namespace = kubernetes_namespace.telemetry.metadata[0].name
  }

  data = {
    databricks-catalog = "main"
    databricks-schema  = "predictive_marts"
  }
}

output "namespace" {
  value = kubernetes_namespace.telemetry.metadata[0].name
}
