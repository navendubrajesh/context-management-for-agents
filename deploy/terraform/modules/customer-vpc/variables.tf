variable "region" {
  type        = string
  description = "Pinned AWS region for data residency"
}

variable "customer_id" {
  type        = string
  description = "Single-tenant customer identifier"
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
  default = "10.30.0.0/16"
}

variable "db_password" {
  type      = string
  sensitive = true
  default   = "change-me-in-production"
}

variable "allowed_ingress_cidrs" {
  type        = list(string)
  description = "Restrict API ingress to customer corporate CIDRs"
  default     = []
}

variable "tags" {
  type    = map(string)
  default = { project = "context-skills", mode = "customer-vpc" }
}
