variable "location" {
  type        = string
  description = "Azure region for all resources."
  default     = "Central India"
}

variable "project_name" {
  type        = string
  description = "Short lowercase name used in Azure resources."
  default     = "smartcityenv"
}

variable "environment" {
  type        = string
  description = "Environment tag."
  default     = "capstone"
}

variable "aks_node_vm_size" {
  type        = string
  description = "Single AKS node size for the capstone deployment."
  default     = "Standard_B2s_v2"
}

variable "postgres_sku_name" {
  type        = string
  description = "Burstable PostgreSQL Flexible Server SKU."
  default     = "B_Standard_B1ms"
}

variable "postgres_admin_login" {
  type        = string
  description = "PostgreSQL administrator login."
  default     = "smartadmin"
}

variable "postgres_admin_password" {
  type        = string
  description = "Strong PostgreSQL password."
  sensitive   = true
}

variable "rabbitmq_user" {
  type        = string
  description = "RabbitMQ application user."
  default     = "smartcity"
}

variable "rabbitmq_password" {
  type        = string
  description = "Strong RabbitMQ password."
  sensitive   = true
}

variable "enable_monitoring" {
  type        = bool
  description = "Enable Log Analytics and Application Insights. Disable for the lowest-cost demo."
  default     = false
}
