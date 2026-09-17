variable "region" {
  type    = string
  default = "us-east-1"
}

variable "name_prefix" {
  type    = string
  default = "context-skills"
}

variable "auth_mode" {
  type    = string
  default = "enforced"
}

variable "vpc_cidr" {
  type    = string
  default = "10.20.0.0/16"
}

variable "db_password" {
  type      = string
  sensitive = true
  default   = "change-me-in-production"
}

variable "tenant_namespaces" {
  type        = list(string)
  description = "Optional per-tenant Kubernetes namespaces"
  default     = ["tenant-a", "tenant-b", "tenant-c"]
}

variable "tags" {
  type    = map(string)
  default = { project = "context-skills", mode = "saas" }
}
